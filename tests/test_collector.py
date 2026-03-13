#!/usr/bin/env python3
"""
ClawValue 数据采集模块单元测试
"""

import unittest
import sys
import os
import json
import tempfile

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 直接从 parser.py 导入，因为它有完整的方法定义
from lib.parser import LogParser as ParserLogParser
from lib.parser import SkillScanner as ParserSkillScanner
from lib.parser import ConfigAnalyzer as ParserConfigAnalyzer
from lib.parser import DataCollector as ParserDataCollector


class TestLogParser(unittest.TestCase):
    """日志解析器测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.parser = ParserLogParser()
        self.temp_dir = tempfile.mkdtemp()
    
    def test_parse_jsonl_line(self):
        """测试单行 JSONL 解析"""
        line = '{"level":"INFO","message":"Test message","timestamp":"2026-03-13T12:00:00"}'
        result = self.parser._parse_openclaw_log(json.loads(line))
        
        self.assertIsNotNone(result)
    
    def test_parse_empty_line(self):
        """测试空行处理"""
        result = self.parser._parse_openclaw_log({})
        self.assertIsNotNone(result)
    
    def test_parse_log_file(self):
        """测试日志文件解析"""
        # 创建临时日志文件
        log_file = os.path.join(self.temp_dir, 'test.log')
        with open(log_file, 'w') as f:
            f.write('{"level":"INFO","message":"msg1"}\n')
            f.write('{"level":"ERROR","message":"msg2"}\n')
            f.write('{"level":"WARN","message":"msg3"}\n')
        
        result = self.parser.parse_jsonl_file(log_file)
        
        self.assertIsNotNone(result)
        self.assertGreater(len(result), 0)
    
    def test_parse_nonexistent_file(self):
        """测试不存在的文件"""
        result = self.parser.parse_jsonl_file('/nonexistent/path/file.log')
        
        self.assertEqual(len(result), 0)
    
    def test_extract_session_stats(self):
        """测试会话统计提取"""
        logs = [
            {'type': 'tool_call', 'level': 'INFO'},
            {'type': 'model_call', 'level': 'INFO'},
            {'type': 'error', 'level': 'ERROR'}
        ]
        
        result = self.parser.extract_session_stats(logs)
        
        self.assertIsNotNone(result)


class TestSkillScanner(unittest.TestCase):
    """技能扫描器测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.scanner = ParserSkillScanner()
    
    def test_scan_all_skills(self):
        """测试扫描所有技能"""
        result = self.scanner.scan_all_skills()
        
        # 结果应该是列表
        self.assertIsInstance(result, list)
    
    def test_parse_skill_md(self):
        """测试解析技能文件"""
        # 使用实际的技能目录扫描
        result = self.scanner.scan_all_skills()
        
        if len(result) > 0:
            skill = result[0]
            self.assertIn('name', skill)


class TestConfigAnalyzer(unittest.TestCase):
    """配置分析器测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.analyzer = ParserConfigAnalyzer()
    
    def test_parse_config(self):
        """测试分析配置"""
        result = self.analyzer.parse_config()
        
        # 配置可能不存在，但不应该崩溃
        # 只要方法能正常执行就算通过
        self.assertTrue(result is None or isinstance(result, dict))
    
    def test_extract_key_info(self):
        """测试提取关键信息"""
        config = {
            'agents': {
                'defaultModel': 'claude-3-5-sonnet'
            },
            'channels': {
                'qqbot': {'enabled': True},
                'telegram': {'enabled': True}
            }
        }
        
        result = self.analyzer._extract_key_info(config)
        
        self.assertIsNotNone(result)


class TestDataCollector(unittest.TestCase):
    """数据采集器测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.collector = ParserDataCollector()
    
    def test_collect_all(self):
        """测试采集所有数据"""
        result = self.collector.collect_all()
        
        self.assertIn('collected_at', result)
        self.assertIn('skills', result)


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_full_collection_flow(self):
        """测试完整采集流程"""
        collector = ParserDataCollector()
        
        # 采集数据
        data = collector.collect_all()
        
        # 验证数据结构
        self.assertIn('collected_at', data)
        self.assertIn('skills', data)
        
        # 验证时间戳格式
        self.assertIn('T', data['collected_at'])  # ISO 格式
    
    def test_evaluation_with_collected_data(self):
        """测试使用采集数据进行评估"""
        from lib.evaluation import EvaluationEngine
        
        collector = ParserDataCollector()
        engine = EvaluationEngine()
        
        # 采集数据
        data = collector.collect_all()
        
        # 转换为评估引擎需要的格式
        eval_data = {
            'total_skills': len(data.get('skills', [])),
            'total_tokens': 0,
            'usage_days': 1,
            'skills': data.get('skills', []),
            'config': None
        }
        
        # 执行评估
        result = engine.evaluate_usage_depth(eval_data)
        
        self.assertIn('level', result)
        self.assertIn('metrics', result)


if __name__ == '__main__':
    unittest.main(verbosity=2)