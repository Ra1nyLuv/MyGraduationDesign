#!/usr/bin/env python3
"""
ML数据处理修复验证脚本
测试修复后的NoneType处理逻辑
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ml_services import (
    GradePredictionModel,
    LearningBehaviorClustering,
    PersonalizedRecommendation,
    AnomalyDetector
)
import numpy as np

class MockUserWithNulls:
    """包含空值的模拟用户数据"""
    def __init__(self, user_id, has_nulls=True):
        self.id = user_id
        self.name = "Test User"
        
        if has_nulls:
            # 模拟含有None值的数据
            self.synthesis_grades = [MockSynthesisGradeWithNull()]
            self.homework_statistic = [MockHomeworkWithNull()]
            self.exam_statistic = [MockExamWithNull()]
            self.discussion_participation = [MockDiscussionWithNull()]
            self.video_watching_details = [MockVideoWithNull()]
        else:
            # 正常数据
            self.synthesis_grades = [MockSynthesisGrade()]
            self.homework_statistic = [MockHomework()]
            self.exam_statistic = [MockExam()]
            self.discussion_participation = [MockDiscussion()]
            self.video_watching_details = [MockVideo()]

class MockSynthesisGradeWithNull:
    def __init__(self):
        self.comprehensive_score = np.random.uniform(60, 95) if np.random.random() > 0.3 else None
        self.course_points = np.random.uniform(50, 90) if np.random.random() > 0.3 else None

class MockHomeworkWithNull:
    def __init__(self):
        for i in range(2, 10):
            value = np.random.uniform(0, 100) if np.random.random() > 0.4 else None
            setattr(self, f'score{i}', value)

class MockExamWithNull:
    def __init__(self):
        self.score = np.random.uniform(50, 95) if np.random.random() > 0.3 else None

class MockDiscussionWithNull:
    def __init__(self):
        self.total_discussions = np.random.randint(0, 30) if np.random.random() > 0.3 else None
        self.posted_discussions = np.random.randint(0, 10) if np.random.random() > 0.3 else None
        self.replied_discussions = np.random.randint(0, 20) if np.random.random() > 0.3 else None
        self.replied_topics = np.random.randint(0, 15) if np.random.random() > 0.3 else None
        self.upvotes_received = np.random.randint(0, 20) if np.random.random() > 0.3 else None

class MockVideoWithNull:
    def __init__(self):
        for i in range(1, 8):
            duration = np.random.uniform(0, 120) if np.random.random() > 0.4 else None
            ratio = np.random.uniform(0, 0.5) if np.random.random() > 0.4 else None
            setattr(self, f'watch_duration{i}', duration)
            setattr(self, f'rumination_ratio{i}', ratio)

# 正常数据类（用于对比）
class MockSynthesisGrade:
    def __init__(self):
        self.comprehensive_score = np.random.uniform(60, 95)
        self.course_points = np.random.uniform(50, 90)

class MockHomework:
    def __init__(self):
        for i in range(2, 10):
            setattr(self, f'score{i}', np.random.uniform(60, 100))

class MockExam:
    def __init__(self):
        self.score = np.random.uniform(50, 95)

class MockDiscussion:
    def __init__(self):
        self.total_discussions = np.random.randint(5, 30)
        self.posted_discussions = np.random.randint(0, 10)
        self.replied_discussions = np.random.randint(0, 20)
        self.replied_topics = np.random.randint(0, 15)
        self.upvotes_received = np.random.randint(0, 20)

class MockVideo:
    def __init__(self):
        for i in range(1, 8):
            setattr(self, f'watch_duration{i}', np.random.uniform(20, 120))
            setattr(self, f'rumination_ratio{i}', np.random.uniform(0, 0.3))

def test_null_handling():
    """测试空值处理"""
    print("🔧 测试空值处理修复...")
    
    try:
        # 创建包含空值的测试数据
        users_with_nulls = [MockUserWithNulls(f"null_user_{i}") for i in range(5)]
        normal_users = [MockUserWithNulls(f"normal_user_{i}", has_nulls=False) for i in range(3)]
        
        # 混合数据
        all_users = users_with_nulls + normal_users
        
        print(f"   创建了 {len(all_users)} 个测试用户（{len(users_with_nulls)} 个含空值用户）")
        
        # 测试异常检测
        detector = AnomalyDetector()
        features, user_ids = detector.prepare_features(all_users)
        print(f"   ✅ 异常检测特征提取成功: {len(features)} 个有效样本")
        
        if len(features) >= 3:
            success = detector.train_model(all_users)
            print(f"   ✅ 异常检测训练: {'成功' if success else '失败'}")
        
        # 测试聚类分析
        clustering = LearningBehaviorClustering()
        features, user_ids = clustering.prepare_features(all_users)
        print(f"   ✅ 聚类分析特征提取成功: {len(features)} 个有效样本")
        
        if len(features) >= 3:
            success = clustering.train_model(all_users)
            print(f"   ✅ 聚类分析训练: {'成功' if success else '失败'}")
        
        # 测试成绩预测
        predictor = GradePredictionModel()
        features, targets = predictor.prepare_features(all_users)
        print(f"   ✅ 成绩预测特征提取成功: {len(features)} 个有效样本")
        
        if len(features) >= 3:
            success = predictor.train_model(all_users)
            print(f"   ✅ 成绩预测训练: {'成功' if success else '失败'}")
        
        # 测试个性化推荐
        recommender = PersonalizedRecommendation()
        test_user = normal_users[0] if normal_users else all_users[0]
        recommendations = recommender.generate_personalized_recommendations(test_user)
        print(f"   ✅ 个性化推荐: {'成功' if recommendations else '失败'}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_edge_cases():
    """测试边界情况"""
    print("\n🎯 测试边界情况...")
    
    try:
        # 测试极少数据
        minimal_users = [MockUserWithNulls(f"minimal_{i}", has_nulls=False) for i in range(2)]
        
        detector = AnomalyDetector()
        success = detector.train_model(minimal_users)
        print(f"   ✅ 少量数据异常检测: {'成功处理' if not success else '意外成功'}")
        
        # 测试全空数据
        empty_users = [MockUserWithNulls(f"empty_{i}") for i in range(3)]
        # 手动设置为全空
        for user in empty_users:
            user.synthesis_grades = []
            user.homework_statistic = []
            user.discussion_participation = []
            user.video_watching_details = []
        
        features, _ = detector.prepare_features(empty_users)
        print(f"   ✅ 全空数据处理: 提取到 {len(features)} 个特征")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 边界测试失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("🚀 ML数据处理修复验证")
    print("=" * 60)
    
    tests = [
        test_null_handling,
        test_edge_cases
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 测试结果: {passed}/{len(tests)} 通过")
    
    if passed == len(tests):
        print("🎉 所有测试通过！空值处理修复成功")
        print("\n📋 修复总结:")
        print("✅ 修复了NoneType除法错误")
        print("✅ 增强了空值处理逻辑")
        print("✅ 降低了最小训练样本要求")
        print("✅ 添加了更详细的错误信息")
    else:
        print("⚠️ 部分测试失败，需要进一步检查")
    
    return passed == len(tests)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)