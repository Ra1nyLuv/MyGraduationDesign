#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试模型训练API修复
验证/api/ml/train-models接口是否正常工作
"""

import sys
import os
import requests
import json

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

def test_train_models_api():
    """测试模型训练API"""
    print("🧪 测试模型训练API")
    print("="*50)
    
    # API端点
    url = "http://localhost:5000/api/ml/train-models"
    
    # 请求头
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer admin_token'  # 假设的管理员token
    }
    
    try:
        print("📤 发送POST请求到模型训练API...")
        response = requests.post(url, headers=headers, json={}, timeout=30)
        
        print(f"📥 响应状态码: {response.status_code}")
        print(f"📄 响应头: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            print("📊 响应内容:")
            print(json.dumps(response_data, indent=2, ensure_ascii=False))
            
            if response.status_code == 200:
                print("✅ API调用成功")
                
                if response_data.get('success'):
                    print("✅ 模型训练成功")
                    results = response_data.get('results', {})
                    print(f"📈 训练结果: {results}")
                else:
                    print("❌ 模型训练失败")
                    errors = response_data.get('details', [])
                    if errors:
                        print("💥 详细错误:")
                        for error in errors:
                            print(f"   - {error}")
            else:
                print(f"❌ API调用失败: {response.status_code}")
                if 'error' in response_data:
                    print(f"💥 错误信息: {response_data['error']}")
                    if 'detail' in response_data:
                        print(f"💥 详细信息: {response_data['detail']}")
        
        except json.JSONDecodeError:
            print("❌ 响应不是有效的JSON格式")
            print(f"📄 原始响应: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败: 请确保Flask服务器正在运行")
        print("💡 启动命令: python app.py")
    except requests.exceptions.Timeout:
        print("❌ 请求超时: 模型训练可能需要更长时间")
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")

def test_local_training():
    """本地测试模型训练逻辑"""
    print("\n🧪 本地测试模型训练逻辑")
    print("="*50)
    
    try:
        from app import app, User, db
        from ml_services import GradePredictionModel, LearningBehaviorClustering, AnomalyDetector
        
        with app.app_context():
            print("📊 查询用户数据...")
            users = User.query.options(
                db.joinedload(User.synthesis_grades),
                db.joinedload(User.homework_statistic),
                db.joinedload(User.discussion_participation),
                db.joinedload(User.video_watching_details)
            ).all()
            
            print(f"👥 找到 {len(users)} 个用户")
            
            if len(users) < 3:
                print(f"❌ 用户数量不足: {len(users)} < 3")
                return False
            
            results = {
                'prediction_model': False,
                'clustering_model': False,
                'anomaly_model': False
            }
            
            # 测试预测模型
            print("🔮 测试预测模型训练...")
            try:
                predictor = GradePredictionModel()
                results['prediction_model'] = predictor.train_model(users)
                print(f"   结果: {'✅ 成功' if results['prediction_model'] else '❌ 失败'}")
            except Exception as e:
                print(f"   ❌ 异常: {str(e)}")
            
            # 测试聚类模型
            print("🔗 测试聚类模型训练...")
            try:
                clustering = LearningBehaviorClustering()
                results['clustering_model'] = clustering.train_model(users)
                print(f"   结果: {'✅ 成功' if results['clustering_model'] else '❌ 失败'}")
            except Exception as e:
                print(f"   ❌ 异常: {str(e)}")
            
            # 测试异常检测
            print("🚨 测试异常检测训练...")
            try:
                detector = AnomalyDetector()
                results['anomaly_model'] = detector.train_model(users)
                print(f"   结果: {'✅ 成功' if results['anomaly_model'] else '❌ 失败'}")
            except Exception as e:
                print(f"   ❌ 异常: {str(e)}")
            
            success_count = sum(results.values())
            print(f"\n📈 总结: {success_count}/3 个模型训练成功")
            
            return success_count > 0
            
    except Exception as e:
        print(f"❌ 本地测试失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("🩺 模型训练API修复验证")
    print("="*60)
    
    print("1️⃣ 本地测试模型训练逻辑")
    local_success = test_local_training()
    
    if local_success:
        print("\n2️⃣ 测试API接口")
        test_train_models_api()
    else:
        print("\n❌ 本地测试失败，跳过API测试")
        print("💡 请先解决本地训练问题")
    
    print("\n" + "="*60)
    print("🎯 使用说明:")
    print("1. 确保Flask服务器正在运行: python app.py")
    print("2. 在前端点击'运行模型训练'按钮")
    print("3. 查看浏览器开发者工具的网络请求")
    print("4. 检查Flask服务器的控制台日志")

if __name__ == "__main__":
    main()