#!/usr/bin/env python3
"""
ClawValue 评估模块单元测试
"""

import unittest
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.evaluation import EvaluationEngine


class TestEvaluationEngine(unittest.TestCase):
    """评估引擎测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.engine = EvaluationEngine()
    
    def test_shallow_level_evaluation(self):
        """测试浅度使用评估"""
        data = {
            'total_skills': 3,
            'total_tokens': 5000,
            'usage_days': 1,
            'skills': [{'name': 'skill1', 'is_custom': False}],
            'config': {
                'agent_count': 1,
                'heartbeat_interval': 0,
                'channels': []
            }
        }
        
        result = self.engine.evaluate_usage_depth(data)
        
        self.assertIn(result['level'], ['shallow', 'moderate'])
        self.assertGreaterEqual(result['skill_score'], 0)
        self.assertLessEqual(result['skill_score'], 100)
        self.assertIn('metrics', result)
    
    def test_moderate_level_evaluation(self):
        """测试中度使用评估"""
        data = {
            'total_skills': 10,
            'total_tokens': 100000,
            'usage_days': 30,
            'skills': [
                {'name': 'skill1', 'is_custom': True},
                {'name': 'skill2', 'is_custom': True},
                {'name': 'skill3', 'is_custom': False}
            ],
            'config': {
                'agent_count': 2,
                'heartbeat_interval': 1800,
                'channels': ['qqbot']
            }
        }
        
        result = self.engine.evaluate_usage_depth(data)
        
        self.assertIn(result['level'], ['moderate', 'deep'])
        self.assertGreater(result['skill_score'], 20)
        self.assertTrue(result['metrics']['has_heartbeat'])
    
    def test_deep_level_evaluation(self):
        """测试深度使用评估"""
        data = {
            'total_skills': 20,
            'total_tokens': 1000000,
            'usage_days': 90,
            'skills': [
                {'name': f'skill{i}', 'is_custom': i < 8} for i in range(20)
            ],
            'config': {
                'agent_count': 3,
                'heartbeat_interval': 300,
                'channels': ['qqbot', 'telegram', 'discord', 'slack']
            }
        }
        
        result = self.engine.evaluate_usage_depth(data)
        
        self.assertEqual(result['level'], 'deep')
        self.assertGreater(result['skill_score'], 50)
        self.assertEqual(result['metrics']['custom_skills'], 8)
    
    def test_value_estimation(self):
        """测试价值估算"""
        # 浅度使用价值
        eval_shallow = {'level': 'shallow', 'total_score': 20}
        value_shallow = self.engine.estimate_value(eval_shallow)
        self.assertIn('value_estimate', value_shallow)
        self.assertIn('元', value_shallow['value_estimate'])
        
        # 深度使用价值
        eval_deep = {'level': 'deep', 'total_score': 85}
        value_deep = self.engine.estimate_value(eval_deep)
        self.assertIn('value_estimate', value_deep)
    
    def test_lobster_skill(self):
        """测试龙虾等级获取"""
        for level in ['shallow', 'moderate', 'deep']:
            result = self.engine.get_lobster_skill(level)
            self.assertIn('title', result)
            self.assertIn('rank', result)
            self.assertIn('message', result)
            self.assertIn('龙虾能力估Skill', result['title'])
    
    def test_achievements_detection(self):
        """测试成就检测"""
        data = {
            'total_skills': 15,
            'total_tokens': 2000000,
            'usage_days': 60,
            'skills': [
                {'name': f'skill{i}', 'is_custom': i < 6} for i in range(15)
            ],
            'config': {
                'agent_count': 2,
                'heartbeat_interval': 300,
                'channels': ['qqbot', 'telegram', 'discord']
            },
            'log_stats': {'error_count': 0}
        }
        
        evaluation = {
            'level': 'deep',
            'total_score': 75,
            'metrics': {
                'skill_count': 15,
                'custom_skills': 6,
                'has_heartbeat': True,
                'channels': 3,
                'daily_tokens': 30000
            }
        }
        
        achievements = self.engine.detect_achievements(data, evaluation)
        
        # 应该检测到多个成就
        self.assertGreater(len(achievements), 0)
        
        # 检查成就格式
        for achievement in achievements:
            self.assertIsInstance(achievement, str)
            self.assertGreater(len(achievement), 0)
    
    def test_full_evaluation(self):
        """测试完整评估流程"""
        data = {
            'total_skills': 12,
            'total_tokens': 150000,
            'usage_days': 30,
            'skills': [
                {'name': 'skill1', 'is_custom': True},
                {'name': 'skill2', 'is_custom': True},
                {'name': 'skill3', 'is_custom': False}
            ],
            'config': {
                'agent_count': 2,
                'heartbeat_interval': 1800,
                'channels': ['qqbot', 'telegram']
            }
        }
        
        result = self.engine.generate_full_evaluation(data)
        
        # 检查必要字段
        self.assertIn('evaluated_at', result)
        self.assertIn('usage_level', result)
        self.assertIn('value_estimate', result)
        self.assertIn('lobster_skill', result)
        self.assertIn('lobster_message', result)
        self.assertIn('achievements', result)
        self.assertIn('metrics', result)
        
        # 检查评估时间格式
        self.assertIn('T', result['evaluated_at'])  # ISO 格式


class TestEvaluationEdgeCases(unittest.TestCase):
    """边缘情况测试"""
    
    def setUp(self):
        self.engine = EvaluationEngine()
    
    def test_empty_data(self):
        """测试空数据"""
        data = {}
        result = self.engine.evaluate_usage_depth(data)
        
        self.assertIn('level', result)
        self.assertIn('metrics', result)
    
    def test_zero_values(self):
        """测试零值"""
        data = {
            'total_skills': 0,
            'total_tokens': 0,
            'usage_days': 0,
            'skills': [],
            'config': None
        }
        
        result = self.engine.evaluate_usage_depth(data)
        
        self.assertEqual(result['level'], 'shallow')
        self.assertEqual(result['metrics']['skill_count'], 0)
    
    def test_very_large_values(self):
        """测试超大值"""
        data = {
            'total_skills': 100,
            'total_tokens': 100000000,  # 1亿
            'usage_days': 365,
            'skills': [{'name': f'skill{i}', 'is_custom': True} for i in range(50)],
            'config': {
                'agent_count': 10,
                'heartbeat_interval': 60,
                'channels': list(range(10))
            }
        }
        
        result = self.engine.evaluate_usage_depth(data)
        
        self.assertEqual(result['level'], 'deep')
        self.assertLessEqual(result['skill_score'], 100)  # 不超过满分


if __name__ == '__main__':
    unittest.main(verbosity=2)