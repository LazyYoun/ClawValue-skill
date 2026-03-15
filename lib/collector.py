#!/usr/bin/env python3
"""
ClawValue 数据采集模块

负责从 OpenClaw 系统采集各类数据：
- 日志解析：解析 /tmp/openclaw/ 目录下的 JSONL 日志
- 技能扫描：扫描 ~/.openclaw/workspace/skills/ 目录
- 配置分析：解析 ~/.openclaw/openclaw.json 配置文件
- Token 统计：从会话日志中提取模型使用情况

设计原则：
- 使用常量定义字段名，避免硬编码字符串
- 结构化数据模型，提供类型安全
- 模块化设计，每个采集器独立可测试
- 详细注释，便于维护

参考文档：docs/OPENCLAW_REFERENCE.md
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime

# 使用条件导入支持包内和直接运行
try:
    from .constants import (
        LOG_DIR, OPENCLAW_HOME, OPENCLAW_CONFIG_FILE,
        SESSIONS_DIR_NEW, SESSIONS_DIR_OLD, BACKUPS_DIR,
        SKILLS_DIR, SKILL_FILE, CRON_CONFIG_FILE,
        MAX_SCAN_DEPTH, MAX_FILE_SIZE_MB, MAX_FILES_PER_DIR, SKIP_DIRS,
        LogField, LogLevel, LogType,
        SkillCategory
    )
    from .schemas import (
        LogEntry, LogStats, Skill, OpenClawConfig,
        CollectionData
    )
except ImportError:
    from constants import (
        LOG_DIR, OPENCLAW_HOME, OPENCLAW_CONFIG_FILE,
        SESSIONS_DIR_NEW, SESSIONS_DIR_OLD, BACKUPS_DIR,
        SKILLS_DIR, SKILL_FILE, CRON_CONFIG_FILE,
        MAX_SCAN_DEPTH, MAX_FILE_SIZE_MB, MAX_FILES_PER_DIR, SKIP_DIRS,
        LogField, LogLevel, LogType,
        SkillCategory
    )
    from schemas import (
        LogEntry, LogStats, Skill, OpenClawConfig,
        CollectionData
    )


# =============================================================================
# 日志解析器
# =============================================================================

class LogParser:
    """
    OpenClaw 日志解析器
    
    负责解析多个目录下的 JSONL 日志文件，支持新旧版本 OpenClaw。
    
    扫描位置：
    - /tmp/openclaw/ (官方日志目录)
    - ~/.openclaw/agents/main/sessions/ (新版本会话日志)
    - ~/.openclaw/sessions/ (老版本会话日志)
    - ~/.openclaw/backups/ (历史备份，可选)
    
    日志格式参考：
    - 文件位置：/tmp/openclaw/openclaw-YYYY-MM-DD.log
    - 格式：每行一个 JSON 对象
    - 文档：https://docs.openclaw.ai/zh-CN/logging
    
    Example:
        >>> parser = LogParser()
        >>> logs = parser.get_all_logs()
        >>> stats = parser.extract_stats(logs)
        >>> print(f"Total logs: {stats.total_entries}")
    """
    
    def __init__(self, log_dir: str = None, openclaw_home: str = None):
        """
        初始化日志解析器
        
        Args:
            log_dir: 日志目录路径，默认使用官方定义的 /tmp/openclaw
            openclaw_home: OpenClaw 主目录，用于查找会话日志
        """
        self.log_dir = log_dir or LOG_DIR
        self.openclaw_home = openclaw_home or str(Path.home() / '.openclaw')
        
        # 构建所有需要扫描的目录列表
        self.scan_dirs = self._build_scan_dirs()
        
        # Token 统计（按模型分类）
        self.token_stats: Dict[str, Dict[str, Any]] = {}
    
    def _build_scan_dirs(self) -> List[str]:
        """
        构建需要扫描的所有目录列表
        
        Returns:
            目录路径列表
        """
        dirs = []
        
        # 1. 官方日志目录
        if self.log_dir and isinstance(self.log_dir, str):
            dirs.append(self.log_dir)
        
        # 2. 新版本会话日志目录
        if self.openclaw_home and isinstance(self.openclaw_home, str):
            new_sessions = os.path.join(self.openclaw_home, SESSIONS_DIR_NEW)
            dirs.append(new_sessions)
            
            # 3. 老版本会话日志目录
            old_sessions = os.path.join(self.openclaw_home, SESSIONS_DIR_OLD)
            dirs.append(old_sessions)
            
            # 4. 历史备份目录（可选）
            backups = os.path.join(self.openclaw_home, BACKUPS_DIR)
            dirs.append(backups)
        
        return dirs
    
    def parse_jsonl_file(self, filepath: str) -> List[LogEntry]:
        """
        解析单个 JSONL 日志文件（传统格式）
        
        传统格式示例：
        {
            "0": "[tools] read failed: ...",
            "_meta": {"logLevelName": "ERROR", ...},
            "time": "2026-03-13T01:00:04.080+08:00"
        }
        
        优化：同时从传统日志中提取 token 使用信息
        
        Args:
            filepath: 日志文件路径
            
        Returns:
            LogEntry 列表
        """
        entries = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        data = json.loads(line)
                        entry = LogEntry.from_openclaw_json(data)
                        entries.append(entry)
                        
                        # 从传统日志中提取 token 信息（如果存在）
                        self._extract_token_from_traditional_log(data)
                        
                    except json.JSONDecodeError:
                        # 跳过无法解析的行
                        if line_num <= 5:  # 只记录前 5 个解析错误
                            print(f"[LogParser] 解析行 {line_num} 失败：{line[:100]}")
                        continue
        except FileNotFoundError:
            pass
        except UnicodeDecodeError as e:
            print(f"[LogParser] 文件编码错误 {filepath}: {e}")
        except Exception as e:
            print(f"[LogParser] 解析文件 {filepath} 时出错：{e}")
        
        return entries
    
    def _extract_token_from_traditional_log(self, data: Dict[str, Any]) -> None:
        """
        从传统日志格式中提取 token 使用信息
        
        传统日志中可能包含模型调用信息，尝试从中提取 token 统计
        
        Args:
            data: 日志 JSON 数据
        """
        message = data.get('0', '') or data.get('message', '')
        if not isinstance(message, str):
            return
        
        # 匹配模型调用信息
        import re
        
        # 匹配模型名称
        model_match = re.search(r'model[:\s]+([a-zA-Z0-9._-]+)', message, re.IGNORECASE)
        if not model_match:
            # 尝试从 raw_data 中查找
            meta = data.get('_meta', {})
            if isinstance(meta, dict):
                path = meta.get('path', {})
                if isinstance(path, dict):
                    file_name = path.get('fileName', '')
                    if 'qwen' in file_name.lower():
                        model_match = type('obj', (object,), {'group': lambda x: 'qwen3.5-plus'})()
        
        if model_match:
            model = model_match.group(1) if hasattr(model_match, 'group') else 'qwen3.5-plus'
            
            # 匹配 token 数量
            token_match = re.search(r'(\d+(?:,\d+)*)\s*tokens?', message, re.IGNORECASE)
            if token_match:
                tokens_str = token_match.group(1).replace(',', '')
                total_tokens = int(tokens_str)
                
                # 估算输入/输出比例（通常输出占 30-40%）
                input_tokens = int(total_tokens * 0.65)
                output_tokens = total_tokens - input_tokens
                
                # 估算成本（按 qwen3.5-plus 价格：输入 0.002 元/1K，输出 0.006 元/1K）
                cost = (input_tokens / 1000 * 0.002) + (output_tokens / 1000 * 0.006)
                
                # 更新统计
                if model not in self.token_stats:
                    self.token_stats[model] = {
                        'input_tokens': 0,
                        'output_tokens': 0,
                        'total_tokens': 0,
                        'cost': 0.0,
                        'call_count': 0
                    }
                
                stats = self.token_stats[model]
                stats['input_tokens'] += input_tokens
                stats['output_tokens'] += output_tokens
                stats['total_tokens'] += total_tokens
                stats['cost'] += cost
                stats['call_count'] += 1
    
    def parse_session_jsonl(self, filepath: str) -> List[LogEntry]:
        """
        解析新版本会话日志文件（type-based 格式）
        
        新版本格式示例：
        {"type":"message","message":{"role":"assistant",..., "usage":{...}}}
        
        Args:
            filepath: 会话日志文件路径
            
        Returns:
            LogEntry 列表
        """
        entries = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        data = json.loads(line)
                        # 转换新版本格式为 LogEntry
                        entry = self._convert_session_event_to_entry(data)
                        if entry:
                            entries.append(entry)
                    except json.JSONDecodeError:
                        continue
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"[LogParser] 解析会话文件 {filepath} 时出错：{e}")
        
        return entries
    
    def _convert_session_event_to_entry(self, data: Dict[str, Any]) -> Optional[LogEntry]:
        """
        将新版本会话事件转换为 LogEntry
        
        Args:
            data: 会话事件 JSON 数据
            
        Returns:
            LogEntry 对象或 None
        """
        event_type = data.get('type', '')
        timestamp = data.get('timestamp', '')
        
        # 处理不同类型的会话事件
        if event_type == 'message':
            message_data = data.get('message', {})
            role = message_data.get('role', '')
            content = message_data.get('content', '')
            usage = message_data.get('usage', {})
            
            # 提取 usage 信息
            if usage and role == 'assistant':
                self._extract_token_usage(usage, message_data.get('model', 'unknown'))
            
            # 构建消息文本
            msg_text = f"[session:{data.get('id', '')}] {role}: {str(content)[:200]}"
            
            return LogEntry(
                message=msg_text,
                level=LogLevel.INFO,
                timestamp=timestamp,
                subsystem='session',
                log_type=LogType.SESSION if role else LogType.OTHER,
                raw_data=data
            )
        
        elif event_type == 'tool_call':
            tool_name = data.get('toolName', 'unknown')
            return LogEntry(
                message=f"[tools] {tool_name} called",
                level=LogLevel.INFO,
                timestamp=timestamp,
                subsystem='tools',
                log_type=LogType.TOOL,
                raw_data=data
            )
        
        elif event_type == 'model_change':
            model = data.get('modelId', 'unknown')
            return LogEntry(
                message=f"[model] Changed to {model}",
                level=LogLevel.INFO,
                timestamp=timestamp,
                subsystem='model',
                log_type=LogType.MODEL,
                raw_data=data
            )
        
        return None
    
    def _extract_token_usage(self, usage: Dict[str, Any], model: str) -> None:
        """
        从 usage 对象中提取 token 统计信息
        
        支持多种 usage 格式：
        - OpenAI 格式：{prompt_tokens, completion_tokens, total_tokens}
        - DashScope 格式：{input, output, totalTokens, cost}
        - 简化格式：{input_tokens, output_tokens, total_tokens}
        
        Args:
            usage: usage 字典 {input, output, totalTokens, cost, ...}
            model: 模型名称
        """
        if not model:
            model = 'unknown'
        
        # 规范化模型名称
        model = self._normalize_model_name(model)
        
        if model not in self.token_stats:
            self.token_stats[model] = {
                'input_tokens': 0,
                'output_tokens': 0,
                'total_tokens': 0,
                'cost': 0.0,
                'call_count': 0
            }
        
        stats = self.token_stats[model]
        
        # 提取各项指标（支持多种格式）
        input_tokens = (
            usage.get('input', 0) or 
            usage.get('prompt_tokens', 0) or 
            usage.get('input_tokens', 0) or 
            0
        )
        output_tokens = (
            usage.get('output', 0) or 
            usage.get('completion_tokens', 0) or 
            usage.get('output_tokens', 0) or 
            0
        )
        total_tokens = (
            usage.get('totalTokens', 0) or 
            usage.get('total_tokens', 0) or 
            (input_tokens + output_tokens)
        )
        
        # 提取成本（支持多种格式）
        cost = self._extract_cost_from_usage(usage)
        
        # 累加统计
        stats['input_tokens'] += int(input_tokens)
        stats['output_tokens'] += int(output_tokens)
        stats['total_tokens'] += int(total_tokens)
        stats['cost'] += float(cost)
        stats['call_count'] += 1
    
    def _normalize_model_name(self, model: str) -> str:
        """
        规范化模型名称
        
        处理常见的模型名称变体，统一命名
        
        Args:
            model: 原始模型名称
            
        Returns:
            规范化后的模型名称
        """
        if not model:
            return 'unknown'
        
        model_lower = model.lower()
        
        # 常见模型名称映射
        model_mapping = {
            'qwen3.5-plus': 'qwen3.5-plus',
            'qwen3.5': 'qwen3.5-plus',
            'qwen-plus': 'qwen3.5-plus',
            'glm-5': 'glm-5',
            'glm5': 'glm-5',
            'minimax-m2.5': 'minimax-m2.5',
            'minimax-m2': 'minimax-m2.5',
            'gateway-injected': 'gateway-injected',
        }
        
        # 查找匹配
        for key, normalized in model_mapping.items():
            if key in model_lower:
                return normalized
        
        # 返回原始名称（去除版本号的变体）
        return model.strip()
    
    def _extract_cost_from_usage(self, usage: Dict[str, Any]) -> float:
        """
        从 usage 中提取成本信息
        
        支持多种成本格式：
        - 直接数值：usage['cost'] = 0.001
        - 字典格式：usage['cost'] = {'total': 0.001, 'input': 0.0005, 'output': 0.0005}
        - 嵌套格式：usage['cost']['total']
        - DashScope 格式：usage['total_cost'] 或 usage['charge']
        
        Args:
            usage: usage 字典
            
        Returns:
            成本值（元）
        """
        # 1. 直接成本字段
        cost_data = usage.get('cost', {})
        
        if isinstance(cost_data, (int, float)):
            return float(cost_data)
        
        if isinstance(cost_data, dict):
            # 尝试多种字段名
            cost = (
                cost_data.get('total', 0.0) or
                cost_data.get('totalCost', 0.0) or
                cost_data.get('amount', 0.0) or
                0.0
            )
            if cost > 0:
                return float(cost)
        
        # 2. DashScope 格式：total_cost 或 charge
        total_cost = usage.get('total_cost', 0.0) or usage.get('charge', 0.0)
        if isinstance(total_cost, (int, float)) and total_cost > 0:
            return float(total_cost)
        
        # 3. 如果没有成本信息，根据 token 数估算（按模型差异化定价）
        input_tokens = usage.get('input', 0) or usage.get('prompt_tokens', 0) or 0
        output_tokens = usage.get('output', 0) or usage.get('completion_tokens', 0) or 0
        
        if input_tokens == 0 and output_tokens == 0:
            return 0.0
        
        # 按模型定价（元/1K tokens）
        # qwen3.5-plus: 输入 0.002, 输出 0.006
        # minimax-m2.5: 输入 0.001, 输出 0.001
        # glm-5: 输入 0.001, 输出 0.001
        # 默认：输入 0.002, 输出 0.006
        input_price = 0.002
        output_price = 0.006
        
        estimated_cost = (input_tokens / 1000 * input_price) + (output_tokens / 1000 * output_price)
        return round(estimated_cost, 4)
    
    def get_all_logs(self) -> List[LogEntry]:
        """
        获取所有日志条目
        
        扫描所有配置的目录下匹配 *.log 和 *.jsonl 的文件并解析。
        支持新旧版本 OpenClaw 的日志格式。
        
        Returns:
            所有日志条目的列表
        """
        all_entries = []
        
        for scan_dir in self.scan_dirs:
            # 验证路径类型
            if not isinstance(scan_dir, str):
                print(f"[LogParser] 跳过非字符串路径：{type(scan_dir)}")
                continue
            
            if not os.path.exists(scan_dir):
                # Graceful fallback: 目录不存在时不报错，仅记录日志
                print(f"[LogParser] 目录不存在，跳过：{scan_dir}")
                continue
            
            try:
                entries = self._scan_directory(scan_dir)
                all_entries.extend(entries)
                if entries:
                    print(f"[LogParser] 从 {scan_dir} 扫描到 {len(entries)} 条日志")
            except Exception as e:
                # 捕获异常，避免单个目录问题影响整体扫描
                print(f"[LogParser] 扫描目录 {scan_dir} 时出错：{e}")
        
        return all_entries
    
    def _scan_directory(self, directory: str) -> List[LogEntry]:
        """
        扫描单个目录下的所有日志文件
        
        优化点：
        - 智能识别日志类型（传统日志 vs 会话日志）
        - 跳过无关目录（node_modules, .git, __pycache__等）
        - 限制扫描深度和文件大小
        - 支持多种日志格式（.log, .jsonl）
        - 详细日志输出，便于调试
        
        Args:
            directory: 目录路径
            
        Returns:
            日志条目列表
        """
        entries = []
        
        # 验证目录是否存在且是字符串路径
        if not directory or not isinstance(directory, str):
            print(f"[LogParser] 跳过无效目录：{directory} (类型：{type(directory)})")
            return entries
        
        if not os.path.exists(directory):
            print(f"[LogParser] 目录不存在，跳过：{directory}")
            return entries
        
        if not os.path.isdir(directory):
            print(f"[LogParser] 不是目录，跳过：{directory}")
            return entries
        
        print(f"[LogParser] 开始扫描目录：{directory}")
        
        # 跳过目录名称判断
        skip_dirs = {'node_modules', '.git', '__pycache__', '.venv', 'venv', '.pytest_cache', '.mypy_cache', '.DS_Store'}
        
        total_files = 0
        scanned_files = 0
        skipped_files = 0
        
        try:
            for root, dirs, files in os.walk(directory):
                # 确保 root 是字符串
                if not isinstance(root, str):
                    continue
                
                # 原地修改 dirs 列表，跳过无关子目录
                skipped_subdirs = [d for d in dirs if d in skip_dirs]
                dirs[:] = [d for d in dirs if d not in skip_dirs]
                if skipped_subdirs:
                    print(f"[LogParser] 跳过子目录：{skipped_subdirs}")
                
                # 限制扫描深度（避免扫描太深）
                depth = root.replace(directory, '').count(os.sep)
                if depth > MAX_SCAN_DEPTH:
                    print(f"[LogParser] 达到最大扫描深度 {MAX_SCAN_DEPTH}，停止深入：{root}")
                    dirs.clear()  # 不再深入子目录
                    continue
                
                # 限制单个目录的文件数量（性能优化）
                if len(files) > MAX_FILES_PER_DIR:
                    print(f"[LogParser] 目录文件数超限 ({len(files)} > {MAX_FILES_PER_DIR})，只处理前 {MAX_FILES_PER_DIR} 个：{root}")
                files = files[:MAX_FILES_PER_DIR]
                total_files += len(files)
                    
                for filename in files:
                    # 匹配日志文件：*.log, *.jsonl
                    if isinstance(filename, str):
                        # 跳过锁文件和临时文件
                        if filename.endswith('.lock') or filename.endswith('.tmp') or filename.endswith('.deleted'):
                            skipped_files += 1
                            continue
                        
                        # 增强日志文件识别：支持更多扩展名
                        is_log_file = (
                            filename.endswith('.log') or 
                            filename.endswith('.jsonl') or
                            filename.endswith('.jsonl.bak') or  # 备份文件
                            (filename.startswith('openclaw-') and '.' not in filename)  # 无扩展名的日志
                        )
                        
                        if not is_log_file:
                            skipped_files += 1
                            continue
                        
                        filepath = os.path.join(root, filename)
                        
                        # 跳过过大的文件（>50MB）
                        try:
                            file_size = os.path.getsize(filepath)
                            if file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
                                print(f"[LogParser] 跳过过大文件：{filepath} ({file_size / 1024 / 1024:.1f}MB > {MAX_FILE_SIZE_MB}MB)")
                                skipped_files += 1
                                continue
                        except OSError:
                            skipped_files += 1
                            continue
                        
                        scanned_files += 1
                        
                        if filename.endswith('.log'):
                            # 传统日志格式
                            file_entries = self.parse_jsonl_file(filepath)
                            entries.extend(file_entries)
                            if file_entries:
                                print(f"[LogParser] 解析日志文件：{filename} ({len(file_entries)} 条)")
                        elif filename.endswith('.jsonl'):
                            # 智能判断日志类型
                            file_entries = self._parse_smart_jsonl(filepath, directory)
                            entries.extend(file_entries)
                            if file_entries:
                                print(f"[LogParser] 解析 JSONL 文件：{filename} ({len(file_entries)} 条)")
            
            print(f"[LogParser] 目录扫描完成：{directory}")
            print(f"[LogParser] 统计：总计 {total_files} 个文件，扫描 {scanned_files} 个，跳过 {skipped_files} 个，获取 {len(entries)} 条日志")
            
        except PermissionError:
            print(f"[LogParser] 无权限访问目录：{directory}")
        except Exception as e:
            import traceback
            print(f"[LogParser] 扫描目录 {directory} 时出错：{e}")
            print(f"[LogParser] 错误堆栈：{traceback.format_exc()[:500]}")
        
        return entries
    
    def _parse_smart_jsonl(self, filepath: str, directory: str) -> List[LogEntry]:
        """
        智能解析 JSONL 文件，自动判断格式
        
        判断逻辑：
        1. 路径包含 'sessions' → 会话日志格式
        2. 首行包含 'type' 字段 → 会话日志格式
        3. 首行包含 '0' 或 '_meta' 字段 → 传统日志格式
        4. 默认使用传统日志格式
        
        Args:
            filepath: 文件路径
            directory: 所属目录（用于路径判断）
            
        Returns:
            日志条目列表
        """
        # 路径判断优先
        if 'sessions' in directory.lower():
            return self.parse_session_jsonl(filepath)
        
        # 检查文件内容判断格式
        if self._is_session_log(filepath):
            return self.parse_session_jsonl(filepath)
        else:
            return self.parse_jsonl_file(filepath)
    
    def _is_session_log(self, filepath: str) -> bool:
        """
        检查文件是否为新版本会话日志
        
        Args:
            filepath: 文件路径
            
        Returns:
            True 如果是会话日志
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                if first_line:
                    data = json.loads(first_line)
                    return 'type' in data and 'version' in data
        except Exception:
            pass
        return False
    
    def extract_stats(self, entries: List[LogEntry]) -> LogStats:
        """
        从日志条目中提取统计信息
        
        Args:
            entries: 日志条目列表
            
        Returns:
            LogStats 统计对象
        """
        stats = LogStats()
        
        for entry in entries:
            stats.add_entry(entry)
        
        # 添加 token 统计
        stats.model_usage = self.token_stats
        
        return stats
    
    def get_token_stats(self) -> Dict[str, Dict[str, Any]]:
        """
        获取 token 使用统计
        
        Returns:
            token 统计字典
        """
        return self.token_stats
    
    def get_entries_by_type(self, entries: List[LogEntry], log_type: str) -> List[LogEntry]:
        """按类型过滤日志条目"""
        return [e for e in entries if e.log_type == log_type]
    
    def get_entries_by_level(self, entries: List[LogEntry], level: str) -> List[LogEntry]:
        """按级别过滤日志条目"""
        return [e for e in entries if e.level == level]


