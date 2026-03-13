#!/usr/bin/env python3
"""
ClawValue 数据采集脚本
采集 OpenClaw 数据并存储到 SQLite
"""

import sys
import os
import json
import argparse
from pathlib import Path

# 添加 lib 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))

from parser import DataCollector
from models import ClawValueDB
from evaluation import EvaluationEngine


def main():
    parser = argparse.ArgumentParser(description='ClawValue 数据采集器')
    parser.add_argument('--output', '-o', choices=['json', 'db'], default='db',
                       help='输出格式：json 或 db（默认）')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    args = parser.parse_args()
    
    # 初始化采集器
    collector = DataCollector()
    
    # 采集数据
    print("📊 正在采集 OpenClaw 数据...")
    data = collector.collect_all()
    
    if args.verbose:
        print(f"  - 技能数量: {data['total_skills']}")
        print(f"  - 会话数量: {data['total_sessions']}")
        print(f"  - Token 消耗: {data['total_tokens']}")
        print(f"  - 消息总数: {data['total_messages']}")
        print(f"  - 工具调用: {data['tool_calls']}")
    
    # 评估
    print("🔍 正在评估使用深度...")
    engine = EvaluationEngine()
    evaluation = engine.generate_full_evaluation(data)
    
    if args.verbose:
        print(f"  - 使用深度: {evaluation['usage_level']}")
        print(f"  - 价值估算: {evaluation['value_estimate']}")
        print(f"  - 龙虾等级: {evaluation['lobster_skill']}")
    
    # 输出
    if args.output == 'json':
        print(json.dumps(evaluation, ensure_ascii=False, indent=2))
    else:
        # 存储到 SQLite
        print("💾 正在存储到数据库...")
        db = ClawValueDB()
        
        # 插入采集记录
        db.insert_collection_record({
            'total_sessions': data['total_sessions'],
            'total_skills': data['total_skills'],
            'total_agents': data['config'].get('agent_count', 1) if data['config'] else 1,
            'total_tokens': data['total_tokens'],
            'usage_days': data['usage_days'],
            'error_count': data['errors']
        })
        
        # 插入技能
        for skill in data.get('skills', []):
            db.insert_skill(skill)
        
        # 插入评估结果
        db.insert_evaluation({
            'usage_level': evaluation['usage_level'],
            'value_estimate': evaluation['value_estimate'],
            'lobster_skill': evaluation['lobster_skill'],
            'skill_score': evaluation['skill_score'],
            'automation_score': evaluation['automation_score'],
            'integration_score': evaluation['integration_score'],
            'total_score': evaluation['total_score'],
            'raw_data': json.dumps(evaluation['raw_data'], ensure_ascii=False)
        })
        
        db.close()
        print(f"✅ 数据已存储到: {db.db_path}")
    
    # 输出摘要
    print("\n" + "="*50)
    print(f"🦞 {evaluation['lobster_skill']}")
    print(f"📊 使用深度: {evaluation['usage_level']}")
    print(f"💰 价值估算: {evaluation['value_estimate']}")
    print(f"💬 {evaluation['lobster_message']}")
    print("="*50)


if __name__ == '__main__':
    main()