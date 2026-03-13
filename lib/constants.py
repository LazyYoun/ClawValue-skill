"""
ClawValue 常量定义模块

集中管理所有配置常量、字段名称和阈值定义。
遵循"单一真相源"原则，避免魔法数字和硬编码字符串。

设计理念:
- 所有关键配置集中在此文件
- 字段名称使用常量定义，便于维护和重构
- 阈值参数可配置化，支持未来调整
"""

# =============================================================================
# 路径配置
# =============================================================================

# OpenClaw 配置路径
OPENCLAW_HOME = '~/.openclaw'
OPENCLAW_CONFIG_FILE = 'openclaw.json'

# 日志路径（官方文档定义）
LOG_DIR = '/tmp/openclaw'
LOG_FILE_PATTERN = 'openclaw-YYYY-MM-DD.log'

# 技能目录
SKILLS_DIR = 'skills'
SKILL_FILE = 'SKILL.md'

# 数据库路径
DEFAULT_DB_PATH = '~/.openclaw/workspace/data/clawvalue.db'

# =============================================================================
# 日志字段常量 (Log Field Constants)
# =============================================================================

class LogField:
    """
    OpenClaw 日志 JSON 字段常量
    
    日志格式示例:
    {
        "0": "[tools] read failed: ...",
        "_meta": {
            "logLevelName": "ERROR",
            "logLevelId": 5,
            "runtime": "node",
            "runtimeVersion": "23.5.0",
            "hostname": "unknown",
            "name": "openclaw",
            "date": "2026-03-12T17:00:04.080Z",
            "path": {
                "fullFilePath": "file:///opt/homebrew/.../logger.js:20:34",
                "fileName": "logger.js",
                "fileNameWithLine": "logger.js:20",
                "fileLine": "20",
                "fileColumn": "34"
            }
        },
        "time": "2026-03-13T01:00:04.080+08:00"
    }
    
    参考: https://docs.openclaw.ai/zh-CN/logging
    """
    # 顶层字段
    MESSAGE = '0'              # 日志消息字段（OpenClaw 使用 "0" 作为消息键）
    MESSAGE_ALT = 'message'    # 备用消息字段
    META = '_meta'             # 元数据字段
    TIMESTAMP = 'time'         # 时间戳字段（本地时间）
    
    # 元数据字段 (_meta 子字段)
    class Meta:
        """_meta 对象内的字段"""
        # 日志级别
        LEVEL = 'logLevelName'         # 日志级别名称: DEBUG/INFO/WARN/ERROR/FATAL
        LEVEL_ID = 'logLevelId'        # 日志级别 ID (数字: 0-5)
        
        # 运行时信息
        RUNTIME = 'runtime'            # 运行时环境: node
        RUNTIME_VERSION = 'runtimeVersion'  # 运行时版本: 23.5.0
        HOSTNAME = 'hostname'          # 主机名
        APP_NAME = 'name'              # 应用名称: openclaw
        
        # 时间
        DATE = 'date'                  # UTC 时间戳
        
        # 文件路径信息
        PATH = 'path'                  # 文件路径对象
    
    # 路径字段 (path 子字段)
    class Path:
        """_meta.path 对象内的字段"""
        FULL_PATH = 'fullFilePath'     # 完整文件路径
        FILE_NAME = 'fileName'         # 文件名
        FILE_WITH_LINE = 'fileNameWithLine'  # 文件名:行号
        FILE_LINE = 'fileLine'         # 行号
        FILE_COLUMN = 'fileColumn'     # 列号


class LogLevel:
    """日志级别常量"""
    DEBUG = 'DEBUG'
    INFO = 'INFO'
    WARN = 'WARN'
    ERROR = 'ERROR'
    FATAL = 'FATAL'
    TRACE = 'TRACE'


class LogType:
    """
    日志类型分类常量
    
    用于统计不同类型的日志活动
    """
    ERROR = 'error'           # 错误日志
    SESSION = 'session'       # 会话相关
    TOOL = 'tool'             # 工具/技能调用
    MODEL = 'model'           # 模型调用
    MESSAGE = 'message'       # 消息/Webhook
    CONNECTION = 'connection' # 连接状态
    OTHER = 'other'           # 其他


# =============================================================================
# 评估阈值常量 (Evaluation Thresholds)
# =============================================================================

class SkillThreshold:
    """
    技能评估阈值
    
    用于判断使用深度等级
    """
    # 技能数量阈值
    SKILL_COUNT_SHALLOW = 5
    SKILL_COUNT_MODERATE = 10
    SKILL_COUNT_DEEP = 15
    
    # 自定义技能阈值
    CUSTOM_SKILL_SHALLOW = 0
    CUSTOM_SKILL_MODERATE = 1
    CUSTOM_SKILL_DEEP = 3
    
    # Token 日均阈值
    TOKEN_DAILY_SHALLOW = 5000
    TOKEN_DAILY_MODERATE = 50000
    TOKEN_DAILY_DEEP = 100000
    
    # Agent 数量阈值
    AGENT_SHALLOW = 1
    AGENT_MODERATE = 2
    AGENT_DEEP = 3


