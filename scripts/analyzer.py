#!/usr/bin/env python3
"""
ClawValue 数据分析器
支持多种输出模式：JSON、Markdown、消息格式
"""

import sys
import os
import json
import argparse
from datetime import datetime

# 添加 lib 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))

from parser import DataCollector
from evaluation import EvaluationEngine


def format_as_json(evaluation: dict) -> str:
    """格式化为 JSON 输出"""
    return json.dumps({
        'level': evaluation['usage_level'],
        'value_estimate': evaluation['value_estimate'],
        'skill_count': evaluation['metrics']['skill_count'],
        'custom_skills': evaluation['metrics']['custom_skills'],
        'total_score': evaluation['total_score'],
        'lobster_skill': evaluation['lobster_skill'],
        'lobster_rank': evaluation['lobster_rank'],
        'lobster_message': evaluation['lobster_message'],
        'achievements': evaluation['achievements'],
        'evaluated_at': evaluation['evaluated_at']
    }, ensure_ascii=False, indent=2)


def format_as_markdown(evaluation: dict) -> str:
    """格式化为 Markdown 报告"""
    md = f"""# 🦞 龙虾能力估Skill 评估报告

> 评估时间：{evaluation['evaluated_at']}

## 📊 评估概览

| 指标 | 数值 |
|------|------|
| 使用深度 | {evaluation['usage_level']} |
| 龙虾等级 | {evaluation['lobster_skill']} |
| 价值估算 | {evaluation['value_estimate']} |
| 综合得分 | {evaluation['total_score']:.1f} |

## 📈 详细得分

| 维度 | 得分 |
|------|------|
| 技能得分 | {evaluation['skill_score']:.1f} |
| 自动化得分 | {evaluation['automation_score']:.1f} |
| 集成得分 | {evaluation['integration_score']:.1f} |

## 🔧 技能统计

- 总技能数：{evaluation['metrics']['skill_count']}
- 自定义技能：{evaluation['metrics']['custom_skills']}
- Agent 数量：{evaluation['metrics']['agent_count']}
- 集成渠道：{evaluation['metrics']['channels']}

## 💬 龙虾点评

{evaluation['lobster_message']}

"""
    
    if evaluation['achievements']:
        md += "## 🏆 成就解锁\n\n"
        for a in evaluation['achievements']:
            md += f"- {a}\n"
    
    return md


def format_as_message(evaluation: dict) -> str:
    """格式化为 OpenClaw 消息格式（适合 QQ/Discord 等平台）"""
    emoji = "🦞" if evaluation['total_score'] < 70 else "🔥"
    
    msg = f"""{emoji} 龙虾能力估Skill v1.0

📊 评估结果
• 等级：{evaluation['lobster_skill']}
• 深度：{evaluation['usage_level']}
• 得分：{evaluation['total_score']:.1f} 分
• 估值：{evaluation['value_estimate']}

📈 维度得分
• 技能：{evaluation['skill_score']} | 自动化：{evaluation['automation_score']} | 集成：{evaluation['integration_score']}

💬 点评
{evaluation['lobster_message']}
"""
    
    if evaluation['achievements']:
        msg += f"\n🏆 成就：{len(evaluation['achievements'])} 个\n"
        for a in evaluation['achievements'][:3]:  # 最多显示3个
            msg += f"• {a}\n"
    
    return msg.strip()


def format_as_brief(evaluation: dict) -> str:
    """格式化为简短消息"""
    level_emoji = {
        '浅度使用': '🐣',
        '中度使用': '🎯',
        '深度使用': '🔥'
    }
    emoji = level_emoji.get(evaluation['usage_level'], '🦞')
    
    return f"""{emoji} {evaluation['lobster_skill']}
得分 {evaluation['total_score']:.0f} | 估值 {evaluation['value_estimate']}
{evaluation['lobster_message'][:50]}..."""


def main():
    parser = argparse.ArgumentParser(description='ClawValue 数据分析器')
    parser.add_argument('--mode', '-m', choices=['json', 'markdown', 'md', 'message', 'msg', 'brief'],
                        default='json', help='输出格式')
    parser.add_argument('--output', '-o', help='输出文件路径')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    args = parser.parse_args()
    
    # 采集数据
    if args.verbose:
        print("正在采集数据...", file=sys.stderr)
    
    collector = DataCollector()
    data = collector.collect_all()
    
    if args.verbose:
        print(f"采集完成：{data['total_skills']} 技能，{data['usage_days']} 天使用", file=sys.stderr)
    
    # 评估
    engine = EvaluationEngine()
    evaluation = engine.generate_full_evaluation(data)
    
    # 格式化输出
    if args.mode == 'json':
        output = format_as_json(evaluation)
    elif args.mode in ['markdown', 'md']:
        output = format_as_markdown(evaluation)
    elif args.mode in ['message', 'msg']:
        output = format_as_message(evaluation)
    elif args.mode == 'brief':
        output = format_as_brief(evaluation)
    else:
        output = format_as_json(evaluation)
    
    # 输出
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"报告已保存到 {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == '__main__':
    main()