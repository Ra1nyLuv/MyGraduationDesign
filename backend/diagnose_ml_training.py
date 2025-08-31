#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ML模型训练失败诊断脚本
专门诊断"模型训练失败: 训练失败"问题
"""

import sys
import os
import traceback

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

def print_section(title):
    """打印章节标题"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def diagnose_imports():
    """诊断模块导入问题"""
    print_section("🔍 诊断模块导入")
    
    try:
        print("1️⃣ 测试基础ML库...")
        import numpy as np
        import pandas as pd
        import sklearn
        print("   ✅ 基础ML库导入正常")
        
        print("2️⃣ 测试ML服务模块导入...")
        from ml_services import GradePredictionModel, LearningBehaviorClustering, AnomalyDetector
        print("   ✅ ML服务模块导入正常")
        
        return True
    except Exception as e:
        print(f"   ❌ 导入失败: {str(e)}")
        print(f"   详细错误: {traceback.format_exc()}")
        return False

def diagnose_database_connection():
    """诊断数据库连接"""
    print_section("🗄️ 诊断数据库连接")
    
    try:
        print("1️⃣ 测试Flask应用上下文...")
        from app import app, db, User
        
        with app.app_context():
            print("   ✅ Flask应用上下文正常")
            
            print("2️⃣ 测试数据库查询...")
            user_count = User.query.count()
            print(f"   ✅ 数据库连接正常，用户数量: {user_count}")
            
            if user_count < 3:
                print(f"   ⚠️  用户数量不足：{user_count} < 3")
                return False
            
            return True
    except Exception as e:
        print(f"   ❌ 数据库连接失败: {str(e)}")
        print(f"   详细错误: {traceback.format_exc()}")
        return False

def diagnose_model_initialization():
    """诊断模型初始化"""
    print_section("🛠️ 诊断模型初始化")
    
    try:
        from ml_services import GradePredictionModel, LearningBehaviorClustering, AnomalyDetector
        
        print("1️⃣ 初始化预测模型...")
        predictor = GradePredictionModel()
        print(f"   ✅ 预测模型初始化成功 - 特征数: {len(predictor.feature_names)}")
        
        print("2️⃣ 初始化聚类模型...")
        clustering = LearningBehaviorClustering()
        print(f"   ✅ 聚类模型初始化成功 - 默认聚类数: {clustering.n_clusters}")
        
        print("3️⃣ 初始化异常检测模型...")
        detector = AnomalyDetector()
        print(f"   ✅ 异常检测初始化成功 - 异常比例: {detector.contamination}")
        
        return True
    except Exception as e:
        print(f"   ❌ 模型初始化失败: {str(e)}")
        print(f"   详细错误: {traceback.format_exc()}")
        return False

def diagnose_data_loading():
    """诊断数据加载"""
    print_section("📊 诊断数据加载")
    
    try:
        from app import app, db, User
        
        with app.app_context():
            print("1️⃣ 加载用户数据...")
            users = User.query.options(
                db.joinedload(User.synthesis_grades),
                db.joinedload(User.homework_statistic),
                db.joinedload(User.discussion_participation),
                db.joinedload(User.video_watching_details)
            ).all()
            
            print(f"   ✅ 成功加载 {len(users)} 个用户")
            
            if len(users) < 3:
                print(f"   ❌ 用户数量不足: {len(users)} < 3")
                return False
            
            print("2️⃣ 检查用户数据完整性...")
            complete_users = 0
            for user in users[:5]:  # 检查前5个用户
                has_synthesis = bool(user.synthesis_grades)
                has_homework = bool(user.homework_statistic)
                has_discussion = bool(user.discussion_participation)
                has_video = bool(user.video_watching_details)
                
                if has_synthesis:
                    complete_users += 1
                    
                print(f"   用户 {user.id}: 综合={has_synthesis}, 作业={has_homework}, 讨论={has_discussion}, 视频={has_video}")
            
            print(f"   ✅ 有完整数据的用户: {complete_users}")
            return True
            
    except Exception as e:
        print(f"   ❌ 数据加载失败: {str(e)}")
        print(f"   详细错误: {traceback.format_exc()}")
        return False

