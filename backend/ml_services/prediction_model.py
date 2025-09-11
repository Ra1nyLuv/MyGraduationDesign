"""
学习成绩预测模型
基于历史学习数据预测学生的期末成绩
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.linear_model import Ridge
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import RobustScaler
import joblib
import os
import logging

class GradePredictionModel:
    def __init__(self):
        # 自适应模型选择
        self.model = None
        self.scaler = RobustScaler()  # 更鲁棒的缩放器
        self.is_trained = False
        self.data_size = 'unknown'
        self.feature_names = [
            'homework_avg', 'homework_completion_rate', 'homework_consistency',
            'discussion_activity', 'upvotes_ratio', 'video_engagement',
            'learning_consistency', 'base_performance'
        ]
        
    def prepare_features(self, users):
        """优化的特征准备"""
        features = []
        targets = []
        
        for user in users:
            try:
                # 1. 作业特征（更鲁棒的处理）
                homework = user.homework_statistic[0] if user.homework_statistic else None
                if homework:
                    scores = [getattr(homework, f'score{i}', 0) or 0 for i in range(2, 10)]
                    valid_scores = [s for s in scores if s > 0]
                    
                    homework_avg = np.mean(valid_scores) if valid_scores else 50  # 默认值
                    homework_completion_rate = len(valid_scores) / len(scores)
                    
                    # 作业一致性（新特征）
                    if len(valid_scores) > 2:
                        homework_consistency = 1.0 / (1.0 + np.std(valid_scores) / (np.mean(valid_scores) + 1e-6))
                    else:
                        homework_consistency = 0.5
                else:
                    homework_avg = 50
                    homework_completion_rate = 0
                    homework_consistency = 0.5
                
                # 2. 讨论特征（合并处理）
                discussion = user.discussion_participation[0] if user.discussion_participation else None
                if discussion:
                    posts = discussion.posted_discussions or 0
                    replies = discussion.replied_discussions or 0
                    upvotes = discussion.upvotes_received or 0
                    
                    discussion_activity = posts + replies
                    upvotes_ratio = upvotes / max(discussion_activity, 1) if discussion_activity > 0 else 0
                else:
                    discussion_activity = 0
                    upvotes_ratio = 0
                
                # 3. 视频学习特征（综合指标）
                video = user.video_watching_details[0] if user.video_watching_details else None
                if video:
                    watch_times = [getattr(video, f'watch_duration{i}', 0) or 0 for i in range(1, 8)]
                    rumination_ratios = [getattr(video, f'rumination_ratio{i}', 0) or 0 for i in range(1, 8)]
                    
                    total_watch_time = sum(watch_times)
                    avg_rumination = np.mean([r for r in rumination_ratios if r > 0]) if any(r > 0 for r in rumination_ratios) else 0
                    
                    # 视频投入度 = 观看时间 - 重复观看惩罚
                    video_engagement = total_watch_time * (1 - min(avg_rumination, 0.5))
                else:
                    video_engagement = 0
                
                # 4. 学习一致性指标（新特征）
                learning_consistency = (
                    homework_consistency * 0.4 + 
                    min(homework_completion_rate, 1.0) * 0.3 + 
                    min(discussion_activity / 10, 1.0) * 0.3
                )
                
                # 5. 基础表现指标
                synthesis = user.synthesis_grades[0] if user.synthesis_grades else None
                if synthesis:
                    base_performance = synthesis.course_points or homework_avg
                    target = synthesis.comprehensive_score
                else:
                    base_performance = homework_avg
                    target = 0
                
                # 只包含有效目标的数据
                if target > 0:
                    features.append([
                        homework_avg,
                        homework_completion_rate,
                        homework_consistency,
                        discussion_activity,
                        upvotes_ratio,
                        video_engagement,
                        learning_consistency,
                        base_performance
                    ])
                    targets.append(target)
                    
            except Exception as e:
                logging.warning(f"处理用户 {user.id} 数据时出错: {str(e)}")
                continue
        
        return np.array(features), np.array(targets)
    
    def train_model(self, users):
        """优化的模型训练"""
        try:
            features, targets = self.prepare_features(users)
            
            if len(features) < 3:
                logging.warning(f"训练数据不足，当前有{len(features)}个有效样本，至少需要3个样本")
                return False
            
            # 自适应模型选择
            if len(features) < 15:
                self.data_size = 'small'
                self.model = Ridge(alpha=1.0)  # 小数据集使用岭回归
                min_samples = 3
                logging.info("使用小数据集模式：岭回归")
            elif len(features) < 50:
                self.data_size = 'medium'
                self.model = DecisionTreeRegressor(max_depth=5, random_state=42)
                min_samples = 5
                logging.info("使用中型数据集模式：决策树")
            else:
                self.data_size = 'large'
                self.model = RandomForestRegressor(n_estimators=50, max_depth=10, random_state=42)
                min_samples = 10
                logging.info("使用大型数据集模式：随机森林")
            
            # 处理异常值
            features = self._handle_outliers(features)
            
            # 数据标准化
            features_scaled = self.scaler.fit_transform(features)
            
            # 模型训练
            if len(features) >= 10:
                # 使用交叉验证
                cv_scores = cross_val_score(self.model, features_scaled, targets, cv=min(5, len(features)//2))
                logging.info(f"交叉验证得分: {np.mean(cv_scores):.3f} (+/- {np.std(cv_scores) * 2:.3f})")
                
                # 训练最终模型
                self.model.fit(features_scaled, targets)
            else:
                # 小数据集直接训练
                self.model.fit(features_scaled, targets)
                
                # 简单验证
                y_pred = self.model.predict(features_scaled)
                mse = mean_squared_error(targets, y_pred)
                r2 = r2_score(targets, y_pred)
                logging.info(f"小数据集训练完成 - MSE: {mse:.2f}, R2: {r2:.3f}")
            
            self.is_trained = True
            return True
            
        except Exception as e:
            logging.error(f"模型训练失败: {str(e)}")
            return False
    
    def _handle_outliers(self, features):
        """处理异常值"""
        features_clean = features.copy()
        
        for i in range(features.shape[1]):
            col = features[:, i]
            Q1 = np.percentile(col, 25)
            Q3 = np.percentile(col, 75)
            IQR = Q3 - Q1
            
            if IQR > 0:  # 避免除零错误
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                # 截断异常值而不是删除
                features_clean[:, i] = np.clip(col, lower_bound, upper_bound)
        
        return features_clean
    
    def predict_grade(self, user):
        """预测单个用户的成绩"""
        if not self.is_trained:
            return None
            
        try:
            features, _ = self.prepare_features([user])
            if len(features) == 0:
                return None
                
            features_scaled = self.scaler.transform(features)
            prediction = self.model.predict(features_scaled)[0]
            
            # 计算置信度
            confidence = self._calculate_confidence(features[0])
            
            # 获取特征重要性
            feature_importance = self._get_feature_importance()
            
            return {
                'predicted_score': max(0, min(100, float(prediction))),  # 限制在合理范围
                'confidence': confidence,
                'feature_importance': feature_importance,
                'recommendations': self._generate_recommendations(features[0])
            }
            
        except Exception as e:
            logging.error(f"预测失败: {str(e)}")
            return None
    
    def _calculate_confidence(self, features):
        """计算预测置信度"""
        # 基于特征完整性计算置信度
        completeness = sum(1 for f in features if f > 0) / len(features)
        
        if completeness > 0.8:
            return 'high'
        elif completeness > 0.5:
            return 'medium'
        else:
            return 'low'
    
    def _get_feature_importance(self):
        """获取特征重要性"""
        try:
            if hasattr(self.model, 'feature_importances_'):
                return dict(zip(self.feature_names, self.model.feature_importances_))
            elif hasattr(self.model, 'coef_'):
                # 对线性模型使用系数绝对值
                importances = np.abs(self.model.coef_)
                importances = importances / np.sum(importances)  # 归一化
                return dict(zip(self.feature_names, importances))
        except:
            pass
        return {}
    
    def _generate_recommendations(self, features):
        """生成个性化建议"""
        recommendations = []
        
        homework_avg, homework_completion_rate, homework_consistency = features[0], features[1], features[2]
        discussion_activity, upvotes_ratio, video_engagement = features[3], features[4], features[5]
        learning_consistency = features[6]
        
        # 作业相关建议
        if homework_completion_rate < 0.7:
            recommendations.append("提高作业完成率，争取完成所有作业")
        if homework_avg < 70:
            recommendations.append("加强基础知识学习，提高作业质量")
        if homework_consistency < 0.5:
            recommendations.append("保持稳定的学习节奏，避免成绩波动")
        
        # 讨论参与建议
        if discussion_activity < 3:
            recommendations.append("增加课程讨论参与度，多与同学交流")
        
        # 视频学习建议
        if video_engagement < 100:
            recommendations.append("增加视频学习时间，提高学习投入度")
        
        # 综合建议
        if learning_consistency < 0.6:
            recommendations.append("制定学习计划，保持学习的连续性")
        
        return recommendations[:4]  # 最多返回4条建议
    
    def save_model(self, filepath):
        """保存模型"""
        if self.is_trained:
            model_data = {
                'model': self.model,
                'scaler': self.scaler,
                'feature_names': self.feature_names
            }
            joblib.dump(model_data, filepath)
            return True
        return False
    
    def load_model(self, filepath):
        """加载模型"""
        try:
            if os.path.exists(filepath):
                model_data = joblib.load(filepath)
                self.model = model_data['model']
                self.scaler = model_data['scaler'] 
                self.feature_names = model_data['feature_names']
                self.is_trained = True
                return True
        except Exception as e:
            logging.error(f"模型加载失败: {str(e)}")
        return False