class DepthLevel:
    """
    使用深度等级定义
    
    等级范围: 1-5
    """
    MIN = 1
    MAX = 5
    
    # 等级名称
    NAMES = {
        1: ('入门小白', '🐣'),
        2: ('初级玩家', '🎮'),
        3: ('中级开发者', '💻'),
        4: ('高级工程师', '🚀'),
        5: ('龙虾大师', '🦞')
    }
    
    # 分数阈值
    SCORE_THRESHOLDS = {
        1: 20,
        2: 40,
        3: 60,
        4: 80,
        5: 100
    }


class ValueRange:
    """
    价值估算范围
    
    单位: 人民币 (CNY)
    """
    BASIC = (100, 200)        # 基础价值级
    ADVANCED = (1000, 5000)   # 进阶价值级
    EXPERT = (10000, 50000)   # 高阶价值级


# =============================================================================
# 龙虾等级常量
# =============================================================================

class LobsterLevel:
    """
    龙虾能力估Skill 等级定义
    
    对应使用深度的三个档位
    """
    SHALLOW = 'shallow'       # 三分熟
    MODERATE = 'moderate'     # 七分熟
    DEEP = 'deep'             # 全熟
    
    LABELS = {
        'shallow': ('🦞 龙虾能力估Skill v1.0 - 三分熟', '入门级'),
        'moderate': ('🦞 龙虾能力估Skill v1.0 - 七分熟', '进阶级'),
        'deep': ('🦞 龙虾能力估Skill v1.0 - 全熟', '专家级')
    }


# =============================================================================
# 成就常量
# =============================================================================

class Achievement:
    """
    成就定义
    
    解锁条件和显示信息
    """
    # 成就 ID
    SKILL_MASTER = 'skill_master'
    AUTOMATION_PRO = 'automation_pro'
    MULTI_CHANNEL = 'multi_channel'
    POWER_USER = 'power_user'
    EARLY_ADOPTER = 'early_adopter'
    
    # 成就信息: (显示文本, 解锁条件描述)
    INFO = {
        'skill_master': (
            '🏅 技能大师',
            '自定义技能超过5个，你是个真正的创造者！'
        ),
        'automation_pro': (
            '🤖 自动化达人',
            '心跳检测已开启，你的AI正在24小时待命！'
        ),
        'multi_channel': (
            '🌐 多渠道运营',
            '连接了多个平台，你的AI帝国正在扩张！'
        ),
        'power_user': (
            '⚡ 超级用户',
            'Token消耗惊人，你的AI助手表示「有点累但很充实」！'
        ),
        'early_adopter': (
            '🚀 早期采用者',
            '你比大多数人更早发现了这个宝藏工具！'
        )
    }
    
    # 解锁阈值
    THRESHOLDS = {
        'skill_master': 5,        # 自定义技能数
        'automation_pro': True,   # 心跳检测开启
        'multi_channel': 2,       # 渠道数量
        'power_user': 50000       # 日均 Token
    }


# =============================================================================
# 技能分类常量
# =============================================================================

class SkillCategory:
    """
    技能类别定义
    
    用于分类和统计用户技能
    """
    SEARCH = 'Search & Research'
    DEVOPS = 'DevOps & Cloud'
    TOOLS = 'Tools & Utilities'
    COMMUNICATION = 'Communication'
    DATA = 'Data & Storage'
    MEDIA = 'Media & Content'
    OTHER = 'Other'
    
    # 关键词映射
    KEYWORDS = {
        'Search & Research': ['搜索', 'search', '查询', 'web', '研究', 'research'],
        'DevOps & Cloud': ['devops', '部署', 'ci/cd', 'docker', 'k8s', 'cloud'],
        'Tools & Utilities': ['mcp', '工具', 'tool', 'utility', 'util'],
        'Communication': ['消息', 'message', '通知', 'notify', 'notify', '聊天'],
        'Data & Storage': ['数据库', 'database', 'sql', '存储', 'storage', 'db'],
        'Media & Content': ['媒体', 'media', '图片', 'image', '视频', 'video', '音频']
    }


# =============================================================================
# API 响应常量
# =============================================================================

class APIResponse:
    """API 响应字段常量"""
    SUCCESS = 'success'
    DATA = 'data'
    ERROR = 'error'
    MESSAGE = 'message'
    TIMESTAMP = 'timestamp'


# =============================================================================
# 默认值常量
# =============================================================================

class Defaults:
    """默认值定义"""
    HOST = '127.0.0.1'
    PORT = 5002
    DEBUG = False
    
    # 评估默认值
    DEFAULT_SKILL_COUNT = 0
    DEFAULT_TOKEN_COUNT = 0
    DEFAULT_SESSION_COUNT = 0
    DEFAULT_USAGE_DAYS = 1


# =============================================================================
# 版本信息
# =============================================================================

VERSION = '1.0.0'
APP_NAME = 'ClawValue'
APP_TITLE = '🦞 龙虾能力估值 Skill'
APP_DESCRIPTION = 'OpenClaw Claw度评估系统 - 量化你的 AI 自动化能力'