# =============================================================================
# 技能扫描器
# =============================================================================

class SkillScanner:
    """
    OpenClaw 技能扫描器
    
    负责扫描所有 workspace 目录下的技能，支持多 agent 配置。
    
    技能来源分类：
    - Workspace Skills（自定义）- 来自各 agent workspace/skills 目录
    - Built-in Skills（内置）- 来自 OpenClaw bundled
    - Extra Skills（扩展）- 来自插件如 qqbot
    """
    
    def __init__(self, workspace: str = None):
        """
        初始化技能扫描器
        
        Args:
            workspace: 默认工作区路径，默认为 ~/.openclaw/workspace
        """
        if workspace is None:
            workspace = str(Path.home() / '.openclaw' / 'workspace')
        self.default_workspace = workspace
        self.openclaw_home = str(Path.home() / '.openclaw')
        self.config_file = os.path.join(self.openclaw_home, 'openclaw.json')
    
    def get_agent_workspaces(self) -> List[Dict[str, str]]:
        """从 openclaw.json 获取所有 agent 的 workspace 配置"""
        agents = []
        
        # 添加默认 workspace
        agents.append({
            'id': 'default',
            'workspace': self.default_workspace
        })
        
        try:
            import re
            with open(self.config_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 移除注释（支持 JSON5）
            content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
            content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
            
            config = json.loads(content)
            
            # 解析 agents.list
            agents_list = config.get('agents', {}).get('list', [])
            for agent in agents_list:
                agent_id = agent.get('id', '')
                agent_workspace = agent.get('workspace', '')
                if agent_workspace and agent_workspace != self.default_workspace:
                    agents.append({
                        'id': agent_id,
                        'workspace': agent_workspace
                    })
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        
        return agents
    
    def scan_workspace_skills(self, workspace: str, source: str = 'workspace') -> List[Skill]:
        """扫描指定 workspace 的技能"""
        skills = []
        skills_dir = os.path.join(workspace, SKILLS_DIR)
        
        if not os.path.exists(skills_dir):
            return skills
        
        for skill_name in os.listdir(skills_dir):
            skill_path = os.path.join(skills_dir, skill_name)
            
            # 只处理目录
            if not os.path.isdir(skill_path):
                continue
            
            # 查找 SKILL.md 文件
            skill_md = os.path.join(skill_path, SKILL_FILE)
            if os.path.exists(skill_md):
                skill = Skill.from_skill_md(skill_md, source=source)
                if skill:
                    skills.append(skill)
        
        return skills
    
    def scan_extra_skills(self) -> List[Skill]:
        """扫描扩展技能（来自插件）"""
        extra_skills = []
        extensions_dir = os.path.join(self.openclaw_home, 'extensions')
        
        if not os.path.exists(extensions_dir):
            return extra_skills
        
        # 扫描各插件的 skills 目录
        for plugin_name in os.listdir(extensions_dir):
            plugin_path = os.path.join(extensions_dir, plugin_name)
            if not os.path.isdir(plugin_path):
                continue
            
            # 检查插件的 skills 目录
            plugin_skills_dir = os.path.join(plugin_path, 'skills')
            if os.path.exists(plugin_skills_dir):
                for skill_name in os.listdir(plugin_skills_dir):
                    skill_path = os.path.join(plugin_skills_dir, skill_name)
                    if os.path.isdir(skill_path):
                        skill_md = os.path.join(skill_path, SKILL_FILE)
                        if os.path.exists(skill_md):
                            skill = Skill.from_skill_md(skill_md, source='extra')
                            if skill:
                                extra_skills.append(skill)
        
        return extra_skills
    
    def scan_all(self) -> List[Skill]:
        """扫描所有技能"""
        all_skills = []
        seen_names = set()
        
        # 1. 扫描所有 agent 的 workspace
        agents = self.get_agent_workspaces()
        for agent in agents:
            workspace = agent['workspace']
            agent_skills = self.scan_workspace_skills(workspace, source='workspace')
            for skill in agent_skills:
                if skill.name not in seen_names:
                    seen_names.add(skill.name)
                    all_skills.append(skill)
        
        # 2. 扫描扩展技能
        extra_skills = self.scan_extra_skills()
        for skill in extra_skills:
            if skill.name not in seen_names:
                seen_names.add(skill.name)
                all_skills.append(skill)
        
        return all_skills
    
    def get_skills_by_source(self, skills: List[Skill], source: str) -> List[Skill]:
        """按来源过滤技能"""
        return [s for s in skills if s.source == source]
    
    def get_by_category(self, skills: List[Skill], category: str) -> List[Skill]:
        """按类别过滤技能"""
        return [s for s in skills if s.category == category]
    
    def get_custom_skills(self, skills: List[Skill]) -> List[Skill]:
        """获取所有自定义技能"""
        return [s for s in skills if s.is_custom]


# =============================================================================
# 配置分析器
# =============================================================================

class ConfigAnalyzer:
    """
    OpenClaw 配置分析器
    
    负责解析 ~/.openclaw/openclaw.json 配置文件。
    支持多路径查找，确保能找到配置文件。
    """
    
    def __init__(self, openclaw_home: str = None):
        """
        初始化配置分析器
        
        Args:
            openclaw_home: OpenClaw 主目录，默认为 ~/.openclaw
        """
        if openclaw_home is None:
            openclaw_home = str(Path.home() / '.openclaw')
        self.openclaw_home = openclaw_home
        
        # 多路径查找配置文件
        self.config_paths = [
            os.path.join(openclaw_home, OPENCLAW_CONFIG_FILE),  # ~/.openclaw/openclaw.json
            os.path.join(openclaw_home, 'config', OPENCLAW_CONFIG_FILE),  # ~/.openclaw/config/openclaw.json
            os.path.expanduser('~/Library/Application Support/openclaw/openclaw.json'),  # macOS 标准路径
        ]
        self.config_file = self.config_paths[0]  # 默认使用第一个路径
    
    def parse(self) -> Optional[OpenClawConfig]:
        """解析配置文件（尝试多个路径）"""
        for config_path in self.config_paths:
            config = OpenClawConfig.from_json_file(config_path)
            if config:
                self.config_file = config_path
                print(f"[ConfigAnalyzer] ✅ 配置文件找到：{config_path}")
                return config
        
        print(f"[ConfigAnalyzer] ⚠️  配置文件未找到，尝试路径：{self.config_paths}")
        return None
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        config = self.parse()
        if not config:
            return {}
        
        return {
            'primary_model': config.primary_model,
            'agent_count': config.agent_count
        }
    
    def get_channels(self) -> List[str]:
        """获取配置的渠道列表"""
        config = self.parse()
        if not config:
            return []
        
        return config.channels


# =============================================================================
# 数据采集器（整合模块）
# =============================================================================

class DataCollector:
    """
    数据采集器 - 整合所有数据源
    
    协调日志解析、技能扫描和配置分析，提供统一的数据采集接口。
    """
    
    def __init__(self, openclaw_home: str = None, workspace: str = None):
        """
        初始化数据采集器
        
        Args:
            openclaw_home: OpenClaw 主目录
            workspace: 工作区路径
        """
        self.openclaw_home = openclaw_home or str(Path.home() / '.openclaw')
        self.log_parser = LogParser(openclaw_home=self.openclaw_home)
        self.skill_scanner = SkillScanner(workspace)
        self.config_analyzer = ConfigAnalyzer(self.openclaw_home)
    
    def collect(self) -> CollectionData:
        """
        执行完整的数据采集
        
        Returns:
            CollectionData 采集结果
        """
        print("\n" + "="*60)
        print("[DataCollector] 🦞 ClawValue 数据采集开始")
        print("="*60)
        
        # 1. 解析日志
        print("\n[DataCollector] 📝 步骤 1/6: 解析日志...")
        print(f"[DataCollector] 扫描目录：{self.log_parser.scan_dirs}")
        log_entries = self.log_parser.get_all_logs()
        log_stats = self.log_parser.extract_stats(log_entries)
        print(f"[DataCollector] ✅ 日志解析完成：{log_stats.total_entries} 条")
        
        # 2. 扫描技能
        print("\n[DataCollector] 📦 步骤 2/6: 扫描技能...")
        skills = self.skill_scanner.scan_all()
        print(f"[DataCollector] ✅ 技能扫描完成：{len(skills)} 个技能")
        
        # 按来源统计
        workspace_skills = len([s for s in skills if s.source == 'workspace'])
        extra_skills = len([s for s in skills if s.source == 'extra'])
        print(f"[DataCollector]    - 自定义技能：{workspace_skills} 个")
        print(f"[DataCollector]    - 扩展技能：{extra_skills} 个")
        
        # 3. 解析配置
        print("\n[DataCollector] ⚙️  步骤 3/6: 解析配置...")
        config = self.config_analyzer.parse()
        if config:
            print(f"[DataCollector] ✅ 配置解析完成")
            print(f"[DataCollector]    - 主模型：{config.primary_model}")
            print(f"[DataCollector]    - Agent 数量：{config.agent_count}")
            print(f"[DataCollector]    - 渠道：{len(config.channels)} 个")
        else:
            print(f"[DataCollector] ⚠️  配置文件未找到或解析失败")
        
        # 4. 统计会话数量（从会话日志文件数统计）
        print("\n[DataCollector] 💬 步骤 4/6: 统计会话...")
        log_stats.session_count = self._count_session_files()
        print(f"[DataCollector] ✅ 会话数量：{log_stats.session_count} 个")
        
        # 5. 统计 Cron 任务执行情况
        print("\n[DataCollector] ⏰ 步骤 5/6: 统计 Cron 任务...")
        log_stats.cron_executions = self._count_cron_executions(log_entries)
        print(f"[DataCollector] ✅ Cron 执行次数：{log_stats.cron_executions} 次")
        
        # 6. 检测 Gateway 状态
        print("\n[DataCollector] 🚪 步骤 6/6: 检测 Gateway 状态...")
        log_stats.gateway_status = self._check_gateway_status()
        
        # 7. 计算使用天数
        usage_days = self._estimate_usage_days(log_entries)
        
        # 输出 Token 统计摘要
        token_stats = self.log_parser.get_token_stats()
        if token_stats:
            print("\n[DataCollector] 💰 Token 使用统计:")
            total_tokens = 0
            total_cost = 0.0
            for model, stats in token_stats.items():
                model_tokens = stats['total_tokens']
                model_cost = stats['cost']
                total_tokens += model_tokens
                total_cost += model_cost
                print(f"[DataCollector]    - {model}: {model_tokens:,} tokens, ¥{model_cost:.2f}")
            print(f"[DataCollector]    总计：{total_tokens:,} tokens, ¥{total_cost:.2f}")
        
        # 工具调用统计
        if log_stats.tool_calls_by_type:
            print("\n[DataCollector] 🛠️  工具调用统计 (Top 10):")
            sorted_tools = sorted(log_stats.tool_calls_by_type.items(), key=lambda x: x[1], reverse=True)[:10]
            for tool_name, count in sorted_tools:
                print(f"[DataCollector]    - {tool_name}: {count} 次")
        
        print("\n" + "="*60)
        print(f"[DataCollector] ✅ 数据采集完成！")
        print(f"[DataCollector] 📊 汇总：{log_stats.total_entries} 条日志 | {len(skills)} 个技能 | {log_stats.session_count} 个会话 | {usage_days} 天")
        print("="*60 + "\n")
        
        return CollectionData(
            skills=skills,
            config=config,
            log_stats=log_stats,
            usage_days=usage_days
        )
    
    def _count_session_files(self) -> int:
        """统计会话文件数量"""
        sessions_dir = os.path.join(self.openclaw_home, SESSIONS_DIR_NEW)
        if not os.path.exists(sessions_dir):
            return 0
        
        count = 0
        for f in os.listdir(sessions_dir):
            if f.endswith('.jsonl') and not f.endswith('.lock'):
                count += 1
        return max(count, 1)
    
    def _estimate_usage_days(self, entries: List[LogEntry]) -> int:
        """估算使用天数"""
        if not entries:
            return 1
        
        dates = set()
        for entry in entries:
            if entry.timestamp:
                try:
                    date_part = entry.timestamp[:10]
                    dates.add(date_part)
                except Exception:
                    pass
        
        return max(len(dates), 1)
    
    def _count_cron_executions(self, entries: List[LogEntry]) -> int:
        """
        统计 Cron 任务执行次数
        
        识别模式：
        - 包含 'cron' 关键词
        - 包含 'scheduled' 关键词
        - 包含 '定时' 关键词
        - 包含 'heartbeat' 关键词
        - 包含 'edict' 关键词（三省六部制）
        
        Args:
            entries: 日志条目列表
            
        Returns:
            Cron 执行次数
        """
        count = 0
        keywords = ['cron', 'scheduled', '定时', 'heartbeat', '心跳', 'edict', '三省']
        
        for entry in entries:
            msg_lower = entry.message.lower()
            if any(kw in msg_lower or kw.lower() in msg_lower for kw in keywords):
                count += 1
        
        return count
    
    def _check_gateway_status(self) -> str:
        """
        检查 Gateway 运行状态
        
        检测方式：
        1. 检查进程是否存在 (pgrep)
        2. 检查端口是否监听（7890, 使用 lsof 或 netstat）
        3. 检查最近日志是否有活动
        
        Returns:
            状态：'running', 'stopped', 'unknown'
        """
        import subprocess
        
        try:
            # 方式 1: 检查进程
            result = subprocess.run(
                ['pgrep', '-f', 'openclaw'],
                capture_output=True,
                text=True,
                timeout=5
            )
            process_found = result.returncode == 0 and result.stdout.strip()
            
            if process_found:
                print(f"[DataCollector] Gateway 进程：找到 (PID: {result.stdout.strip()[:50]})")
                
                # 方式 2: 检查端口（尝试多种命令）
                port_found = False
                port_check_methods = [
                    ['lsof', '-i', ':7890'],
                    ['netstat', '-an', '|', 'grep', '7890'],
                    ['ss', '-tlnp', '|', 'grep', '7890']
                ]
                
                # 优先尝试 lsof
                try:
                    port_result = subprocess.run(
                        ['lsof', '-i', ':7890'],
                        capture_output=True,
                        text=True,
                        timeout=3
                    )
                    if port_result.returncode == 0:
                        port_found = True
                        print("[DataCollector] Gateway 端口：7890 (lsof 检测通过)")
                except FileNotFoundError:
                    print("[DataCollector] lsof 命令不存在，尝试其他方式")
                except Exception as e:
                    print(f"[DataCollector] lsof 检测失败：{e}")
                
                # 如果 lsof 失败，尝试 netstat
                if not port_found:
                    try:
                        # 使用 shell 管道
                        port_result = subprocess.run(
                            'netstat -an 2>/dev/null | grep -q ":7890"',
                            shell=True,
                            timeout=3
                        )
                        if port_result.returncode == 0:
                            port_found = True
                            print("[DataCollector] Gateway 端口：7890 (netstat 检测通过)")
                    except Exception as e:
                        print(f"[DataCollector] netstat 检测失败：{e}")
                
                if port_found:
                    print("[DataCollector] Gateway 状态：running ✅ (进程 + 端口检测通过)")
                    return 'running'
                else:
                    print("[DataCollector] Gateway 状态：running ⚠️ (进程存在，端口检测失败)")
                    return 'running'
            else:
                print("[DataCollector] Gateway 状态：stopped ❌ (无进程)")
                return 'stopped'
        except FileNotFoundError as e:
            # pgrep 命令不存在
            print(f"[DataCollector] Gateway 状态：unknown ❌ (命令不存在：{e})")
            return 'unknown'
        except Exception as e:
            print(f"[DataCollector] 检查 Gateway 状态失败：{e}")
            return 'unknown'
    
    def collect_summary(self) -> Dict[str, Any]:
        """获取采集摘要"""
        data = self.collect()
        
        return {
            'total_skills': data.total_skills,
            'custom_skills': data.custom_skills,
            'log_entries': data.log_stats.total_entries,
            'tool_calls': data.log_stats.tool_calls,
            'errors': data.log_stats.error_count,
            'primary_model': data.config.primary_model if data.config else 'unknown',
            'channels': len(data.config.channels) if data.config else 0,
            'usage_days': data.usage_days,
            'token_stats': self.log_parser.get_token_stats()
        }


# =============================================================================
# 命令行入口
# =============================================================================

if __name__ == '__main__':
    """命令行测试入口"""
    
    print("=" * 60)
    print("🦞 ClawValue 数据采集测试")
    print("=" * 60)
    
    collector = DataCollector()
    
    # 采集数据
    print("\n📊 正在采集数据...")
    data = collector.collect()
    
    # 输出结果
    print(f"\n✅ 采集完成!")
    print(f"\n📁 技能统计:")
    print(f"   - 总数：{data.total_skills}")
    print(f"   - 自定义：{data.custom_skills}")
    
    print(f"\n📝 日志统计:")
    print(f"   - 总条目：{data.log_stats.total_entries}")
    print(f"   - INFO: {data.log_stats.info_count}")
    print(f"   - WARN: {data.log_stats.warn_count}")
    print(f"   - ERROR: {data.log_stats.error_count}")
    print(f"   - 工具调用：{data.log_stats.tool_calls}")
    
    # 输出 token 统计
    token_stats = collector.log_parser.get_token_stats()
    if token_stats:
        print(f"\n💰 Token 使用统计:")
        for model, stats in token_stats.items():
            print(f"   - {model}:")
            print(f"      输入：{stats['input_tokens']:,} tokens")
            print(f"      输出：{stats['output_tokens']:,} tokens")
            print(f"      总计：{stats['total_tokens']:,} tokens")
            print(f"      调用：{stats['call_count']} 次")
    
    if data.config:
        print(f"\n⚙️ 配置信息:")
        print(f"   - 主模型：{data.config.primary_model}")
        print(f"   - Agent 数量：{data.config.agent_count}")
        print(f"   - 渠道：{', '.join(data.config.channels) or '无'}")
        print(f"   - 心跳检测：{'已开启' if data.config.has_heartbeat else '未开启'}")
    
    print(f"\n📅 使用天数：{data.usage_days}")
    print(f"📊 会话数量：{data.log_stats.session_count}")
    
    # 输出技能列表
    if data.skills:
        print(f"\n📋 技能列表 (前 10 个):")
        for skill in data.skills[:10]:
            desc = skill.description[:40] + '...' if len(skill.description) > 40 else skill.description
            print(f"   - [{skill.category}] {skill.name}: {desc}")
