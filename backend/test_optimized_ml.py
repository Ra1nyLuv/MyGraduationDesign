#!/usr/bin/env python3
"""
优化后ML算法测试脚本
验证针对实际数据优化的机器学习算法
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ml_services.prediction_model import GradePredictionModel
from ml_services.clustering_analysis import LearningBehaviorClustering
from ml_services.anomaly_detection import AnomalyDetector
from ml_services.recommendation_system import PersonalizedRecommendation
import numpy as np
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MockOptimizedUser:
    """优化的模拟用户数据"""
    def __init__(self, user_id, scenario='normal'):
        self.id = user_id
        self.name = f"Test User {user_id}"
        
        if scenario == 'normal':
            # 正常学生
            self.synthesis_grades = [MockSynthesisGrade(80)]
            self.homework_statistic = [MockHomework(scenario='good')]
            self.exam_statistic = [MockExam(75)]
            self.discussion_participation = [MockDiscussion(scenario='active')]
            self.video_watching_details = [MockVideo(scenario='engaged')]
        elif scenario == 'struggling':
            # 学习困难学生
            self.synthesis_grades = [MockSynthesisGrade(55)]
            self.homework_statistic = [MockHomework(scenario='poor')]
            self.exam_statistic = [MockExam(45)]
            self.discussion_participation = [MockDiscussion(scenario='passive')]
            self.video_watching_details = [MockVideo(scenario='minimal')]
        elif scenario == 'excellent':
            # 优秀学生
            self.synthesis_grades = [MockSynthesisGrade(95)]
            self.homework_statistic = [MockHomework(scenario='excellent')]
            self.exam_statistic = [MockExam(92)]
            self.discussion_participation = [MockDiscussion(scenario='very_active')]
            self.video_watching_details = [MockVideo(scenario='intensive')]
        else:
            # 有缺失数据的学生
            self.synthesis_grades = [MockSynthesisGrade(70)]
            self.homework_statistic = []
            self.exam_statistic = []
            self.discussion_participation = []
            self.video_watching_details = []

class MockSynthesisGrade:
    def __init__(self, score=75):
        self.comprehensive_score = score
        self.course_points = score * 0.8

class MockHomework:
    def __init__(self, scenario='normal'):
        if scenario == 'excellent':
            base_scores = [90, 92, 88, 94, 89, 91, 93, 87]
        elif scenario == 'good':
            base_scores = [78, 82, 75, 80, 77, 83, 79, 81]
        elif scenario == 'poor':
            base_scores = [45, 0, 52, 48, 0, 55, 50, 0]  # 有缺失
        else:
            base_scores = [70, 68, 72, 69, 71, 67, 73, 70]
        
        for i, score in enumerate(base_scores, 2):
            setattr(self, f'score{i}', score)

class MockExam:
    def __init__(self, score=70):
        self.score = score

class MockDiscussion:
    def __init__(self, scenario='normal'):
        if scenario == 'very_active':
            self.total_discussions = 25
            self.posted_discussions = 8
            self.replied_discussions = 15
            self.replied_topics = 12
            self.upvotes_received = 18
        elif scenario == 'active':
            self.total_discussions = 12
            self.posted_discussions = 3
            self.replied_discussions = 8
            self.replied_topics = 6
            self.upvotes_received = 7
        elif scenario == 'passive':
            self.total_discussions = 2
            self.posted_discussions = 0
            self.replied_discussions = 2
            self.replied_topics = 1
            self.upvotes_received = 1
        else:
            self.total_discussions = 5
            self.posted_discussions = 1
            self.replied_discussions = 4
            self.replied_topics = 3
            self.upvotes_received = 3

class MockVideo:
    def __init__(self, scenario='normal'):
        if scenario == 'intensive':
            watch_times = [120, 95, 110, 105, 88, 115, 98]
            rumination_ratios = [0.1, 0.15, 0.08, 0.12, 0.18, 0.09, 0.11]
        elif scenario == 'engaged':
            watch_times = [85, 70, 78, 82, 65, 88, 75]
            rumination_ratios = [0.2, 0.25, 0.18, 0.22, 0.28, 0.19, 0.21]
        elif scenario == 'minimal':
            watch_times = [25, 0, 35, 20, 0, 30, 15]
            rumination_ratios = [0.4, 0.0, 0.45, 0.38, 0.0, 0.42, 0.35]
        else:
            watch_times = [60, 55, 65, 58, 50, 68, 62]
            rumination_ratios = [0.3, 0.28, 0.32, 0.29, 0.35, 0.27, 0.31]
        
        for i, (time, ratio) in enumerate(zip(watch_times, rumination_ratios), 1):
            setattr(self, f'watch_duration{i}', time)
            setattr(self, f'rumination_ratio{i}', ratio)

def test_optimized_prediction():
    """测试优化的预测模型"""
    print("\n🎯 测试优化预测模型...")
    
    try:
        # 创建测试数据
        users = [
            MockOptimizedUser("opt_001", "excellent"),
            MockOptimizedUser("opt_002", "normal"),
            MockOptimizedUser("opt_003", "normal"),
            MockOptimizedUser("opt_004", "struggling"),
            MockOptimizedUser("opt_005", "normal"),
            MockOptimizedUser("opt_006", "missing_data"),
            MockOptimizedUser("opt_007", "excellent"),
            MockOptimizedUser("opt_008", "struggling")
        ]
        
        # 初始化模型
        predictor = GradePredictionModel()
        
        # 测试特征准备
        features, targets = predictor.prepare_features(users)
        print(f"   ✅ 特征提取成功: {len(features)} 个样本, {features.shape[1]} 个特征")
        print(f"   📊 目标分布: 最小{min(targets):.1f}, 最大{max(targets):.1f}, 平均{np.mean(targets):.1f}")
        
        # 训练模型
        success = predictor.train_model(users)
        if success:
            print(f"   ✅ 模型训练成功 (数据规模: {predictor.data_size})")
            print(f"   🤖 选择的算法: {type(predictor.model).__name__}")
            
            # 测试预测
            test_user = users[0]  # 优秀学生
            prediction = predictor.predict_grade(test_user)
            if prediction:
                print(f"   🔮 预测测试: 预测分数={prediction['predicted_score']:.1f}, 置信度={prediction['confidence']}")
                print(f"   💡 建议数量: {len(prediction['recommendations'])}")
            else:
                print("   ❌ 预测失败")
        else:
            print("   ❌ 模型训练失败")
            
        return success
        
    except Exception as e:
        print(f"   ❌ 测试失败: {str(e)}")
        return False

def test_optimized_clustering():
    """测试优化的聚类模型"""
    print("\n🔍 测试优化聚类模型...")
    
    try:
        # 创建测试数据
        users = [
            MockOptimizedUser(f"clust_{i:03d}", scenario) 
            for i, scenario in enumerate([
                "excellent", "excellent", "normal", "normal", "normal",
                "struggling", "struggling", "missing_data", "normal", "excellent"
            ])
        ]
        
        # 初始化模型
        clustering = LearningBehaviorClustering()
        
        # 测试特征准备
        features, user_ids = clustering.prepare_features(users)
        print(f"   ✅ 聚类特征提取成功: {len(features)} 个样本")
        
        # 训练模型
        success = clustering.train_model(users)
        if success:
            print(f"   ✅ 聚类训练成功")
            print(f"   📊 聚类数: {clustering.n_clusters} (数据规模: {clustering.data_size})")
            
            if hasattr(clustering, 'cluster_analysis'):
                for cluster_id, analysis in clustering.cluster_analysis.items():
                    print(f"   🏷️ {analysis['name']}: {analysis['user_count']} 用户")
            
        else:
            print("   ❌ 聚类训练失败")
            
        return success
        
    except Exception as e:
        print(f"   ❌ 测试失败: {str(e)}")
        return False

def test_optimized_anomaly_detection():
    """测试优化的异常检测"""
    print("\n⚠️ 测试优化异常检测...")
    
    try:
        # 创建测试数据，包含明显的异常情况
        users = [
            MockOptimizedUser("anom_001", "normal"),
            MockOptimizedUser("anom_002", "normal"),
            MockOptimizedUser("anom_003", "excellent"),
            MockOptimizedUser("anom_004", "struggling"),  # 潜在异常
            MockOptimizedUser("anom_005", "normal"),
            MockOptimizedUser("anom_006", "missing_data"),  # 潜在异常
            MockOptimizedUser("anom_007", "normal"),
        ]
        
        # 初始化模型
        detector = AnomalyDetector()
        
        # 测试特征准备
        features, user_ids = detector.prepare_features(users)
        print(f"   ✅ 异常检测特征提取成功: {len(features)} 个样本")
        
        # 训练模型
        success = detector.train_model(users)
        if success:
            print(f"   ✅ 异常检测训练成功")
            print(f"   📊 数据规模: {detector.data_size}, 异常比例: {detector.contamination}")
            
            if hasattr(detector, 'anomaly_analysis'):
                analysis = detector.anomaly_analysis
                print(f"   🚨 检测结果: {analysis['anomaly_count']}/{analysis['total_users']} 个异常")
                print(f"   📈 异常率: {analysis['anomaly_rate']:.1f}%")
        else:
            print("   ❌ 异常检测训练失败")
            
        return success
        
    except Exception as e:
        print(f"   ❌ 测试失败: {str(e)}")
        return False

def test_small_dataset_handling():
    """测试小数据集处理能力"""
    print("\n📦 测试小数据集处理...")
    
    try:
        # 创建很小的数据集
        small_users = [
            MockOptimizedUser("small_001", "normal"),
            MockOptimizedUser("small_002", "excellent"),
            MockOptimizedUser("small_003", "struggling")
        ]
        
        # 测试预测模型
        predictor = GradePredictionModel()
        pred_success = predictor.train_model(small_users)
        print(f"   {'✅' if pred_success else '❌'} 小数据集预测: {'成功' if pred_success else '失败'}")
        
        # 测试聚类
        clustering = LearningBehaviorClustering()
        clust_success = clustering.train_model(small_users)
        print(f"   {'✅' if clust_success else '❌'} 小数据集聚类: {'成功' if clust_success else '失败'}")
        
        # 测试异常检测
        detector = AnomalyDetector()
        anom_success = detector.train_model(small_users)
        print(f"   {'✅' if anom_success else '❌'} 小数据集异常检测: {'成功' if anom_success else '失败'}")
        
        return pred_success and clust_success and anom_success
        
    except Exception as e:
        print(f"   ❌ 测试失败: {str(e)}")
        return False

def test_recommendation_compatibility():
    """测试推荐系统兼容性"""
    print("\n💡 测试推荐系统兼容性...")
    
    try:
        users = [MockOptimizedUser("rec_001", "normal")]
        recommender = PersonalizedRecommendation()
        
        recommendations = recommender.generate_personalized_recommendations(users[0])
        
        if recommendations:
            print("   ✅ 推荐系统正常工作")
            print(f"   📝 生成建议: {len(recommendations.get('learning_resources', []))} 个学习资源")
            return True
        else:
            print("   ❌ 推荐系统失败")
            return False
            
    except Exception as e:
        print(f"   ❌ 测试失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("🚀 优化ML算法测试")
    print("=" * 60)
    
    tests = [
        ("预测模型", test_optimized_prediction),
        ("聚类分析", test_optimized_clustering),
        ("异常检测", test_optimized_anomaly_detection),
        ("小数据集处理", test_small_dataset_handling),
        ("推荐系统兼容性", test_recommendation_compatibility)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} 测试通过")
            else:
                print(f"❌ {test_name} 测试失败")
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {str(e)}")
    
    print("\n" + "=" * 60)
    print(f"📊 测试结果: {passed}/{total} 通过 ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 所有测试通过！ML算法优化成功")
        print("\n💡 优化亮点:")
        print("   ✅ 自适应算法选择 (小数据集使用简单模型)")
        print("   ✅ 鲁棒特征工程 (处理空值和异常值)")
        print("   ✅ 动态参数调整 (根据数据量调整聚类数)")
        print("   ✅ 改进的异常检测 (适合小数据集的contamination)")
        print("   ✅ 增强的置信度评估")
    else:
        print("⚠️ 部分测试未通过，需要进一步调试")
    
    print("=" * 60)

if __name__ == "__main__":
    main()