"""
学习成绩预测模型
基于历史学习数据预测学生的期末成绩
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
import joblib
import os
import logging

class GradePredictionModel:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_names = [
            'homework_avg', 'homework_completion_rate', 'discussion_posts',
            'discussion_replies', 'upvotes_received', 'video_watch_time',
            'video_rumination_avg', 'course_points'
        ]
        
    def prepare_features(self, users):
        """准备特征数据"""
        features = []
        targets = []
        
        for user in users:
            try:
                # 作业相关特征
                homework = user.homework_statistic[0] if user.homework_statistic else None
                if homework:
                    scores = [
                        getattr(homework, f'score{i}', 0) for i in range(2, 10)
                    ]
                    homework_avg = np.mean([s for s in scores if s > 0]) if any(s > 0 for s in scores) else 0
                    homework_completion_rate = sum(1 for s in scores if s > 0) / len(scores)
                else:
                    homework_avg = 0
                    homework_completion_rate = 0
                
                # 讨论相关特征
                discussion = user.discussion_participation[0] if user.discussion_participation else None
                discussion_posts = discussion.posted_discussions if discussion else 0
                discussion_replies = discussion.replied_discussions if discussion else 0
                upvotes_received = discussion.upvotes_received if discussion else 0
                
                # 处理空值
                discussion_posts = discussion_posts or 0
                discussion_replies = discussion_replies or 0
                upvotes_received = upvotes_received or 0
                
                # 视频学习特征
                video = user.video_watching_details[0] if user.video_watching_details else None
                if video:
                    watch_times = [
                        getattr(video, f'watch_duration{i}', 0) for i in range(1, 8)
                    ]
                    rumination_ratios = [
                        getattr(video, f'rumination_ratio{i}', 0) for i in range(1, 8)
                    ]
                    video_watch_time = sum(watch_times)
                    video_rumination_avg = np.mean([r for r in rumination_ratios if r > 0]) if any(r > 0 for r in rumination_ratios) else 0
                else:
                    video_watch_time = 0
                    video_rumination_avg = 0
                
                # 课程积分
                synthesis = user.synthesis_grades[0] if user.synthesis_grades else None
                course_points = synthesis.course_points if synthesis else 0
                
                # 目标变量（综合成绩）
                target = synthesis.comprehensive_score if synthesis else 0
                
                if target > 0:  # 只包含有效的目标数据
                    features.append([
                        homework_avg, homework_completion_rate, discussion_posts,
                        discussion_replies, upvotes_received, video_watch_time,
                        video_rumination_avg, course_points
                    ])
                    targets.append(target)
                    
            except Exception as e:
                logging.warning(f"处理用户 {user.id} 数据时出错: {str(e)}")
                continue
        
        return np.array(features), np.array(targets)
    
    def train_model(self, users):
        """训练预测模型"""
        try:
            features, targets = self.prepare_features(users)
            
            if len(features) < 3:
                logging.warning(f"训练数据不足，当前有{len(features)}个有效样本，至少需要3个样本")
                return False
            
            # 数据标准化
            features_scaled = self.scaler.fit_transform(features)
            
            # 如果数据足够，进行训练验证分割
            if len(features) >= 10:
                X_train, X_test, y_train, y_test = train_test_split(
                    features_scaled, targets, test_size=0.2, random_state=42
                )
                
                # 训练模型
                self.model.fit(X_train, y_train)
                
                # 验证模型
                y_pred = self.model.predict(X_test)
                mse = mean_squared_error(y_test, y_pred)
                r2 = r2_score(y_test, y_pred)
                
                logging.info(f"模型训练完成 - MSE: {mse:.2f}, R2: {r2:.2f}")
            else:
                # 数据较少时，使用全部数据训练
                self.model.fit(features_scaled, targets)
                logging.info("模型训练完成（小数据集）")
            
            self.is_trained = True
            return True
            
        except Exception as e:
            logging.error(f"模型训练失败: {str(e)}")
            return False
    
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
            
            # 获取特征重要性
            feature_importance = dict(zip(self.feature_names, self.model.feature_importances_))
            
            return {
                'predicted_score': float(prediction),
                'confidence': 'high' if len(features) > 0 else 'low',
                'feature_importance': feature_importance,
                'recommendations': self._generate_recommendations(features[0], feature_importance)
            }
            
        except Exception as e:
            logging.error(f"预测失败: {str(e)}")
            return None
    
    def _generate_recommendations(self, features, importance):
        """根据特征重要性生成建议"""
        recommendations = []
        
        # 作业完成率建议
        if features[1] < 0.8:  # homework_completion_rate
            recommendations.append("建议提高作业完成率，按时提交所有作业")
        
        # 讨论参与建议  
        if features[2] + features[3] < 5:  # discussion_posts + replies
            recommendations.append("建议更积极参与课程讨论，提高互动频率")
        
        # 视频学习建议
        if features[5] < 60:  # video_watch_time
            recommendations.append("建议增加视频学习时间，深入理解课程内容")
        
        return recommendations
    
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