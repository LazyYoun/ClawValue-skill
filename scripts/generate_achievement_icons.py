#!/usr/bin/env python3
"""
成就图标生成脚本

使用万象API批量生成成就图标并保存到本地。
"""

import os
import sys
import requests
import time
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.image_generator import WanxImageGenerator

# 成就定义
ACHIEVEMENTS = {
    # 技能相关
    'skill_master': {'name': '技能大师', 'desc': '自定义技能≥5个', 'emoji': '🏅'},
    'skill_collector': {'name': '技能收藏家', 'desc': '技能数量≥10个', 'emoji': '📚'},
    'skill_connoisseur': {'name': '技能鉴赏家', 'desc': '技能数量≥15个', 'emoji': '🎖️'},
    'skill_legend': {'name': '技能传奇', 'desc': '技能数量≥20个', 'emoji': '👑'},
    'custom_creator': {'name': '自定义创造者', 'desc': '自定义技能≥3个', 'emoji': '🎨'},
    'custom_master': {'name': '自定义大师', 'desc': '自定义技能≥7个', 'emoji': '🛠️'},
    
    # 自动化相关
    'automation_pro': {'name': '自动化达人', 'desc': '心跳检测已开启', 'emoji': '🤖'},
    'heartbeat_hero': {'name': '心跳英雄', 'desc': '心跳任务已配置', 'emoji': '💓'},
    'automation_god': {'name': '自动化之神', 'desc': '日均Token≥10万', 'emoji': '⚡'},
    'cron_master': {'name': '定时任务大师', 'desc': '配置多个定时任务', 'emoji': '⏰'},
    
    # 集成相关
    'multi_channel': {'name': '多渠道运营', 'desc': '连接多个平台', 'emoji': '🌐'},
    'integration_expert': {'name': '集成专家', 'desc': '连接3个以上渠道', 'emoji': '🔗'},
    'channel_master': {'name': '渠道大师', 'desc': '连接5个以上渠道', 'emoji': '📡'},
    
    # 使用量相关
    'power_user': {'name': '超级用户', 'desc': 'Token消耗惊人', 'emoji': '⚡'},
    'token_millionaire': {'name': 'Token百万富翁', 'desc': 'Token消耗≥100万', 'emoji': '💰'},
    'token_billionaire': {'name': 'Token亿万富翁', 'desc': 'Token消耗≥1000万', 'emoji': '💎'},
    
    # 活跃度
    'daily_active': {'name': '活跃玩家', 'desc': '连续使用≥7天', 'emoji': '📅'},
    'weekly_warrior': {'name': '周常战士', 'desc': '连续使用≥30天', 'emoji': '🗓️'},
    'monthly_master': {'name': '月度大师', 'desc': '连续使用≥90天', 'emoji': '📆'},
    'veteran_user': {'name': '资深玩家', 'desc': '使用≥180天', 'emoji': '🏆'},
    
    # 特殊
    'early_adopter': {'name': '早期采用者', 'desc': '比大多数人更早发现', 'emoji': '🚀'},
    'night_owl': {'name': '夜猫子认证', 'desc': '深夜活跃使用', 'emoji': '🦉'},
    'secret_lobster': {'name': '龙虾宗师', 'desc': '解锁隐藏成就', 'emoji': '🦞'},
    'perfectionist': {'name': '完美主义者', 'desc': '所有指标优秀', 'emoji': '✨'},
}

# 输出目录
OUTPUT_DIR = Path(__file__).parent.parent / 'web' / 'images' / 'achievements'

def main():
    """主函数"""
    print("=" * 60)
    print("🦞 成就图标生成器")
    print("=" * 60)
    
    # 创建输出目录
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"\n📁 输出目录: {OUTPUT_DIR}")
    
    # 初始化生成器
    generator = WanxImageGenerator()
    
    if not generator.api_key:
        print("❌ 未配置 DASHSCOPE_API_KEY")
        return
    
    print(f"✅ API Key 已配置")
    
    # 生成图标
    success_count = 0
    fail_count = 0
    
    for key, info in ACHIEVEMENTS.items():
        print(f"\n🎨 生成: {info['name']}...")
        
        result = generator.generate_achievement_icon(
            achievement_name=info['name'],
            achievement_desc=info['desc']
        )
        
        if result.success:
            # 下载图片
            try:
                response = requests.get(result.image_url, timeout=30)
                if response.status_code == 200:
                    output_path = OUTPUT_DIR / f"{key}.png"
                    with open(output_path, 'wb') as f:
                        f.write(response.content)
                    print(f"   ✅ 保存成功: {output_path.name}")
                    success_count += 1
                else:
                    print(f"   ❌ 下载失败: {response.status_code}")
                    fail_count += 1
            except Exception as e:
                print(f"   ❌ 下载异常: {e}")
                fail_count += 1
        else:
            print(f"   ❌ 生成失败: {result.error}")
            fail_count += 1
        
        # 避免API限流
        time.sleep(2)
    
    print("\n" + "=" * 60)
    print(f"✅ 成功: {success_count} | ❌ 失败: {fail_count}")
    print("=" * 60)

if __name__ == '__main__':
    main()