"""
异常行为检测
使用孤立森林算法检测学生的异常学习行为，帮助识别需要关注的学生
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import RobustScaler
from sklearn.metrics import classification_report
import joblib
import logging
from datetime import datetime

class AnomalyDetector:
    def __init__(self, contamination=0.2):
        """
        初始化异常检测器
        contamination: 异常比例，默认20%（适合小数据集）
        """
        self.contamination = contamination
        self.model = IsolationForest(contamination=contamination, random_state=42, n_estimators=50)
        self.scaler = RobustScaler()
        self.is_trained = False
        self.data_size = 'unknown'
        self.feature_names = [
            'performance_variability', 'completion_anomaly', 'engagement_anomaly',
            'learning_pattern_anomaly', 'academic_deviation', 'behavior_consistency'
        ]
        self.anomaly_types = {
            'low_engagement': '学习参与度过低',
            'irregular_pattern': '学习模式不规律',
            'poor_performance': '学习成绩异常偏低',
            'excessive_struggle': '学习困难程度异常',
            'inconsistent_behavior': '行为模式不一致'
        }
        
    def prepare_features(self, users):
        """准备异常检测特征"""
        features = []
        user_ids = []
        
        for user in users:
            try:
                # 作业相关特征
                homework = user.homework_statistic[0] if user.homework_statistic else None
                if homework:
                    scores = [getattr(homework, f'score{i}', 0) for i in range(2, 10)]
                    valid_scores = [s for s in scores if s > 0]
                    
                    homework_avg = np.mean(valid_scores) if valid_scores else 0
                    homework_completion_rate = len(valid_scores) / len(scores)
                    
                    # 作业一致性（波动程度）
                    if len(valid_scores) > 2:
                        homework_consistency = 1 / (1 + np.std(valid_scores) / (np.mean(valid_scores) + 1e-6))
                    else:
                        homework_consistency = 0
                else:
                    homework_avg = 0
                    homework_completion_rate = 0
                    homework_consistency = 0
                
                # 讨论参与特征
                discussion = user.discussion_participation[0] if user.discussion_participation else None
                if discussion:
                    discussion_posts = discussion.posted_discussions or 0
                    discussion_replies = discussion.replied_discussions or 0
                    total_discussions = discussion.total_discussions or 0
                    upvotes = discussion.upvotes_received or 0
                    
                    # 获赞率（质量指标）
                    total_activity = discussion_posts + discussion_replies
                    upvotes_ratio = upvotes / max(total_activity, 1) if total_activity > 0 else 0
                else:
                    discussion_posts = 0
                    discussion_replies = 0
                    upvotes = 0
                    upvotes_ratio = 0
                
                # 视频学习特征
                video = user.video_watching_details[0] if user.video_watching_details else None
                if video:
                    watch_times = [getattr(video, f'watch_duration{i}', 0) or 0 for i in range(1, 8)]
                    rumination_ratios = [getattr(video, f'rumination_ratio{i}', 0) or 0 for i in range(1, 8)]
                    
                    video_watch_time = sum(watch_times)
                    valid_ratios = [r for r in rumination_ratios if r > 0]
                    video_rumination_ratio = np.mean(valid_ratios) if valid_ratios else 0
                else:
                    video_watch_time = 0
                    video_rumination_ratio = 0
                
                # 学习模式得分（综合评估）
                learning_pattern_score = (
                    homework_completion_rate * 0.3 +
                    min(discussion_posts + discussion_replies, 20) / 20 * 0.3 +
                    min(video_watch_time, 500) / 500 * 0.4
                )
                
                # 学术表现
                synthesis = user.synthesis_grades[0] if user.synthesis_grades else None
                academic_performance = synthesis.comprehensive_score if synthesis else 0
                
                # 总体参与度得分
                engagement_score = (
                    homework_completion_rate * 0.4 +
                    min(discussion_posts + discussion_replies + (upvotes * 2), 30) / 30 * 0.3 +
                    min(video_watch_time, 400) / 400 * 0.3
                )
                
                features.append([
                    homework_avg, homework_completion_rate, homework_consistency,
                    discussion_posts, discussion_replies, upvotes_ratio,
                    video_watch_time, video_rumination_ratio, learning_pattern_score,
                    academic_performance, engagement_score
                ])
                user_ids.append(user.id)
                
            except Exception as e:
                logging.warning(f"处理用户 {user.id} 异常检测特征时出错: {str(e)}")
                continue
        
        return np.array(features), user_ids
    
    def train_model(self, users):
        """优化的异常检测模型训练"""
        try:
            features, user_ids = self.prepare_features(users)
            
            if len(features) < 3:
                logging.warning(f"异常检测数据不足，当前有{len(features)}个有效样本，至少需要3个样本")
                return False
            
            # 自适应调整参数
            if len(features) < 10:
                self.contamination = 0.3  # 小数据集提高异常比例
                self.model = IsolationForest(contamination=self.contamination, random_state=42, n_estimators=50)
                self.data_size = 'small'
                logging.info(f"小数据集模式：调整异常比例为{self.contamination}")
            elif len(features) < 30:
                self.contamination = 0.2
                self.model = IsolationForest(contamination=self.contamination, random_state=42, n_estimators=100)
                self.data_size = 'medium'
                logging.info(f"中型数据集模式：异常比例{self.contamination}")
            else:
                self.contamination = 0.1
                self.model = IsolationForest(contamination=self.contamination, random_state=42)
                self.data_size = 'large'
            
            # 处理异常值
            features = self._handle_outliers(features)
            
            # 数据标准化
            features_scaled = self.scaler.fit_transform(features)
            
            # 训练异常检测模型
            self.model.fit(features_scaled)
            
            # 获取异常得分和标签
            anomaly_scores = self.model.decision_function(features_scaled)
            anomaly_labels = self.model.predict(features_scaled)
            
            # 分析异常情况
            anomaly_count = sum(1 for label in anomaly_labels if label == -1)
            logging.info(f"异常检测训练完成 - 检测到 {anomaly_count}/{len(features)} 个异常样本")
            
            self.is_trained = True
            
            # 分析异常模式
            self._analyze_anomaly_patterns(features_scaled, anomaly_labels, user_ids, anomaly_scores)
            
            return True
            
        except Exception as e:
            logging.error(f"异常检测训练失败: {str(e)}")
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
                lower_bound = Q1 - 2.0 * IQR  # 放宽异常值范围
                upper_bound = Q3 + 2.0 * IQR
                
                # 不截断，保留异常值信息
                pass
        
        return features_clean
    
    def _analyze_anomaly_patterns(self, features, labels, user_ids, scores):
        """分析异常模式"""
        self.anomaly_analysis = {
            'total_users': len(user_ids),
            'anomaly_count': sum(1 for label in labels if label == -1),
            'normal_count': sum(1 for label in labels if label == 1),
            'anomaly_rate': sum(1 for label in labels if label == -1) / len(labels) * 100,
            'anomalies': []
        }
        
        for i, (user_id, label, score) in enumerate(zip(user_ids, labels, scores)):
            if label == -1:  # 异常样本
                anomaly_info = {
                    'user_id': user_id,
                    'anomaly_score': float(score),
                    'severity': self._get_anomaly_severity(score),
                    'anomaly_types': self._identify_anomaly_types(features[i]),
                    'features': features[i].tolist()
                }
                self.anomaly_analysis['anomalies'].append(anomaly_info)
        
        # 按异常程度排序
        self.anomaly_analysis['anomalies'].sort(key=lambda x: x['anomaly_score'])
    
    def _get_anomaly_severity(self, score):
        """确定异常严重程度"""
        if score < -0.5:
            return 'high'
        elif score < -0.2:
            return 'medium'
        else:
            return 'low'
    
    def _identify_anomaly_types(self, features):
        """识别异常类型"""
        anomaly_types = []
        
        # 特征索引对应
        homework_avg = features[0]
        homework_completion_rate = features[1]
        homework_consistency = features[2]
        discussion_posts = features[3]
        discussion_replies = features[4]
        upvotes_ratio = features[5]
        video_watch_time = features[6]
        video_rumination_ratio = features[7]
        learning_pattern_score = features[8]
        academic_performance = features[9]
        engagement_score = features[10]
        
        # 判断异常类型
        if engagement_score < -1:  # 标准化后小于-1表示极低
            anomaly_types.append('low_engagement')
        
        if homework_consistency < -1:
            anomaly_types.append('irregular_pattern')
        
        if academic_performance < -1.5:
            anomaly_types.append('poor_performance')
        
        if video_rumination_ratio > 1.5:  # 过度重复观看
            anomaly_types.append('excessive_struggle')
        
        if (homework_completion_rate > 0.5 and academic_performance < -1) or \
           (discussion_posts + discussion_replies > 0 and academic_performance < -1):
            anomaly_types.append('inconsistent_behavior')
        
        return anomaly_types if anomaly_types else ['unknown']
    
    def detect_anomalies(self, user):
        """检测单个用户的异常行为"""
        if not self.is_trained:
            return None
            
        try:
            features, _ = self.prepare_features([user])
            if len(features) == 0:
                return None
                
            features_scaled = self.scaler.transform(features)
            
            # 预测异常
            anomaly_label = self.model.predict(features_scaled)[0]
            anomaly_score = self.model.decision_function(features_scaled)[0]
            
            is_anomaly = anomaly_label == -1
            
            result = {
                'user_id': user.id,
                'is_anomaly': is_anomaly,
                'anomaly_score': float(anomaly_score),
                'severity': self._get_anomaly_severity(anomaly_score) if is_anomaly else 'normal',
                'confidence': 'high' if abs(anomaly_score) > 0.3 else 'medium',
                'recommendations': []
            }
            
            if is_anomaly:
                result['anomaly_types'] = self._identify_anomaly_types(features_scaled[0])
                result['recommendations'] = self._generate_anomaly_recommendations(result['anomaly_types'])
                result['alert_level'] = self._get_alert_level(anomaly_score, result['anomaly_types'])
            
            return result
            
        except Exception as e:
            logging.error(f"异常检测失败: {str(e)}")
            return None
    
    def _generate_anomaly_recommendations(self, anomaly_types):
        """根据异常类型生成建议"""
        recommendations = []
        
        type_recommendations = {
            'low_engagement': [
                "建议老师主动联系该学生",
                "安排学习伙伴协助",
                "提供额外的学习激励措施"
            ],
            'irregular_pattern': [
                "建议制定固定的学习时间表",
                "提供时间管理指导",
                "监督学习计划执行"
            ],
            'poor_performance': [
                "安排补充辅导课程",
                "重新评估学习基础",
                "提供个性化学习方案"
            ],
            'excessive_struggle': [
                "检查学习方法是否得当",
                "提供更多基础资料",
                "安排一对一答疑"
            ],
            'inconsistent_behavior': [
                "深入了解学生学习困难",
                "评估是否存在外部因素影响",
                "提供心理支持和指导"
            ]
        }
        
        for anomaly_type in anomaly_types:
            if anomaly_type in type_recommendations:
                recommendations.extend(type_recommendations[anomaly_type])
        
        return list(set(recommendations))[:5]  # 去重并限制数量
    
    def _get_alert_level(self, score, anomaly_types):
        """确定警报级别"""
        if score < -0.5 or 'poor_performance' in anomaly_types:
            return 'urgent'
        elif score < -0.2 or 'low_engagement' in anomaly_types:
            return 'warning'
        else:
            return 'attention'
    
    def batch_detect_anomalies(self, users):
        """批量检测异常行为"""
        if not self.is_trained:
            return None
            
        try:
            features, user_ids = self.prepare_features(users)
            features_scaled = self.scaler.transform(features)
            
            # 批量预测
            anomaly_labels = self.model.predict(features_scaled)
            anomaly_scores = self.model.decision_function(features_scaled)
            
            # 统计结果
            anomalies = []
            for i, (user_id, label, score) in enumerate(zip(user_ids, anomaly_labels, anomaly_scores)):
                if label == -1:
                    anomaly_info = {
                        'user_id': user_id,
                        'anomaly_score': float(score),
                        'severity': self._get_anomaly_severity(score),
                        'anomaly_types': self._identify_anomaly_types(features_scaled[i])
                    }
                    anomalies.append(anomaly_info)
            
            # 按严重程度排序
            anomalies.sort(key=lambda x: x['anomaly_score'])
            
            return {
                'total_users': len(user_ids),
                'anomaly_count': len(anomalies),
                'normal_count': len(user_ids) - len(anomalies),
                'anomaly_rate': len(anomalies) / len(user_ids) * 100 if len(user_ids) > 0 else 0,
                'anomalies': anomalies,
                'summary': self._generate_summary_report(anomalies)
            }
            
        except Exception as e:
            logging.error(f"批量异常检测失败: {str(e)}")
            return None
    
    def _generate_summary_report(self, anomalies):
        """生成异常检测摘要报告"""
        if not anomalies:
            return "未检测到异常行为"
        
        # 统计异常类型分布
        type_counts = {}
        severity_counts = {'high': 0, 'medium': 0, 'low': 0}
        
        for anomaly in anomalies:
            # 统计严重程度
            severity_counts[anomaly['severity']] += 1
            
            # 统计异常类型
            for anomaly_type in anomaly['anomaly_types']:
                type_counts[anomaly_type] = type_counts.get(anomaly_type, 0) + 1
        
        # 生成报告
        report_lines = []
        
        if severity_counts['high'] > 0:
            report_lines.append(f"🚨 发现 {severity_counts['high']} 个高风险学生")
        
        if severity_counts['medium'] > 0:
            report_lines.append(f"⚠️ 发现 {severity_counts['medium']} 个中等风险学生")
        
        # 主要异常类型
        if type_counts:
            most_common_type = max(type_counts.items(), key=lambda x: x[1])
            type_name = self.anomaly_types.get(most_common_type[0], most_common_type[0])
            report_lines.append(f"主要问题：{type_name} ({most_common_type[1]}人)")
        
        return " | ".join(report_lines)
    
    def save_model(self, filepath):
        """保存异常检测模型"""
        if self.is_trained:
            model_data = {
                'model': self.model,
                'scaler': self.scaler,
                'contamination': self.contamination,
                'feature_names': self.feature_names,
                'anomaly_types': self.anomaly_types,
                'anomaly_analysis': getattr(self, 'anomaly_analysis', {})
            }
            joblib.dump(model_data, filepath)
            return True
        return False
    
    def load_model(self, filepath):
        """加载异常检测模型"""
        try:
            model_data = joblib.load(filepath)
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.contamination = model_data['contamination']
            self.feature_names = model_data['feature_names']
            self.anomaly_types = model_data['anomaly_types']
            self.anomaly_analysis = model_data.get('anomaly_analysis', {})
            self.is_trained = True
            return True
        except Exception as e:
            logging.error(f"异常检测模型加载失败: {str(e)}")
            return False