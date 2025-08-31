#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能分析问题快速诊断
"""

import sys
import os
sys.path.insert(0, os.getcwd())

def quick_test():
    print("🔍 快速诊断智能分析问题")
    print("=" * 40)
    
    try:
        # 测试数据库连接
        from app import app, db, User
        print("✅ 数据库连接正常")
        
        with app.app_context():
            user_count = User.query.count()
            print(f"📊 用户数量: {user_count}")
            
            if user_count < 3:
                print("❌ 用户数量不足，至少需要3个用户")
                return
            
            # 测试ML模块
            from ml_services import LearningBehaviorClustering, AnomalyDetector
            print("✅ ML模块导入成功")
            
            # 测试聚类
            clustering = LearningBehaviorClustering()
            users = User.query.options(
                db.joinedload(User.synthesis_grades),
                db.joinedload(User.homework_statistic),
                db.joinedload(User.discussion_participation),
                db.joinedload(User.video_watching_details)
            ).all()
            
            if clustering.train_model(users):
                analysis = clustering.get_all_clusters_analysis(users)
                if analysis:
                    print("✅ 聚类分析正常")
                    print(f"   总用户: {analysis.get('total_users', 0)}")
                    print(f"   聚类数: {len(analysis.get('cluster_distribution', {}))}")
                else:
                    print("❌ 聚类分析结果为空")
            else:
                print("❌ 聚类训练失败")
            
            # 测试异常检测
            detector = AnomalyDetector()
            if detector.train_model(users):
                results = detector.batch_detect_anomalies(users)
                if results:
                    print("✅ 异常检测正常")
                    print(f"   总用户: {results.get('total_users', 0)}")
                    print(f"   异常用户: {results.get('anomaly_count', 0)}")
                else:
                    print("❌ 异常检测结果为空")
            else:
                print("❌ 异常检测训练失败")
                
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
    
    print("\n💡 解决步骤:")
    print("1. 重启Flask服务器: python app.py")
    print("2. 在前端点击'模型训练'按钮")
    print("3. 训练完成后点击'刷新分析'")
    print("4. 查看浏览器开发者工具的控制台")

if __name__ == "__main__":
    quick_test()