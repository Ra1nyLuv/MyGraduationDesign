#!/usr/bin/env python3
"""
数据分析脚本
分析实际数据的分布和质量，为ML算法优化提供依据
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, SynthesisGrade, HomeworkStatistic, DiscussionParticipation, VideoWatchingDetail, ExamStatistic
import numpy as np
import pandas as pd

def analyze_data_distribution():
    """分析数据分布"""
    print("=" * 60)
    print("📊 数据分布分析")
    print("=" * 60)
    
    with app.app_context():
        # 基础统计
        total_users = User.query.count()
        users_with_synthesis = db.session.query(User).join(SynthesisGrade).count()
        users_with_homework = db.session.query(User).join(HomeworkStatistic).count()
        users_with_discussion = db.session.query(User).join(DiscussionParticipation).count()
        users_with_video = db.session.query(User).join(VideoWatchingDetail).count()
        users_with_exam = db.session.query(User).join(ExamStatistic).count()
        
        print(f"📈 基础统计:")
        print(f"  总用户数: {total_users}")
        print(f"  有综合成绩: {users_with_synthesis} ({users_with_synthesis/total_users*100:.1f}%)")
        print(f"  有作业记录: {users_with_homework} ({users_with_homework/total_users*100:.1f}%)")
        print(f"  有讨论记录: {users_with_discussion} ({users_with_discussion/total_users*100:.1f}%)")
        print(f"  有视频记录: {users_with_video} ({users_with_video/total_users*100:.1f}%)")
        print(f"  有考试记录: {users_with_exam} ({users_with_exam/total_users*100:.1f}%)")
        
        return {
            'total_users': total_users,
            'data_completeness': {
                'synthesis': users_with_synthesis / total_users,
                'homework': users_with_homework / total_users,
                'discussion': users_with_discussion / total_users,
                'video': users_with_video / total_users,
                'exam': users_with_exam / total_users
            }
        }

def analyze_score_distribution():
    """分析成绩分布"""
    print(f"\n📊 成绩分布分析:")
    
    with app.app_context():
        # 综合成绩分析
        synthesis_scores = [s.comprehensive_score for s in SynthesisGrade.query.all() if s.comprehensive_score]
        if synthesis_scores:
            print(f"  综合成绩统计:")
            print(f"    平均分: {np.mean(synthesis_scores):.2f}")
            print(f"    标准差: {np.std(synthesis_scores):.2f}")
            print(f"    最高分: {max(synthesis_scores):.2f}")
            print(f"    最低分: {min(synthesis_scores):.2f}")
            print(f"    中位数: {np.median(synthesis_scores):.2f}")
            
            # 分数段分布
            ranges = [(90, 100), (80, 90), (70, 80), (60, 70), (0, 60)]
            print(f"    分数段分布:")
            for low, high in ranges:
                count = sum(1 for s in synthesis_scores if low <= s < high)
                print(f"      {low}-{high}分: {count}人 ({count/len(synthesis_scores)*100:.1f}%)")
        
        # 考试成绩分析
        exam_scores = [e.score for e in ExamStatistic.query.all() if e.score and e.score > 0]
        if exam_scores:
            print(f"  考试成绩统计:")
            print(f"    平均分: {np.mean(exam_scores):.2f}")
            print(f"    标准差: {np.std(exam_scores):.2f}")
            print(f"    最高分: {max(exam_scores):.2f}")
            print(f"    最低分: {min(exam_scores):.2f}")
        
        return {
            'synthesis_scores': synthesis_scores,
            'exam_scores': exam_scores
        }

def analyze_homework_completion():
    """分析作业完成情况"""
    print(f"\n📝 作业完成情况分析:")
    
    with app.app_context():
        homework_data = []
        
        for hw in HomeworkStatistic.query.all():
            scores = []
            for i in range(2, 10):  # score2 到 score9
                score = getattr(hw, f'score{i}', None)
                if score and score > 0:
                    scores.append(score)
            
            homework_data.append({
                'user_id': hw.id,
                'completed_count': len(scores),
                'avg_score': np.mean(scores) if scores else 0,
                'scores': scores
            })
        
        if homework_data:
            completion_rates = [hw['completed_count'] / 8 for hw in homework_data]  # 8个作业
            avg_scores = [hw['avg_score'] for hw in homework_data if hw['avg_score'] > 0]
            
            print(f"    作业完成率:")
            print(f"      平均完成率: {np.mean(completion_rates)*100:.1f}%")
            print(f"      完成率标准差: {np.std(completion_rates)*100:.1f}%")
            
            completion_distribution = {}
            for rate in completion_rates:
                key = f"{int(rate*100//10)*10}-{int(rate*100//10)*10+10}%"
                completion_distribution[key] = completion_distribution.get(key, 0) + 1
            
            print(f"      完成率分布:")
            for range_str, count in sorted(completion_distribution.items()):
                print(f"        {range_str}: {count}人")
            
            if avg_scores:
                print(f"    作业成绩:")
                print(f"      平均分: {np.mean(avg_scores):.2f}")
                print(f"      标准差: {np.std(avg_scores):.2f}")
        
        return homework_data

def analyze_discussion_activity():
    """分析讨论活跃度"""
    print(f"\n💬 讨论活跃度分析:")
    
    with app.app_context():
        discussion_data = []
        
        for disc in DiscussionParticipation.query.all():
            total_activity = (disc.posted_discussions or 0) + (disc.replied_discussions or 0)
            discussion_data.append({
                'user_id': disc.id,
                'total_discussions': disc.total_discussions or 0,
                'posted': disc.posted_discussions or 0,
                'replied': disc.replied_discussions or 0,
                'upvotes': disc.upvotes_received or 0,
                'total_activity': total_activity
            })
        
        if discussion_data:
            activities = [d['total_activity'] for d in discussion_data]
            upvotes = [d['upvotes'] for d in discussion_data]
            
            print(f"    活跃度统计:")
            print(f"      平均活动次数: {np.mean(activities):.2f}")
            print(f"      活跃度标准差: {np.std(activities):.2f}")
            print(f"      最高活跃度: {max(activities)}")
            print(f"      平均获赞数: {np.mean(upvotes):.2f}")
            
            # 活跃度分级
            low_activity = sum(1 for a in activities if a < 3)
            medium_activity = sum(1 for a in activities if 3 <= a < 10)
            high_activity = sum(1 for a in activities if a >= 10)
            
            print(f"      活跃度分布:")
            print(f"        低活跃(<3次): {low_activity}人 ({low_activity/len(activities)*100:.1f}%)")
            print(f"        中活跃(3-9次): {medium_activity}人 ({medium_activity/len(activities)*100:.1f}%)")
            print(f"        高活跃(≥10次): {high_activity}人 ({high_activity/len(activities)*100:.1f}%)")
        
        return discussion_data

def analyze_video_engagement():
    """分析视频学习情况"""
    print(f"\n🎥 视频学习分析:")
    
    with app.app_context():
        video_data = []
        
        for video in VideoWatchingDetail.query.all():
            watch_times = []
            rumination_ratios = []
            
            for i in range(1, 8):  # 1-7个视频
                watch_time = getattr(video, f'watch_duration{i}', None)
                rumination = getattr(video, f'rumination_ratio{i}', None)
                
                if watch_time and watch_time > 0:
                    watch_times.append(watch_time)
                if rumination and rumination > 0:
                    rumination_ratios.append(rumination)
            
            video_data.append({
                'user_id': video.id,
                'total_watch_time': sum(watch_times),
                'avg_rumination': np.mean(rumination_ratios) if rumination_ratios else 0,
                'videos_watched': len(watch_times)
            })
        
        if video_data:
            total_times = [v['total_watch_time'] for v in video_data]
            ruminations = [v['avg_rumination'] for v in video_data if v['avg_rumination'] > 0]
            
            print(f"    视频学习统计:")
            print(f"      平均观看时长: {np.mean(total_times):.2f}分钟")
            print(f"      观看时长标准差: {np.std(total_times):.2f}")
            print(f"      最长观看时长: {max(total_times):.2f}分钟")
            
            if ruminations:
                print(f"      平均重复观看率: {np.mean(ruminations)*100:.1f}%")
                print(f"      重复观看率标准差: {np.std(ruminations)*100:.1f}%")
        
        return video_data

def identify_data_quality_issues():
    """识别数据质量问题"""
    print(f"\n⚠️ 数据质量问题分析:")
    
    with app.app_context():
        issues = []
        
        # 检查空值问题
        users = User.query.options(
            db.joinedload(User.synthesis_grades),
            db.joinedload(User.homework_statistic),
            db.joinedload(User.discussion_participation),
            db.joinedload(User.video_watching_details),
            db.joinedload(User.exam_statistic)
        ).all()
        
        users_without_synthesis = sum(1 for u in users if not u.synthesis_grades)
        users_without_homework = sum(1 for u in users if not u.homework_statistic)
        users_without_discussion = sum(1 for u in users if not u.discussion_participation)
        users_without_video = sum(1 for u in users if not u.video_watching_details)
        
        if users_without_synthesis > 0:
            issues.append(f"缺少综合成绩的用户: {users_without_synthesis}个")
        if users_without_homework > 0:
            issues.append(f"缺少作业记录的用户: {users_without_homework}个")
        if users_without_discussion > 0:
            issues.append(f"缺少讨论记录的用户: {users_without_discussion}个")
        if users_without_video > 0:
            issues.append(f"缺少视频记录的用户: {users_without_video}个")
        
        # 检查异常值
        for user in users:
            if user.synthesis_grades:
                score = user.synthesis_grades[0].comprehensive_score
                if score < 0 or score > 100:
                    issues.append(f"用户{user.id}综合成绩异常: {score}")
        
        if issues:
            print(f"    发现的问题:")
            for issue in issues:
                print(f"      - {issue}")
        else:
            print(f"    ✅ 未发现明显的数据质量问题")
        
        return issues

def recommend_ml_optimizations(basic_stats, score_data, homework_data, discussion_data, video_data, issues):
    """推荐ML算法优化方案"""
    print(f"\n🚀 ML算法优化建议:")
    
    total_users = basic_stats['total_users']
    completeness = basic_stats['data_completeness']
    
    recommendations = []
    
    # 基于数据量的建议
    if total_users < 10:
        recommendations.append("数据量过少，建议使用简单的基于规则的方法替代复杂ML算法")
        recommendations.append("考虑使用无监督学习方法，如简单的统计分析")
    elif total_users < 30:
        recommendations.append("数据量较少，建议降低模型复杂度")
        recommendations.append("使用更简单的算法，如线性回归、决策树")
        recommendations.append("增加数据预处理和特征工程")
    
    # 基于数据完整性的建议
    if completeness['synthesis'] < 0.8:
        recommendations.append("综合成绩数据不完整，考虑使用插值或默认值填充")
    if completeness['homework'] < 0.8:
        recommendations.append("作业数据不完整，使用平均值或中位数填充缺失值")
    if completeness['discussion'] < 0.5:
        recommendations.append("讨论数据缺失严重，考虑降低讨论特征的权重")
    if completeness['video'] < 0.5:
        recommendations.append("视频数据缺失严重，考虑使用简化的学习投入度指标")
    
    # 基于分数分布的建议
    if score_data['synthesis_scores']:
        score_std = np.std(score_data['synthesis_scores'])
        if score_std < 5:
            recommendations.append("成绩分布过于集中，增加特征多样性以提高预测能力")
        elif score_std > 20:
            recommendations.append("成绩分布差异较大，考虑使用分层或分组训练")
    
    # 基于作业完成情况的建议
    if homework_data:
        completion_rates = [hw['completed_count'] / 8 for hw in homework_data]
        low_completion = sum(1 for rate in completion_rates if rate < 0.5)
        if low_completion > total_users * 0.3:
            recommendations.append("作业完成率普遍较低，考虑使用完成率作为主要特征")
    
    # 算法选择建议
    print(f"    推荐的算法调整:")
    if total_users < 20:
        print(f"      预测模型: 使用简单线性回归或决策树")
        print(f"      聚类分析: 使用K-means，聚类数设为2-3")
        print(f"      异常检测: 使用基于统计的方法（Z-score）")
    else:
        print(f"      预测模型: 可以使用随机森林，但减少树的数量")
        print(f"      聚类分析: K-means，动态调整聚类数")
        print(f"      异常检测: 孤立森林，调整contamination参数")
    
    print(f"    具体优化建议:")
    for i, rec in enumerate(recommendations, 1):
        print(f"      {i}. {rec}")
    
    return recommendations

def main():
    """主函数"""
    print("🔍 开始数据分析...")
    
    # 运行各项分析
    basic_stats = analyze_data_distribution()
    score_data = analyze_score_distribution()
    homework_data = analyze_homework_completion()
    discussion_data = analyze_discussion_activity()
    video_data = analyze_video_engagement()
    issues = identify_data_quality_issues()
    
    # 生成优化建议
    recommendations = recommend_ml_optimizations(
        basic_stats, score_data, homework_data, discussion_data, video_data, issues
    )
    
    print(f"\n" + "=" * 60)
    print(f"✅ 数据分析完成")
    print(f"📋 下一步: 根据分析结果调整ML算法")
    print(f"=" * 60)

if __name__ == "__main__":
    main()