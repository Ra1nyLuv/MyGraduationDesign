"""
机器学习服务模块
提供学习成绩预测、行为聚类、个性化推荐和异常检测功能
"""

from .prediction_model import GradePredictionModel
from .clustering_analysis import LearningBehaviorClustering
from .recommendation_system import PersonalizedRecommendation
from .anomaly_detection import AnomalyDetector

__all__ = [
    'GradePredictionModel',
    'LearningBehaviorClustering', 
    'PersonalizedRecommendation',
    'AnomalyDetector'
]