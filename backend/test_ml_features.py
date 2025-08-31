"""
机器学习功能测试脚本
测试各个ML模块的基本功能和API接口
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml_services import (
    GradePredictionModel,
    LearningBehaviorClustering,
    PersonalizedRecommendation,
    AnomalyDetector
)
import numpy as np
from datetime import datetime

class MockUser:
    """模拟用户数据类"""
    def __init__(self, user_id, name="Test User"):
        self.id = user_id
        self.name = name
        
        # 模拟综合成绩数据
        self.synthesis_grades = [MockSynthesisGrade()]
        
        # 模拟作业数据
        self.homework_statistic = [MockHomework()]
        
        # 模拟考试数据
        self.exam_statistic = [MockExam()]
        
        # 模拟讨论数据
        self.discussion_participation = [MockDiscussion()]
        
        # 模拟视频数据
        self.video_watching_details = [MockVideo()]

class MockSynthesisGrade:
    def __init__(self):
        self.comprehensive_score = np.random.uniform(60, 95)
        self.course_points = np.random.uniform(50, 90)

class MockHomework:
    def __init__(self):
        for i in range(2, 10):
            setattr(self, f'score{i}', np.random.uniform(0, 100) if np.random.random() > 0.1 else 0)

class MockExam:
    def __init__(self):
        self.score = np.random.uniform(50, 95)

class MockDiscussion:
    def __init__(self):
        self.total_discussions = np.random.randint(0, 30)
        self.posted_discussions = np.random.randint(0, self.total_discussions + 1)
        self.replied_discussions = np.random.randint(0, self.total_discussions + 1)
        self.replied_topics = np.random.randint(0, 15)
        self.upvotes_received = np.random.randint(0, 20)

class MockVideo:
    def __init__(self):
        for i in range(1, 8):
            setattr(self, f'watch_duration{i}', np.random.uniform(0, 120))
            setattr(self, f'rumination_ratio{i}', np.random.uniform(0, 0.5))

def test_grade_prediction():
    """测试成绩预测模型"""
    print("🔮 测试成绩预测模型...")
    
    try:
        predictor = GradePredictionModel()
        
        # 创建测试数据
        users = [MockUser(f"test_{i}") for i in range(20)]
        
        # 训练模型
        print("   训练模型...")
        success = predictor.train_model(users)
        
        if success:
            print("   ✅ 模型训练成功")
            
            # 测试预测
            test_user = MockUser("test_predict")
            prediction = predictor.predict_grade(test_user)
            
            if prediction:
                print(f"   ✅ 预测成功: {prediction}")
            else:
                print("   ❌ 预测失败")
        else:
            print("   ❌ 模型训练失败")
            
    except Exception as e:
        print(f"   ❌ 测试失败: {str(e)}")

def test_clustering():
    """测试聚类分析"""
    print("\n🎯 测试学习行为聚类...")
    
    try:
        clustering = LearningBehaviorClustering()
        
        # 创建测试数据
        users = [MockUser(f"test_{i}") for i in range(15)]
        
        # 训练模型
        print("   训练聚类模型...")
        success = clustering.train_model(users)
        
        if success:
            print("   ✅ 聚类训练成功")
            
            # 测试聚类预测
            test_user = MockUser("test_cluster")
            cluster_info = clustering.predict_cluster(test_user)
            
            if cluster_info:
                print(f"   ✅ 聚类预测成功: {cluster_info['cluster_name']}")
            else:
                print("   ❌ 聚类预测失败")
                
            # 测试批量分析
            batch_analysis = clustering.get_all_clusters_analysis(users[:10])
            if batch_analysis:
                print(f"   ✅ 批量分析成功: {len(batch_analysis)} 个聚类")
            else:
                print("   ❌ 批量分析失败")
        else:
            print("   ❌ 聚类训练失败")
            
    except Exception as e:
        print(f"   ❌ 测试失败: {str(e)}")

def test_recommendation():
    """测试个性化推荐"""
    print("\n🎁 测试个性化推荐系统...")
    
    try:
        recommender = PersonalizedRecommendation()
        
        # 创建测试用户
        test_user = MockUser("test_recommendation")
        
        # 测试推荐生成
        recommendations = recommender.generate_personalized_recommendations(test_user)
        
        if recommendations:
            print("   ✅ 推荐生成成功")
            print(f"   - 学习资源推荐: {len(recommendations.get('learning_resources', []))} 项")
            print(f"   - 学习策略推荐: {len(recommendations.get('study_strategies', []))} 项")
            print(f"   - 改进领域: {len(recommendations.get('improvement_areas', []))} 项")
        else:
            print("   ❌ 推荐生成失败")
            
    except Exception as e:
        print(f"   ❌ 测试失败: {str(e)}")

def test_anomaly_detection():
    """测试异常检测"""
    print("\n⚠️ 测试异常行为检测...")
    
    try:
        detector = AnomalyDetector()
        
        # 创建测试数据
        users = [MockUser(f"test_{i}") for i in range(15)]
        
        # 训练模型
        print("   训练异常检测模型...")
        success = detector.train_model(users)
        
        if success:
            print("   ✅ 异常检测训练成功")
            
            # 测试异常检测
            test_user = MockUser("test_anomaly")
            anomaly_result = detector.detect_anomalies(test_user)
            
            if anomaly_result:
                print(f"   ✅ 异常检测成功: {'检测到异常' if anomaly_result['is_anomaly'] else '无异常'}")
            else:
                print("   ❌ 异常检测失败")
                
            # 测试批量检测
            batch_result = detector.batch_detect_anomalies(users[:10])
            if batch_result:
                print(f"   ✅ 批量检测成功: {batch_result['anomaly_count']}/{batch_result['total_users']} 异常")
            else:
                print("   ❌ 批量检测失败")
        else:
            print("   ❌ 异常检测训练失败")
            
    except Exception as e:
        print(f"   ❌ 测试失败: {str(e)}")

def test_api_integration():
    """测试API集成"""
    print("\n🌐 测试API接口集成...")
    
    try:
        import requests
        
        base_url = "http://localhost:5000"
        
        # 测试端点可达性
        endpoints = [
            "/api/ml/predict-grade",
            "/api/ml/cluster-analysis", 
            "/api/ml/recommendations",
            "/api/ml/anomaly-detection",
            "/api/ml/batch-cluster",
            "/api/ml/batch-anomaly",
            "/api/ml/train-models"
        ]
        
        for endpoint in endpoints:
            try:
                # 这里只测试端点是否存在，不测试具体功能
                response = requests.get(f"{base_url}{endpoint}", timeout=2)
                if response.status_code in [200, 401, 403]:  # 401/403 表示端点存在但需要认证
                    print(f"   ✅ {endpoint} 端点可达")
                else:
                    print(f"   ❓ {endpoint} 端点状态: {response.status_code}")
            except requests.exceptions.RequestException:
                print(f"   ❌ {endpoint} 端点不可达")
                
    except ImportError:
        print("   ⚠️ requests库未安装，跳过API测试")
    except Exception as e:
        print(f"   ❌ API测试失败: {str(e)}")

def run_ml_tests():
    """运行所有ML功能测试"""
    print("=" * 50)
    print("🚀 机器学习功能测试开始")
    print("=" * 50)
    
    start_time = datetime.now()
    
    # 运行各项测试
    test_grade_prediction()
    test_clustering()
    test_recommendation()
    test_anomaly_detection()
    test_api_integration()
    
    end_time = datetime.now()
    duration = end_time - start_time
    
    print("\n" + "=" * 50)
    print(f"✨ 测试完成，耗时: {duration.total_seconds():.2f} 秒")
    print("=" * 50)

if __name__ == "__main__":
    run_ml_tests()