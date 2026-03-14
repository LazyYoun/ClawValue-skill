#!/usr/bin/env python3
"""成就图标生成器 - 简化版"""

import os
import sys
import requests
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.image_generator import WanxImageGenerator

# 成就定义 (key: name, desc)
ACHIEVEMENTS = {
    'skill_master': ('技能大师', '自定义技能超过5个'),
    'skill_collector': ('技能收藏家', '技能数量超过10个'),
    'skill_connoisseur': ('技能鉴赏家', '技能数量超过15个'),
    'skill_legend': ('技能传奇', '技能数量超过20个'),
    'custom_creator': ('自定义创造者', '自定义技能超过3个'),
    'custom_master': ('自定义大师', '自定义技能超过7个'),
    'automation_pro': ('自动化达人', '心跳检测已开启'),
    'heartbeat_hero': ('心跳英雄', '心跳任务已配置'),
    'automation_god': ('自动化之神', '日均Token超过10万'),
    'cron_master': ('定时任务大师', '配置多个定时任务'),
    'multi_channel': ('多渠道运营', '连接多个平台'),
    'integration_expert': ('集成专家', '连接3个以上渠道'),
    'channel_master': ('渠道大师', '连接5个以上渠道'),
    'power_user': ('超级用户', 'Token消耗惊人'),
    'token_millionaire': ('Token百万富翁', 'Token消耗超过100万'),
    'token_billionaire': ('Token亿万富翁', 'Token消耗超过1000万'),
    'daily_active': ('活跃玩家', '连续使用超过7天'),
    'weekly_warrior': ('周常战士', '连续使用超过30天'),
    'monthly_master': ('月度大师', '连续使用超过90天'),
    'veteran_user': ('资深玩家', '使用超过180天'),
    'early_adopter': ('早期采用者', '比大多数人更早发现'),
    'night_owl': ('夜猫子认证', '深夜活跃使用'),
    'secret_lobster': ('龙虾宗师', '解锁隐藏成就'),
    'perfectionist': ('完美主义者', '所有指标优秀'),
}

OUTPUT_DIR = Path(__file__).parent.parent / 'web' / 'images' / 'achievements'

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"📁 输出目录: {OUTPUT_DIR}")
    
    gen = WanxImageGenerator()
    if not gen.api_key:
        print("❌ 未配置 API Key")
        return
    
    print(f"✅ API Key 已配置")
    print(f"📋 待生成: {len(ACHIEVEMENTS)} 个图标\n")
    
    success, fail = 0, 0
    
    for i, (key, (name, desc)) in enumerate(ACHIEVEMENTS.items(), 1):
        print(f"[{i}/{len(ACHIEVEMENTS)}] {name}...", end=" ", flush=True)
        
        result = gen.generate_achievement_icon(name, desc)
        
        if result.success:
            try:
                resp = requests.get(result.image_url, timeout=30)
                if resp.status_code == 200:
                    path = OUTPUT_DIR / f"{key}.png"
                    path.write_bytes(resp.content)
                    print(f"✅ {path.name}")
                    success += 1
                else:
                    print(f"❌ 下载失败({resp.status_code})")
                    fail += 1
            except Exception as e:
                print(f"❌ {e}")
                fail += 1
        else:
            print(f"❌ {result.error}")
            fail += 1
        
        time.sleep(1)  # 避免限流
    
    print(f"\n{'='*40}")
    print(f"✅ 成功: {success} | ❌ 失败: {fail}")

if __name__ == '__main__':
    main()