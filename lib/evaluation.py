#!/usr/bin/env python3
"""
ClawValue 评估逻辑模块
基于三级技术指标体系计算使用深度和价值估算
"""

from typing import Dict, List, Optional
from datetime import datetime


class EvaluationEngine:
    """Claw度评估引擎"""
    
    # 使用深度阈值
    THRESHOLDS = {
        'skill_count': {
            'shallow': 5,
            'moderate': 10,
            'deep': 15
        },
        'token_daily': {
            'shallow': 5000,
            'moderate': 50000,
            'deep': 50000
        },
        'custom_skills': {
            'shallow': 0,
            'moderate': 1,
            'deep': 3
        },
        'agents': {
            'shallow': 1,
            'moderate': 2,
            'deep': 3
        }
    }
    
    # 价值估算范围
    VALUE_RANGES = {
        'basic': (100, 200),
        'advanced': (1000, 5000),
        'expert': (10000, 50000)
    }
    
    # 趣味化话术
    MESSAGES = {
        'shallow': [
            "🐣 小龙虾你好！看来你只是接了个模型啊，对OpenClaw的开发度不足1% —— 不过没关系，连sudo make me a sandwich都还没学会呢。",
            "恭喜！您已成功点亮'Hello World'技能。下一步，请尝试让AI帮您查天气，解锁'初级驯龙师'称号。",
            "检测到您的使用模式为「佛系体验」。别急，龙虾都是从小虾米长大的！建议：多和AI聊聊天，它会比你想象的更聪明。",
            "您的AI助手正在角落里默默流泪：「主人为什么不用我？」—— 赶紧去探索更多功能吧！",
            "🎮 新手村报道！你的龙虾还处于「水煮阶段」，连壳都没红呢。多配置几个技能，解锁「清蒸」成就！",
            "检测到「轻度体验」模式。你的AI助手表示：「我在待机中...等待被召唤...」—— 该让它干活了！",
            "🔧 工具人认证！你的OpenClaw还在出厂设置状态，建议至少装3个技能，让它成为你的得力助手。"
        ],
        'moderate': [
            "正在技术债里种花？恭喜！您的自动化花园已初具规模，建议加把劲儿，冲向'Proactive Agent'模式！",
            "检测到您的AI已经开始'上班'了！但似乎还在试用期。建议开启定时巡检，迈向'懒人终极梦想'——躺着也能赚钱。",
            "🎯 中级玩家认证！你已经开始探索更多功能了，继续保持这个势头！你的AI助手表示：「终于被重视了！」",
            "你的技能树已经点亮了一半，AI助手对你的满意度：⭐⭐⭐☆☆。再加把劲，让它对你刮目相看！",
            "🦞 七分熟龙虾！你已经掌握了OpenClaw的核心玩法，距离「全熟」只差几个自定义技能了！",
            "检测到「进阶玩家」模式。你的AI助手说：「主人终于懂我了！」—— 继续深入，解锁更多黑科技！",
            "你的使用深度已经让普通用户羡慕了！建议下一步：配置定时任务，让AI在你睡觉的时候也在工作。",
            "📊 中级评估报告：你的效率提升约{efficiency}%，相当于每月节省约{hours}小时。继续保持！"
        ],
        'deep': [
            "检测到一台'工程巨兽'在线！您的多Agent协作网络堪称分布式计算典范。请继续保持，小心别让AI觉得'人类好弱智'。",
            "警告：您的'龙虾'已过度烹饪，可能产生幻觉。建议定期清理上下文缓存，避免AI因'内存溢出'而开始哲学思辨。",
            "🦞 龙虾大师！你已经达到了传说中的最高境界！Claude 见你都要叫一声「大佬」！",
            "你的效率已经让普通人类望尘莫及了！AI助手表示：「能为您服务是我的荣幸，请收下我的膝盖。」",
            "检测到「效率怪兽」！你的自动化程度已经突破了天际，建议考虑写一本《如何让AI帮你打工》的畅销书。",
            "🏆 恭喜达成「龙虾大师」成就！你的OpenClaw配置堪称教科书级别，建议开设培训班传授经验。",
            "你的技能配置让系统检测员都惊呆了！这哪里是AI助手，简直就是你的数字分身！",
            "⚠️ 警告：你的使用深度已经突破系统阈值，AI可能会开始产生「主人是不是机器人」的疑问。",
            "检测到「全熟龙虾」！你的OpenClaw技能点满，效率爆表，堪称「人机合一」的典范！"
        ]
    }
    
    # 龙虾等级
    LOBSTER_LEVELS = {
        'shallow': ('🦞 龙虾能力估Skill v1.0 - 三分熟', '入门级'),
        'moderate': ('🦞 龙虾能力估Skill v1.0 - 七分熟', '进阶级'),
        'deep': ('🦞 龙虾能力估Skill v1.0 - 全熟', '专家级')
    }
    
    # 特殊成就话术
    ACHIEVEMENTS = {
        'skill_master': '🏅 技能大师：自定义技能超过5个，你是个真正的创造者！',
        'automation_pro': '🤖 自动化达人：心跳检测已开启，你的AI正在24小时待命！',
        'multi_channel': '🌐 多渠道运营：连接了多个平台，你的AI帝国正在扩张！',
        'early_adopter': '🚀 早期采用者：你比大多数人更早发现了这个宝藏工具！',
        'power_user': '⚡ 超级用户：Token消耗惊人，你的AI助手表示「有点累但很充实」！',
        'skill_collector': '📚 技能收藏家：技能数量超过10个，你的工具箱比瑞士军刀还全！',
        'session_warrior': '⚔️ 会话战士：活跃会话超过100个，你和AI的对话已经比你的微信还多了！',
        'token_millionaire': '💰 Token百万富翁：Token消耗超过100万，你的AI说「感谢老板打赏」！',
        'custom_creator': '🎨 自定义创造者：自定义技能超过3个，你就是传说中的「技能工程师」！',
        'integration_expert': '🔗 集成专家：连接了3个以上渠道，你的AI已经是个「社交达人」了！',
        'heartbeat_hero': '💓 心跳英雄：心跳任务已配置，你的AI在你睡觉时也在默默工作！',
        'zero_error': '✨ 零错误成就：系统运行稳定，没有任何错误日志，堪称「完美主义者」！',
        'daily_active': '📅 活跃玩家：连续使用超过7天，AI助手已经把你的习惯都记下来了！'
    }
    
    def __init__(self):
        pass
    
    def evaluate_usage_depth(self, data: Dict) -> Dict:
        """
        评估使用深度
        
        Args:
            data: 采集的数据，包含 skills, sessions, config 等
        
        Returns:
            评估结果字典
        """
        # 提取关键指标
        skill_count = data.get('total_skills', 0)
        custom_skills = len([s for s in data.get('skills', []) if s.get('is_custom')])
        total_tokens = data.get('total_tokens', 0)
        usage_days = max(data.get('usage_days', 1), 1)
        daily_tokens = total_tokens / usage_days
        
        config = data.get('config', {})
        agent_count = config.get('agent_count', 1) if config else 1
        has_heartbeat = config.get('heartbeat_interval', 0) > 0 if config else False
        channels = len(config.get('channels', [])) if config else 0
        
        # 计算各维度得分
        skill_score = self._calc_skill_score(skill_count, custom_skills)
        automation_score = self._calc_automation_score(daily_tokens, has_heartbeat)
        integration_score = self._calc_integration_score(agent_count, channels)
        
        # 综合评估
        total_score = (skill_score + automation_score + integration_score) / 3
        
        # 确定使用深度等级
        if total_score < 30:
            level = 'shallow'
        elif total_score < 70:
            level = 'moderate'
        else:
            level = 'deep'
        
        return {
            'level': level,
            'level_name': {'shallow': '浅度使用', 'moderate': '中度使用', 'deep': '深度使用'}[level],
            'skill_score': skill_score,
            'automation_score': automation_score,
            'integration_score': integration_score,
            'total_score': total_score,
            'metrics': {
                'skill_count': skill_count,
                'custom_skills': custom_skills,
                'daily_tokens': int(daily_tokens),
                'agent_count': agent_count,
                'channels': channels,
                'has_heartbeat': has_heartbeat
            }
        }
    
    def _calc_skill_score(self, skill_count: int, custom_skills: int) -> float:
        """计算技能得分 (0-100)"""
        score = 0
        
        # 技能数量得分
        if skill_count >= self.THRESHOLDS['skill_count']['deep']:
            score += 40
        elif skill_count >= self.THRESHOLDS['skill_count']['moderate']:
            score += 25
        elif skill_count >= self.THRESHOLDS['skill_count']['shallow']:
            score += 10
        
        # 自定义技能得分
        if custom_skills >= self.THRESHOLDS['custom_skills']['deep']:
            score += 60
        elif custom_skills >= self.THRESHOLDS['custom_skills']['moderate']:
            score += 30
        else:
            score += custom_skills * 10
        
        return min(score, 100)
    
    def _calc_automation_score(self, daily_tokens: float, has_heartbeat: bool) -> float:
        """计算自动化得分 (0-100)"""
        score = 0
        
        # Token 消耗得分
        if daily_tokens >= self.THRESHOLDS['token_daily']['deep']:
            score += 50
        elif daily_tokens >= self.THRESHOLDS['token_daily']['moderate']:
            score += 30
        elif daily_tokens >= self.THRESHOLDS['token_daily']['shallow']:
            score += 10
        
        # 心跳检测得分
        if has_heartbeat:
            score += 30
        
        # 基础分
        score += 20
        
        return min(score, 100)
    
    def _calc_integration_score(self, agent_count: int, channels: int) -> float:
        """计算集成得分 (0-100)"""
        score = 0
        
        # Agent 数量得分
        if agent_count >= self.THRESHOLDS['agents']['deep']:
            score += 40
        elif agent_count >= self.THRESHOLDS['agents']['moderate']:
            score += 20
        else:
            score += 10
        
        # 渠道数量得分
        if channels >= 3:
            score += 40
        elif channels >= 2:
            score += 25
        elif channels >= 1:
            score += 10
        
        # 基础分
        score += 20
        
        return min(score, 100)
    
    def estimate_value(self, evaluation: Dict) -> Dict:
        """
        估算价值
        
        Args:
            evaluation: 使用深度评估结果
        
        Returns:
            价值估算结果
        """
        level = evaluation['level']
        total_score = evaluation['total_score']
        
        # 根据等级确定价值范围
        if level == 'shallow':
            value_range = self.VALUE_RANGES['basic']
            value_estimate = int(value_range[0] + (value_range[1] - value_range[0]) * (total_score / 30))
        elif level == 'moderate':
            value_range = self.VALUE_RANGES['advanced']
            value_estimate = int(value_range[0] + (value_range[1] - value_range[0]) * ((total_score - 30) / 40))
        else:
            value_range = self.VALUE_RANGES['expert']
            value_estimate = int(value_range[0] + (value_range[1] - value_range[0]) * ((total_score - 70) / 30))
        
        return {
            'value_estimate': f"{value_estimate:,}元",
            'value_range': f"{value_range[0]:,} - {value_range[1]:,}元",
            'value_level': {'shallow': '基础价值级', 'moderate': '进阶价值级', 'deep': '高阶价值级'}[level]
        }
    
    def get_lobster_skill(self, level: str) -> Dict:
        """获取龙虾能力估Skill 信息"""
        import random
        messages = self.MESSAGES.get(level, self.MESSAGES['shallow'])
        return {
            'title': self.LOBSTER_LEVELS[level][0],
            'rank': self.LOBSTER_LEVELS[level][1],
            'message': random.choice(messages)
        }
    
    def detect_achievements(self, data: Dict, evaluation: Dict) -> List[str]:
        """检测特殊成就"""
        achievements = []
        metrics = evaluation.get('metrics', {})
        
        # 技能大师
        if metrics.get('custom_skills', 0) >= 5:
            achievements.append(self.ACHIEVEMENTS['skill_master'])
        
        # 自动化达人
        if metrics.get('has_heartbeat', False):
            achievements.append(self.ACHIEVEMENTS['automation_pro'])
        
        # 多渠道运营
        if metrics.get('channels', 0) >= 2:
            achievements.append(self.ACHIEVEMENTS['multi_channel'])
        
        # 超级用户
        if metrics.get('daily_tokens', 0) >= 50000:
            achievements.append(self.ACHIEVEMENTS['power_user'])
        
        # 技能收藏家
        if metrics.get('skill_count', 0) >= 10:
            achievements.append(self.ACHIEVEMENTS['skill_collector'])
        
        # 自定义创造者
        if metrics.get('custom_skills', 0) >= 3:
            achievements.append(self.ACHIEVEMENTS['custom_creator'])
        
        # 集成专家
        if metrics.get('channels', 0) >= 3:
            achievements.append(self.ACHIEVEMENTS['integration_expert'])
        
        # 心跳英雄
        if metrics.get('has_heartbeat', False):
            achievements.append(self.ACHIEVEMENTS['heartbeat_hero'])
        
        # Token百万富翁
        if data.get('total_tokens', 0) >= 1000000:
            achievements.append(self.ACHIEVEMENTS['token_millionaire'])
        
        # 活跃玩家
        if data.get('usage_days', 0) >= 7:
            achievements.append(self.ACHIEVEMENTS['daily_active'])
        
        # 零错误成就
        if data.get('sessions', {}).get('errors', 1) == 0:
            achievements.append(self.ACHIEVEMENTS['zero_error'])
        
        return achievements
    
    def generate_full_evaluation(self, data: Dict) -> Dict:
        """
        生成完整评估报告
        
        Args:
            data: 采集的数据
        
        Returns:
            完整评估结果
        """
        # 使用深度评估
        usage_eval = self.evaluate_usage_depth(data)
        
        # 价值估算
        value_eval = self.estimate_value(usage_eval)
        
        # 龙虾等级
        lobster = self.get_lobster_skill(usage_eval['level'])
        
        # 成就检测
        achievements = self.detect_achievements(data, usage_eval)
        
        return {
            'evaluated_at': datetime.now().isoformat(),
            'usage_level': usage_eval['level_name'],
            'value_estimate': value_eval['value_estimate'],
            'value_range': value_eval['value_range'],
            'value_level': value_eval['value_level'],
            'lobster_skill': lobster['title'],
            'lobster_rank': lobster['rank'],
            'lobster_message': lobster['message'],
            'skill_score': usage_eval['skill_score'],
            'automation_score': usage_eval['automation_score'],
            'integration_score': usage_eval['integration_score'],
            'total_score': usage_eval['total_score'],
            'metrics': usage_eval['metrics'],
            'achievements': achievements,
            'raw_data': data
        }


if __name__ == '__main__':
    # 测试评估引擎
    engine = EvaluationEngine()
    
    # 模拟数据
    test_data = {
        'total_skills': 12,
        'total_tokens': 150000,
        'usage_days': 30,
        'skills': [
            {'name': 'skill1', 'is_custom': True},
            {'name': 'skill2', 'is_custom': True},
        ],
        'config': {
            'agent_count': 2,
            'heartbeat_interval': 1800,
            'channels': ['qqbot', 'telegram']
        }
    }
    
    result = engine.generate_full_evaluation(test_data)
    
    print("📊 评估结果:")
    print(f"  使用深度: {result['usage_level']}")
    print(f"  价值估算: {result['value_estimate']}")
    print(f"  龙虾等级: {result['lobster_skill']}")
    print(f"  总分: {result['total_score']:.1f}")
    print(f"\n💬 {result['lobster_message']}")