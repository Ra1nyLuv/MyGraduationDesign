#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ML API调试脚本
专门测试聚类分析和异常检测API是否正常工作
"""

import sys
import os
import requests
import json

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

def test_cluster_api():
    """测试聚类分析API"""
    print("🔍 测试聚类分析API")
    print("-" * 40)
    
    try:
        response = requests.get('http://localhost:5000/api/ml/cluster-analysis', timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        try:
            data = response.json()
            print("响应内容:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            if response.status_code == 200:
                if data.get('success'):
                    print("✅ 聚类分析API工作正常")
                    analysis = data.get('analysis')
                    if analysis:
                        print(f"📊 聚类数据: 总用户 {analysis.get('total_users', 0)} 人")
                        clusters = analysis.get('cluster_distribution', {})
                        for cluster_id, cluster_info in clusters.items():
                            print(f"   聚类{cluster_id}: {cluster_info.get('name', '未命名')} - {cluster_info.get('count', 0)}人")
                    else:
                        print("⚠️ 聚类分析数据为空")
                else:
                    print(f"❌ 聚类分析失败: {data.get('error', '未知错误')}")
            else:
                print(f"❌ API调用失败: {response.status_code}")
                
        except json.JSONDecodeError:
            print("❌ 响应不是有效的JSON格式")
            print(f"原始响应: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败: 请确保Flask服务器正在运行")
    except Exception as e:
        print(f"❌ 测试异常: {str(e)}")

def test_anomaly_api():
    """测试异常检测API"""
    print("\n🚨 测试异常检测API")
    print("-" * 40)
    
    try:
        response = requests.get('http://localhost:5000/api/ml/anomaly-detection', timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        try:
            data = response.json()
            print("响应内容:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            if response.status_code == 200:
                if data.get('success'):
                    print("✅ 异常检测API工作正常")
                    results = data.get('results')
                    if results:
                        print(f"📊 异常检测数据: 总用户 {results.get('total_users', 0)} 人")
                        print(f"   异常用户: {results.get('anomaly_count', 0)} 人")
                        print(f"   正常用户: {results.get('normal_count', 0)} 人")
                        print(f"   异常率: {results.get('anomaly_rate', 0):.1f}%")
                        
                        anomalies = results.get('anomalies', [])
                        if anomalies:
                            print(f"   异常用户列表:")
                            for anomaly in anomalies[:3]:  # 只显示前3个
                                print(f"     - {anomaly.get('user_id')}: {anomaly.get('severity', '未知')}风险")
                    else:
                        print("⚠️ 异常检测数据为空")
                else:
                    print(f"❌ 异常检测失败: {data.get('error', '未知错误')}")
            else:
                print(f"❌ API调用失败: {response.status_code}")
                
        except json.JSONDecodeError:
            print("❌ 响应不是有效的JSON格式")
            print(f"原始响应: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败: 请确保Flask服务器正在运行")
    except Exception as e:
        print(f"❌ 测试异常: {str(e)}")

def test_local_ml_functions():
    """本地测试ML函数"""
    print("\n🛠️ 本地测试ML函数")
    print("-" * 40)
    
    try:
        from app import app, User, db
        from ml_services import LearningBehaviorClustering, AnomalyDetector
        
        with app.app_context():
            # 获取用户数据
            users = User.query.options(
                db.joinedload(User.synthesis_grades),
                db.joinedload(User.homework_statistic),
                db.joinedload(User.discussion_participation),
                db.joinedload(User.video_watching_details)
            ).all()
            
            print(f"📊 数据库用户数量: {len(users)}")
            
            if len(users) < 3:
                print(f"❌ 用户数量不足: {len(users)} < 3")
                return False
            
            # 测试聚类分析
            print("\n🔗 测试聚类分析...")
            try:
                clustering = LearningBehaviorClustering()
                if clustering.train_model(users):
                    print("✅ 聚类模型训练成功")
                    
                    analysis = clustering.get_all_clusters_analysis(users)
                    if analysis:
                        print("✅ 聚类分析结果生成成功")
                        print(f"   总用户: {analysis.get('total_users', 0)}")
                        print(f"   聚类分布: {len(analysis.get('cluster_distribution', {}))}")
                        return True
                    else:
                        print("❌ 聚类分析结果生成失败")
                else:
                    print("❌ 聚类模型训练失败")
            except Exception as e:
                print(f"❌ 聚类分析异常: {str(e)}")
            
            # 测试异常检测
            print("\n🚨 测试异常检测...")
            try:
                detector = AnomalyDetector()
                if detector.train_model(users):
                    print("✅ 异常检测模型训练成功")
                    
                    results = detector.batch_detect_anomalies(users)
                    if results:
                        print("✅ 异常检测结果生成成功")
                        print(f"   总用户: {results.get('total_users', 0)}")
                        print(f"   异常用户: {results.get('anomaly_count', 0)}")
                        return True
                    else:
                        print("❌ 异常检测结果生成失败")
                else:
                    print("❌ 异常检测模型训练失败")
            except Exception as e:
                print(f"❌ 异常检测异常: {str(e)}")
                
    except Exception as e:
        print(f"❌ 本地测试失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("🔧 ML API调试工具")
    print("=" * 60)
    
    # 先测试本地ML函数
    local_success = test_local_ml_functions()
    
    if local_success:
        print("\n📡 本地ML函数正常，测试API端点...")
        test_cluster_api()
        test_anomaly_api()
    else:
        print("\n❌ 本地ML函数有问题，请先解决基础问题")
    
    print("\n" + "=" * 60)
    print("💡 调试建议:")
    print("1. 确保Flask服务器正在运行")
    print("2. 检查数据库中是否有足够的用户数据")
    print("3. 查看Flask控制台的错误日志")
    print("4. 在浏览器开发者工具中查看网络请求详情")

if __name__ == "__main__":
    main()