def diagnose_training_process():
    """诊断训练过程"""
    print_section("🎯 诊断训练过程")
    
    try:
        from app import app, db, User
        from ml_services import GradePredictionModel, LearningBehaviorClustering, AnomalyDetector
        
        with app.app_context():
            users = User.query.options(
                db.joinedload(User.synthesis_grades),
                db.joinedload(User.homework_statistic),
                db.joinedload(User.discussion_participation),
                db.joinedload(User.video_watching_details)
            ).all()
            
            if len(users) < 3:
                print(f"   ❌ 用户数量不足: {len(users)} < 3")
                return False
            
            results = {
                'prediction_model': False,
                'clustering_model': False, 
                'anomaly_model': False
            }
            
            # 测试预测模型训练
            print("1️⃣ 测试预测模型训练...")
            try:
                predictor = GradePredictionModel()
                results['prediction_model'] = predictor.train_model(users)
                print(f"   预测模型训练结果: {'✅ 成功' if results['prediction_model'] else '❌ 失败'}")
            except Exception as e:
                print(f"   ❌ 预测模型训练异常: {str(e)}")
                print(f"   详细错误: {traceback.format_exc()}")
            
            # 测试聚类模型训练
            print("2️⃣ 测试聚类模型训练...")
            try:
                clustering = LearningBehaviorClustering()
                results['clustering_model'] = clustering.train_model(users)
                print(f"   聚类模型训练结果: {'✅ 成功' if results['clustering_model'] else '❌ 失败'}")
            except Exception as e:
                print(f"   ❌ 聚类模型训练异常: {str(e)}")
                print(f"   详细错误: {traceback.format_exc()}")
            
            # 测试异常检测模型训练
            print("3️⃣ 测试异常检测模型训练...")
            try:
                detector = AnomalyDetector()
                results['anomaly_model'] = detector.train_model(users)
                print(f"   异常检测训练结果: {'✅ 成功' if results['anomaly_model'] else '❌ 失败'}")
            except Exception as e:
                print(f"   ❌ 异常检测训练异常: {str(e)}")
                print(f"   详细错误: {traceback.format_exc()}")
            
            success_count = sum(results.values())
            print(f"\n   📊 训练结果统计: {success_count}/3 个模型训练成功")
            
            return success_count > 0
            
    except Exception as e:
        print(f"   ❌ 训练过程诊断失败: {str(e)}")
        print(f"   详细错误: {traceback.format_exc()}")
        return False

def main():
    """主诊断函数"""
    print_section("🩺 ML模型训练失败诊断工具")
    print("正在诊断'模型训练失败: 训练失败'问题...")
    
    # 诊断步骤
    tests = [
        ("模块导入", diagnose_imports),
        ("数据库连接", diagnose_database_connection),
        ("模型初始化", diagnose_model_initialization),
        ("数据加载", diagnose_data_loading),
        ("训练过程", diagnose_training_process)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"\n✅ {test_name} 诊断通过")
            else:
                print(f"\n❌ {test_name} 诊断失败")
                break  # 遇到失败就停止，这样更容易定位问题
        except Exception as e:
            print(f"\n💥 {test_name} 诊断异常: {str(e)}")
            break
    
    # 输出诊断结果
    print_section("📋 诊断结果总结")
    print(f"诊断进度: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有诊断通过！ML训练应该可以正常工作")
        print("\n💡 可能的解决方案:")
        print("   1. 重启Flask服务器")
        print("   2. 清空浏览器缓存")
        print("   3. 检查前端调用是否正确")
    else:
        print(f"\n⚠️  发现问题在第 {passed + 1} 步: {tests[passed][0]}")
        print("\n🔧 建议的修复步骤:")
        
        if passed == 0:
            print("   - 检查ML库安装: pip install scikit-learn numpy pandas")
            print("   - 检查ml_services目录和文件")
        elif passed == 1:
            print("   - 检查数据库连接配置")
            print("   - 确保数据库服务正在运行")
        elif passed == 2:
            print("   - 检查模型类定义")
            print("   - 查看具体的初始化错误")
        elif passed == 3:
            print("   - 检查数据库中是否有足够的用户数据")
            print("   - 至少需要3个用户才能进行训练")
        elif passed == 4:
            print("   - 查看具体的训练错误信息")
            print("   - 检查数据格式和完整性")
    
    print(f"\n{'='*60}")

if __name__ == "__main__":
    main()