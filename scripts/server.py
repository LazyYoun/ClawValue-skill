#!/usr/bin/env python3
"""
ClawValue 后端服务

提供 RESTful API 和静态文件服务。

API 端点:
- GET /api/         - 仪表盘主数据
- GET /api/stats    - 统计数据
- GET /api/skills   - 技能列表
- GET /api/sessions - 会话历史
- GET /api/evaluation - 评估结果
- POST /api/refresh - 刷新数据
- GET /api/health   - 健康检查

参考文档: docs/OPENCLAW_REFERENCE.md
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
from flask import Flask, jsonify, send_from_directory, request

# 添加 lib 目录到路径
lib_path = os.path.join(os.path.dirname(__file__), '..', 'lib')
sys.path.insert(0, lib_path)

# 导入核心模块
from collector import DataCollector
from evaluation import EvaluationEngine
from constants import DepthLevel, LobsterLevel, Achievement

# 创建 Flask 应用
app = Flask(__name__,
            static_folder=os.path.join(os.path.dirname(__file__), '..', 'web'))


@app.route('/')
def index():
    """首页"""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """
    获取统计数据

    Returns:
        - skill_count: 技能总数
        - custom_skill_count: 自定义技能数
        - session_count: 会话总数
        - total_tokens: Token 消耗总量
        - usage_days: 使用天数
    """
    try:
        database = get_db()
        stats = database.get_latest_stats()
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/skills', methods=['GET'])
def get_skills():
    """
    获取技能列表

    Query params:
        - category: 按类别筛选
        - custom_only: 仅显示自定义技能

    Returns:
        - skills: 技能列表
    """
    try:
        database = get_db()
        skills = database.get_skill_list()

        # 可选筛选
        category = request.args.get('category')
        custom_only = request.args.get('custom_only', 'false').lower() == 'true'

        if category:
            skills = [s for s in skills if s.get('category') == category]
        if custom_only:
            skills = [s for s in skills if s.get('is_custom')]

        return jsonify({
            'success': True,
            'data': {
                'skills': skills,
                'total': len(skills)
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/sessions', methods=['GET'])
def get_sessions():
    """
    获取会话历史

    Query params:
        - limit: 返回数量限制
        - offset: 偏移量

    Returns:
        - sessions: 会话列表
    """
    try:
        database = get_db()
        cursor = database.conn.cursor()

        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)

        cursor.execute('''
            SELECT * FROM sessions
            ORDER BY last_active DESC
            LIMIT ? OFFSET ?
        ''', (limit, offset))

        sessions = [dict(row) for row in cursor.fetchall()]

        # 获取总数
        cursor.execute('SELECT COUNT(*) FROM sessions')
        total = cursor.fetchone()[0]

        return jsonify({
            'success': True,
            'data': {
                'sessions': sessions,
                'total': total,
                'limit': limit,
                'offset': offset
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/evaluation', methods=['GET'])
def get_evaluation():
    """
    获取评估结果

    Query params:
        - refresh: 是否刷新数据

    Returns:
        - evaluation: 评估结果
    """
    try:
        database = get_db()

        # 检查是否需要刷新
        refresh = request.args.get('refresh', 'false').lower() == 'true'

        if refresh:
            # 重新采集数据
            collector = DataCollector()
            data = collector.collect_all()

            # 评估
            engine = EvaluationEngine()
            evaluation = engine.generate_full_evaluation(data)

            # 存储到数据库
            database.insert_collection_record({
                'total_sessions': data['total_sessions'],
                'total_skills': data['total_skills'],
                'total_agents': data['config'].get('agent_count', 1) if data['config'] else 1,
                'total_tokens': data['total_tokens'],
                'usage_days': data['usage_days'],
                'error_count': data['errors']
            })

            for skill in data.get('skills', []):
                database.insert_skill(skill)

            database.insert_evaluation({
                'usage_level': evaluation['usage_level'],
                'value_estimate': evaluation['value_estimate'],
                'lobster_skill': evaluation['lobster_skill'],
                'skill_score': evaluation['skill_score'],
                'automation_score': evaluation['automation_score'],
                'integration_score': evaluation['integration_score'],
                'total_score': evaluation['total_score'],
                'raw_data': json.dumps(evaluation['raw_data'], ensure_ascii=False)
            })

            return jsonify({
                'success': True,
                'data': evaluation,
                'refreshed': True
            })
        else:
            # 返回最近的评估结果
            history = database.get_evaluation_history(limit=1)
            if history:
                evaluation = history[0]
                # 解析 raw_data
                if evaluation.get('raw_data'):
                    try:
                        evaluation['raw_data'] = json.loads(evaluation['raw_data'])
                    except:
                        pass
                return jsonify({
                    'success': True,
                    'data': evaluation,
                    'refreshed': False
                })
            else:
                # 没有历史数据，触发首次采集
                return get_evaluation_internal()
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def get_evaluation_internal():
    """内部评估方法"""
    collector = DataCollector()
    data = collector.collect_all()

    engine = EvaluationEngine()
    evaluation = engine.generate_full_evaluation(data)

    database = get_db()
    database.insert_collection_record({
        'total_sessions': data['total_sessions'],
        'total_skills': data['total_skills'],
        'total_agents': data['config'].get('agent_count', 1) if data['config'] else 1,
        'total_tokens': data['total_tokens'],
        'usage_days': data['usage_days'],
        'error_count': data['errors']
    })

    for skill in data.get('skills', []):
        database.insert_skill(skill)

    database.insert_evaluation({
        'usage_level': evaluation['usage_level'],
        'value_estimate': evaluation['value_estimate'],
        'lobster_skill': evaluation['lobster_skill'],
        'skill_score': evaluation['skill_score'],
        'automation_score': evaluation['automation_score'],
        'integration_score': evaluation['integration_score'],
        'total_score': evaluation['total_score'],
        'raw_data': json.dumps(evaluation['raw_data'], ensure_ascii=False)
    })

    return jsonify({
        'success': True,
        'data': evaluation,
        'refreshed': True
    })


@app.route('/api/refresh', methods=['POST'])
def refresh_data():
    """
    刷新数据

    手动触发数据重新采集
    """
    try:
        collector = DataCollector()
        data = collector.collect_all()

        engine = EvaluationEngine()
        evaluation = engine.generate_full_evaluation(data)

        database = get_db()

        # 插入采集记录
        database.insert_collection_record({
            'total_sessions': data['total_sessions'],
            'total_skills': data['total_skills'],
            'total_agents': data['config'].get('agent_count', 1) if data['config'] else 1,
            'total_tokens': data['total_tokens'],
            'usage_days': data['usage_days'],
            'error_count': data['errors']
        })

        # 插入技能
        for skill in data.get('skills', []):
            database.insert_skill(skill)

        # 插入评估结果
        database.insert_evaluation({
            'usage_level': evaluation['usage_level'],
            'value_estimate': evaluation['value_estimate'],
            'lobster_skill': evaluation['lobster_skill'],
            'skill_score': evaluation['skill_score'],
            'automation_score': evaluation['automation_score'],
            'integration_score': evaluation['integration_score'],
            'total_score': evaluation['total_score'],
            'raw_data': json.dumps(evaluation['raw_data'], ensure_ascii=False)
        })

        return jsonify({
            'success': True,
            'message': '数据已刷新',
            'data': evaluation
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/history', methods=['GET'])
def get_history():
    """
    获取历史评估记录

    Query params:
        - limit: 返回数量限制

    Returns:
        - history: 历史记录列表
    """
    try:
        database = get_db()
        limit = request.args.get('limit', 10, type=int)
        history = database.get_evaluation_history(limit=limit)

        # 解析 raw_data
        for record in history:
            if record.get('raw_data'):
                try:
                    record['raw_data'] = json.loads(record['raw_data'])
                except:
                    pass

        return jsonify({
            'success': True,
            'data': {
                'history': history,
                'total': len(history)
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'success': True,
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/', methods=['GET'])
@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    """
    获取仪表盘完整数据（前端主入口）

    Returns:
        - depth_level: 使用深度等级 (1-5)
        - depth_breakdown: 各维度得分
        - value_estimation: 价值估算
        - skills: 技能统计
        - sessions: 会话统计
        - trends: 使用趋势
    """
    try:
        # 使用新的数据采集模块
        collector = DataCollector()
        data = collector.collect()  # 返回 CollectionData 对象
        
        # 评估
        engine = EvaluationEngine()
        # 转换为字典格式供评估引擎使用
        data_dict = data.to_dict()
        evaluation = engine.generate_full_evaluation(data_dict)

        # 计算深度等级 (1-5)
        total_score = evaluation.get('total_score', 0)
        depth_level = 1
        for level, threshold in sorted(DepthLevel.SCORE_THRESHOLDS.items()):
            if total_score >= threshold:
                depth_level = level

        # 深度分布
        metrics = evaluation.get('metrics', {})
        depth_breakdown = [
            {'level': 1, 'name': '技能数量', 'count': metrics.get('skill_count', 0)},
            {'level': 2, 'name': '自定义技能', 'count': metrics.get('custom_skills', 0)},
            {'level': 3, 'name': '日志条目', 'count': data.log_stats.total_entries},
            {'level': 4, 'name': 'Agent数量', 'count': metrics.get('agent_count', 1)},
            {'level': 5, 'name': '集成渠道', 'count': metrics.get('channels', 0)}
        ]

        # 价值估算
        value_str = evaluation.get('value_estimate', '0元')
        try:
            value_amount = int(value_str.replace(',', '').replace('元', '').strip())
        except ValueError:
            value_amount = 0
            
        value_estimation = {
            'amount': value_amount,
            'description': evaluation.get('value_level', '基础价值级'),
            'hours_saved': data.log_stats.tool_calls,  # 用工具调用数估算
            'efficiency': min(int(total_score * 1.2), 200),
            'roi': f'{min(int(total_score / 10), 10)}x'
        }

        # 技能统计 - 使用新的数据模型
        skills = {
            'total': data.total_skills,
            'custom': data.custom_skills,
            'categories': data.categories
        }

        # 会话统计 - 使用新的数据模型
        sessions = {
            'total': data.log_stats.total_entries,
            'total_messages': data.log_stats.tool_calls,
            'avg_messages': data.log_stats.tool_calls // max(data.usage_days, 1),
            'active_days': data.usage_days
        }

        # 使用趋势（最近7天模拟）
        trends = []
        for i in range(6, -1, -1):
            date = datetime.now() - timedelta(days=i)
            trends.append({
                'date': date.strftime('%m-%d'),
                'count': max(0, data.log_stats.tool_calls // 7 + (7 - i) * 2)
            })

        # 成就列表
        achievements = evaluation.get('achievements', [])

        return jsonify({
            'success': True,
            'data': {
                'depth_level': depth_level,
                'depth_breakdown': depth_breakdown,
                'value_estimation': value_estimation,
                'skills': skills,
                'sessions': sessions,
                'trends': trends,
                'evaluation': evaluation,
                'achievements': achievements
            }
        })
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


def main():
    """启动服务器"""
    import argparse
    parser = argparse.ArgumentParser(description='ClawValue 后端服务')
    parser.add_argument('--port', '-p', type=int, default=5002, help='服务端口')
    parser.add_argument('--host', '-H', default='127.0.0.1', help='绑定地址')
    parser.add_argument('--debug', '-d', action='store_true', help='调试模式')
    args = parser.parse_args()

    print(f"""
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║   🦞 ClawValue - OpenClaw Claw度评估系统                    ║
║                                                            ║
║   服务地址: http://{args.host}:{args.port}                    ║
║   API 文档: http://{args.host}:{args.port}/api/stats         ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
    """)

    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == '__main__':
    main()