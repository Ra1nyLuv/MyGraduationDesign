"""
个性化推荐系统
基于学生的学习行为和成绩数据，提供个性化的学习建议和资源推荐
"""

import numpy as np
import pandas as pd
from datetime import datetime
import logging

class PersonalizedRecommendation:
    def __init__(self):
        self.learning_resources = {
            'programming': [
                "Python编程基础视频教程",
                "数据结构与算法练习题",
                "编程实战项目案例",
                "代码调试技巧指南"
            ],
            'data_analysis': [
                "数据可视化实践教程",
                "统计学基础知识复习",
                "pandas数据处理教程",
                "机器学习入门指南"
            ],
            'discussion': [
                "课程论坛活跃度提升指南",
                "有效提问技巧",
                "学术讨论礼仪",
                "同伴学习方法"
            ],
            'time_management': [
                "学习时间管理技巧",
                "番茄工作法实践",
                "学习计划制定模板",
                "拖延症克服方法"
            ]
        }
        
        self.study_strategies = {
            'high_performer': [
                "挑战更高难度的项目",
                "参与开源项目贡献",
                "准备技术认证考试",
                "指导其他同学学习"
            ],
            'steady_learner': [
                "保持稳定的学习节奏",
                "适当增加课外拓展",
                "参与小组学习活动",
                "定期复习已学内容"
            ],
            'struggling_student': [
                "寻求老师一对一辅导",
                "参加学习互助小组",
                "重新学习基础知识",
                "制定详细的学习计划"
            ],
            'passive_learner': [
                "设定明确的学习目标",
                "参与更多课堂互动",
                "寻找学习伙伴",
                "使用学习激励工具"
            ]
        }
        
    def generate_personalized_recommendations(self, user):
        """为用户生成个性化推荐"""
        try:
            # 分析用户学习状况
            analysis = self._analyze_user_performance(user)
            
            # 生成推荐内容
            recommendations = {
                'learning_resources': self._recommend_learning_resources(analysis),
                'study_strategies': self._recommend_study_strategies(analysis),
                'improvement_areas': self._identify_improvement_areas(analysis),
                'weekly_goals': self._suggest_weekly_goals(analysis),
                'performance_insights': analysis
            }
            
            return recommendations
            
        except Exception as e:
            logging.error(f"生成个性化推荐失败: {str(e)}")
            return None
    
    def _analyze_user_performance(self, user):
        """分析用户学习表现"""
        analysis = {
            'homework_performance': 0,
            'discussion_activity': 0,
            'video_engagement': 0,
            'learning_consistency': 0,
            'overall_score': 0,
            'strengths': [],
            'weaknesses': [],
            'learning_type': 'unknown'
        }
        
        try:
            # 作业表现分析
            homework = user.homework_statistic[0] if user.homework_statistic else None
            if homework:
                scores = [getattr(homework, f'score{i}', 0) for i in range(2, 10)]
                valid_scores = [s for s in scores if s > 0]
                
                if valid_scores:
                    analysis['homework_performance'] = np.mean(valid_scores)
                    analysis['homework_completion_rate'] = len(valid_scores) / len(scores)
                    
                    if analysis['homework_performance'] >= 85:
                        analysis['strengths'].append('作业完成质量高')
                    elif analysis['homework_performance'] < 60:
                        analysis['weaknesses'].append('作业成绩需要提升')
                    
                    if analysis['homework_completion_rate'] < 0.8:
                        analysis['weaknesses'].append('作业完成率偏低')
            
            # 讨论活跃度分析
            discussion = user.discussion_participation[0] if user.discussion_participation else None
            if discussion:
                total_activity = (
                    discussion.posted_discussions + 
                    discussion.replied_discussions + 
                    discussion.upvotes_received
                )
                analysis['discussion_activity'] = total_activity
                
                if total_activity >= 15:
                    analysis['strengths'].append('课程讨论参与度高')
                elif total_activity < 5:
                    analysis['weaknesses'].append('课程讨论参与度低')
            
            # 视频学习分析
            video = user.video_watching_details[0] if user.video_watching_details else None
            if video:
                watch_times = [getattr(video, f'watch_duration{i}', 0) for i in range(1, 8)]
                rumination_ratios = [getattr(video, f'rumination_ratio{i}', 0) for i in range(1, 8)]
                
                total_watch_time = sum(watch_times)
                avg_rumination = np.mean([r for r in rumination_ratios if r > 0]) if any(r > 0 for r in rumination_ratios) else 0
                
                analysis['video_engagement'] = total_watch_time
                analysis['video_rumination'] = avg_rumination
                
                if total_watch_time >= 300:  # 5小时以上
                    analysis['strengths'].append('视频学习时间充足')
                elif total_watch_time < 120:  # 2小时以下
                    analysis['weaknesses'].append('视频学习时间不足')
                
                if avg_rumination > 0.3:
                    analysis['weaknesses'].append('视频重复观看率高，理解存在困难')
            
            # 综合成绩分析
            synthesis = user.synthesis_grades[0] if user.synthesis_grades else None
            if synthesis:
                analysis['overall_score'] = synthesis.comprehensive_score
                
                if synthesis.comprehensive_score >= 90:
                    analysis['learning_type'] = 'high_performer'
                elif synthesis.comprehensive_score >= 75:
                    analysis['learning_type'] = 'steady_learner'
                elif synthesis.comprehensive_score >= 60:
                    analysis['learning_type'] = 'struggling_student'
                else:
                    analysis['learning_type'] = 'passive_learner'
            
            # 学习一致性分析
            if homework:
                scores = [getattr(homework, f'score{i}', 0) for i in range(2, 10)]
                non_zero_scores = [s for s in scores if s > 0]
                if len(non_zero_scores) > 2:
                    score_std = np.std(non_zero_scores)
                    score_mean = np.mean(non_zero_scores)
                    analysis['learning_consistency'] = 1 / (1 + score_std / score_mean) if score_mean > 0 else 0
                    
                    if analysis['learning_consistency'] > 0.8:
                        analysis['strengths'].append('学习表现稳定')
                    elif analysis['learning_consistency'] < 0.5:
                        analysis['weaknesses'].append('学习表现波动较大')
        
        except Exception as e:
            logging.warning(f"分析用户表现时出错: {str(e)}")
        
        return analysis
    
    def _recommend_learning_resources(self, analysis):
        """推荐学习资源"""
        recommendations = []
        
        # 根据弱项推荐资源
        if '作业成绩需要提升' in analysis['weaknesses']:
            recommendations.extend(self.learning_resources['programming'][:2])
        
        if '课程讨论参与度低' in analysis['weaknesses']:
            recommendations.extend(self.learning_resources['discussion'][:2])
        
        if '视频学习时间不足' in analysis['weaknesses']:
            recommendations.extend(self.learning_resources['data_analysis'][:2])
        
        if '学习表现波动较大' in analysis['weaknesses']:
            recommendations.extend(self.learning_resources['time_management'][:2])
        
        # 根据学习类型补充推荐
        if analysis['learning_type'] == 'high_performer':
            recommendations.extend(self.learning_resources['data_analysis'][2:])
        elif analysis['learning_type'] in ['struggling_student', 'passive_learner']:
            recommendations.extend(self.learning_resources['programming'][:2])
        
        return list(set(recommendations))[:6]  # 去重并限制数量
    
    def _recommend_study_strategies(self, analysis):
        """推荐学习策略"""
        learning_type = analysis.get('learning_type', 'steady_learner')
        strategies = self.study_strategies.get(learning_type, self.study_strategies['steady_learner'])
        
        # 根据具体弱项添加针对性策略
        additional_strategies = []
        
        if '作业完成率偏低' in analysis['weaknesses']:
            additional_strategies.append("设定每日作业完成提醒")
        
        if '视频重复观看率高，理解存在困难' in analysis['weaknesses']:
            additional_strategies.append("观看视频时做笔记，提高理解效率")
        
        return strategies[:3] + additional_strategies[:2]
    
    def _identify_improvement_areas(self, analysis):
        """识别需要改进的领域"""
        improvement_areas = []
        
        # 基于弱项识别改进领域
        weakness_mapping = {
            '作业成绩需要提升': {
                'area': '编程技能',
                'priority': 'high',
                'actions': ['多做编程练习', '复习基础语法', '参考优秀代码']
            },
            '作业完成率偏低': {
                'area': '时间管理',
                'priority': 'high', 
                'actions': ['制定学习计划', '设置截止日期提醒', '分解大任务']
            },
            '课程讨论参与度低': {
                'area': '学习互动',
                'priority': 'medium',
                'actions': ['主动提问', '回复他人问题', '分享学习心得']
            },
            '视频学习时间不足': {
                'area': '学习投入度',
                'priority': 'medium',
                'actions': ['安排固定学习时间', '提高学习专注度', '减少干扰因素']
            },
            '学习表现波动较大': {
                'area': '学习稳定性',
                'priority': 'medium',
                'actions': ['建立学习习惯', '保持学习节奏', '定期自我评估']
            }
        }
        
        for weakness in analysis['weaknesses']:
            if weakness in weakness_mapping:
                improvement_areas.append(weakness_mapping[weakness])
        
        return improvement_areas
    
    def _suggest_weekly_goals(self, analysis):
        """建议每周学习目标"""
        goals = []
        
        # 基础目标
        goals.append({
            'category': '作业完成',
            'goal': '按时完成所有作业',
            'target': '100%完成率',
            'importance': 'high'
        })
        
        # 根据弱项设定针对性目标
        if '课程讨论参与度低' in analysis['weaknesses']:
            goals.append({
                'category': '课程互动',
                'goal': '每周至少参与3次讨论',
                'target': '3次/周',
                'importance': 'medium'
            })
        
        if '视频学习时间不足' in analysis['weaknesses']:
            goals.append({
                'category': '视频学习',
                'goal': '每周视频学习时间不少于4小时',
                'target': '4小时/周',
                'importance': 'medium'
            })
        
        # 根据学习类型调整目标
        if analysis['learning_type'] == 'high_performer':
            goals.append({
                'category': '拓展学习',
                'goal': '完成一个课外编程项目',
                'target': '1个项目/月',
                'importance': 'low'
            })
        elif analysis['learning_type'] in ['struggling_student', 'passive_learner']:
            goals.append({
                'category': '基础巩固',
                'goal': '每周复习已学内容',
                'target': '2小时/周',
                'importance': 'high'
            })
        
        return goals[:4]  # 限制目标数量
    
    def get_learning_path_recommendation(self, user, target_score=None):
        """生成学习路径推荐"""
        try:
            analysis = self._analyze_user_performance(user)
            current_score = analysis.get('overall_score', 0)
            target = target_score or (current_score + 10)
            
            # 计算需要改进的分数
            score_gap = target - current_score
            
            learning_path = {
                'current_level': self._get_level_description(current_score),
                'target_level': self._get_level_description(target),
                'score_gap': score_gap,
                'estimated_weeks': max(2, int(score_gap / 2)),  # 估算需要的周数
                'milestones': self._generate_milestones(current_score, target),
                'priority_actions': self._get_priority_actions(analysis, score_gap)
            }
            
            return learning_path
            
        except Exception as e:
            logging.error(f"生成学习路径推荐失败: {str(e)}")
            return None
    
    def _get_level_description(self, score):
        """获取分数等级描述"""
        if score >= 90:
            return "优秀水平"
        elif score >= 80:
            return "良好水平"
        elif score >= 70:
            return "中等水平"
        elif score >= 60:
            return "及格水平"
        else:
            return "需要努力"
    
    def _generate_milestones(self, current, target):
        """生成学习里程碑"""
        milestones = []
        step = (target - current) / 3
        
        for i in range(1, 4):
            milestone_score = current + step * i
            milestones.append({
                'week': i * 2,
                'target_score': round(milestone_score, 1),
                'description': f"第{i * 2}周目标：达到{milestone_score:.1f}分"
            })
        
        return milestones
    
    def _get_priority_actions(self, analysis, score_gap):
        """获取优先行动项"""
        actions = []
        
        if score_gap > 15:  # 大幅提升
            actions.extend([
                "重新学习基础知识",
                "寻求老师个别指导",
                "参加学习小组"
            ])
        elif score_gap > 8:  # 中等提升
            actions.extend([
                "提高作业质量",
                "增加课程参与度",
                "制定详细学习计划"
            ])
        else:  # 小幅提升
            actions.extend([
                "保持当前学习节奏",
                "适当增加拓展学习",
                "参与更多讨论"
            ])
        
        return actions[:5]