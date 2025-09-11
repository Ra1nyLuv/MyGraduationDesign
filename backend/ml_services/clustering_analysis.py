"""
学习行为聚类分析
基于学习行为数据对学生进行聚类分析，识别不同的学习模式
"""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import RobustScaler
from sklearn.metrics import silhouette_score
import joblib
import logging

class LearningBehaviorClustering:
    def __init__(self, n_clusters=3):
        self.n_clusters = n_clusters
        self.model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        self.scaler = RobustScaler()  # 更鲁棒的缩放器
        self.is_trained = False
        self.data_size = 'unknown'
        self.cluster_labels = {
            0: "高效学习型",
            1: "稳步学习型", 
            2: "需要帮助型",
            3: "观望学习型"
        }
        self.feature_names = [
            'learning_ability', 'completion_rate', 'engagement_level',
            'investment_degree', 'consistency_score', 'academic_performance'
        ]
        
    def prepare_features(self, users):
        """优化的聚类特征准备"""
        features = []
        user_ids = []
        
        for user in users:
            try:
                # 1. 学习能力指标（基于作业表现）
                homework = user.homework_statistic[0] if user.homework_statistic else None
                if homework:
                    scores = [getattr(homework, f'score{i}', 0) or 0 for i in range(2, 10)]
                    valid_scores = [s for s in scores if s > 0]
                    learning_ability = np.mean(valid_scores) if valid_scores else 50
                    completion_rate = len(valid_scores) / len(scores)
                else:
                    learning_ability = 50
                    completion_rate = 0
                
                # 2. 参与度指标（综合讨论和互动）
                discussion = user.discussion_participation[0] if user.discussion_participation else None
                if discussion:
                    posted = discussion.posted_discussions or 0
                    replied = discussion.replied_discussions or 0
                    upvotes = discussion.upvotes_received or 0
                    engagement_level = posted * 2 + replied * 1 + upvotes * 0.5
                else:
                    engagement_level = 0
                
                # 3. 学习投入度（视频学习时间）
                video = user.video_watching_details[0] if user.video_watching_details else None
                if video:
                    watch_times = [getattr(video, f'watch_duration{i}', 0) or 0 for i in range(1, 8)]
                    rumination_ratios = [getattr(video, f'rumination_ratio{i}', 0) or 0 for i in range(1, 8)]
                    
                    total_watch_time = sum(watch_times)
                    avg_rumination = np.mean([r for r in rumination_ratios if r > 0]) if any(r > 0 for r in rumination_ratios) else 0
                    
                    # 投入度 = 观看时间 - 重复观看
                    investment_degree = total_watch_time * (1 - min(avg_rumination * 0.5, 0.3))
                else:
                    investment_degree = 0
                
                # 4. 一致性得分（学习稳定性）
                if homework and len(valid_scores) > 2:
                    score_std = np.std(valid_scores)
                    score_mean = np.mean(valid_scores)
                    consistency_score = 1.0 / (1.0 + score_std / (score_mean + 1e-6))
                else:
                    consistency_score = 0.5
                
                # 5. 学术表现
                synthesis = user.synthesis_grades[0] if user.synthesis_grades else None
                academic_performance = synthesis.comprehensive_score if synthesis else learning_ability
                
                features.append([
                    learning_ability,      # 学习能力
                    completion_rate * 100, # 完成率（百分比）
                    engagement_level,      # 参与度
                    investment_degree,     # 投入度
                    consistency_score * 100, # 一致性（百分比）
                    academic_performance   # 学术表现
                ])
                user_ids.append(user.id)
                
            except Exception as e:
                logging.warning(f"处理用户 {user.id} 聚类特征时出错: {str(e)}")
                continue
        
        return np.array(features), user_ids
    
    def train_model(self, users):
        """优化的聚类模型训练"""
        try:
            features, user_ids = self.prepare_features(users)
            
            if len(features) < 3:
                logging.warning(f"聚类数据不足: {len(features)}个样本")
                return False
            
            # 自适应调整聚类数
            if len(features) < 10:
                optimal_clusters = min(2, len(features))
                self.data_size = 'small'
            elif len(features) < 30:
                optimal_clusters = min(3, len(features))
                self.data_size = 'medium'
            else:
                optimal_clusters = min(4, len(features))
                self.data_size = 'large'
            
            if optimal_clusters != self.n_clusters:
                self.n_clusters = optimal_clusters
                self.model = KMeans(n_clusters=self.n_clusters, random_state=42, n_init=10)
                logging.info(f"自动调整聚类数为: {self.n_clusters}")
            
            # 处理异常值
            features = self._handle_outliers(features)
            
            # 特征缩放
            features_scaled = self.scaler.fit_transform(features)
            
            # 训练聚类模型
            self.model.fit(features_scaled)
            
            # 评估聚类效果
            if len(features) > self.n_clusters:
                silhouette_avg = silhouette_score(features_scaled, self.model.labels_)
                logging.info(f"聚类完成 - 轮廓系数: {silhouette_avg:.3f}")
            
            self.is_trained = True
            
            # 分析各聚类特征
            self._analyze_clusters(features_scaled, self.model.labels_, user_ids)
            
            return True
            
        except Exception as e:
            logging.error(f"聚类训练失败: {str(e)}")
            return False
    
    def _handle_outliers(self, features):
        """处理异常值"""
        features_clean = features.copy()
        
        for i in range(features.shape[1]):
            col = features[:, i]
            Q1 = np.percentile(col, 25)
            Q3 = np.percentile(col, 75)
            IQR = Q3 - Q1
            
            if IQR > 0:
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                # 截断异常值
                features_clean[:, i] = np.clip(col, lower_bound, upper_bound)
        
        return features_clean
    
    def _analyze_clusters(self, features, labels, user_ids):
        """分析各聚类的特征"""
        self.cluster_analysis = {}
        
        for cluster_id in range(self.n_clusters):
            cluster_mask = labels == cluster_id
            cluster_features = features[cluster_mask]
            cluster_users = [user_ids[i] for i in range(len(user_ids)) if cluster_mask[i]]
            
            if len(cluster_features) > 0:
                cluster_center = np.mean(cluster_features, axis=0)
                
                self.cluster_analysis[cluster_id] = {
                    'name': self.cluster_labels.get(cluster_id, f"聚类{cluster_id}"),
                    'user_count': len(cluster_users),
                    'users': cluster_users,
                    'center': cluster_center.tolist(),
                    'characteristics': self._describe_cluster(cluster_center)
                }
    
    def _describe_cluster(self, center):
        """描述聚类特征"""
        characteristics = []
        
        # 作业表现
        if center[0] > 0.8:  # homework_avg
            characteristics.append("作业成绩优秀")
        elif center[0] > 0.6:
            characteristics.append("作业成绩良好")
        else:
            characteristics.append("作业成绩有待提高")
        
        # 完成率
        if center[1] > 0.9:  # homework_completion_rate
            characteristics.append("作业完成率高")
        elif center[1] > 0.7:
            characteristics.append("作业完成率中等")
        else:
            characteristics.append("作业完成率低")
        
        # 讨论活跃度
        if center[2] > 10:  # discussion_activity
            characteristics.append("讨论非常活跃")
        elif center[2] > 5:
            characteristics.append("讨论较为活跃")
        else:
            characteristics.append("讨论参与度低")
        
        # 视频投入度
        if center[3] > 200:  # video_engagement
            characteristics.append("视频学习投入度高")
        elif center[3] > 100:
            characteristics.append("视频学习投入度中等")
        else:
            characteristics.append("视频学习投入度低")
        
        return characteristics
    
    def predict_cluster(self, user):
        """预测单个用户的聚类"""
        if not self.is_trained:
            return None
            
        try:
            features, _ = self.prepare_features([user])
            if len(features) == 0:
                return None
                
            features_scaled = self.scaler.transform(features)
            cluster_id = self.model.predict(features_scaled)[0]
            
            result = {
                'cluster_id': int(cluster_id),
                'cluster_name': self.cluster_labels.get(int(cluster_id), f"聚类{cluster_id}"),
                'features': features[0].tolist(),
                'recommendations': self._generate_cluster_recommendations(int(cluster_id))
            }
            
            if hasattr(self, 'cluster_analysis') and cluster_id in self.cluster_analysis:
                result['characteristics'] = self.cluster_analysis[cluster_id]['characteristics']
            
            return result
            
        except Exception as e:
            logging.error(f"聚类预测失败: {str(e)}")
            return None
    
    def _generate_cluster_recommendations(self, cluster_id):
        """根据聚类结果生成建议"""
        recommendations = {
            0: [  # 积极学习型
                "继续保持优秀的学习习惯",
                "可以尝试帮助其他同学学习",
                "挑战更高难度的学习内容"
            ],
            1: [  # 稳定学习型
                "保持当前的学习节奏",
                "可以增加一些课外拓展学习",
                "尝试更多的课程讨论参与"
            ],
            2: [  # 需要帮助型
                "建议寻求老师或同学的帮助",
                "制定更详细的学习计划",
                "重点关注作业完成质量"
            ],
            3: [  # 观望学习型
                "建议更积极地参与课程活动",
                "增加视频学习时间",
                "主动参与课程讨论"
            ]
        }
        
        return recommendations.get(cluster_id, ["继续努力学习"])
    
    def get_all_clusters_analysis(self, users):
        """获取所有聚类的分析结果"""
        if not self.is_trained:
            return None
            
        try:
            features, user_ids = self.prepare_features(users)
            features_scaled = self.scaler.transform(features)
            predictions = self.model.predict(features_scaled)
            
            # 统计各聚类的用户分布
            cluster_distribution = {}
            for cluster_id in range(self.n_clusters):
                cluster_users = [user_ids[i] for i in range(len(user_ids)) if predictions[i] == cluster_id]
                cluster_distribution[cluster_id] = {
                    'name': self.cluster_labels.get(cluster_id, f"聚类{cluster_id}"),
                    'count': len(cluster_users),
                    'users': cluster_users,
                    'percentage': len(cluster_users) / len(user_ids) * 100 if len(user_ids) > 0 else 0
                }
            
            return {
                'total_users': len(user_ids),
                'cluster_distribution': cluster_distribution,
                'analysis': getattr(self, 'cluster_analysis', {})
            }
            
        except Exception as e:
            logging.error(f"聚类分析失败: {str(e)}")
            return None
    
    def save_model(self, filepath):
        """保存聚类模型"""
        if self.is_trained:
            model_data = {
                'model': self.model,
                'scaler': self.scaler,
                'cluster_labels': self.cluster_labels,
                'feature_names': self.feature_names,
                'cluster_analysis': getattr(self, 'cluster_analysis', {})
            }
            joblib.dump(model_data, filepath)
            return True
        return False
    
    def load_model(self, filepath):
        """加载聚类模型"""
        try:
            model_data = joblib.load(filepath)
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.cluster_labels = model_data['cluster_labels']
            self.feature_names = model_data['feature_names']
            self.cluster_analysis = model_data.get('cluster_analysis', {})
            self.is_trained = True
            return True
        except Exception as e:
            logging.error(f"聚类模型加载失败: {str(e)}")
            return False