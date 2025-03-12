from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv
import os
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
import jwt
from datetime import datetime, timedelta
import pandas as pd

load_dotenv()
app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@"
    f"{os.getenv('MYSQL_HOST')}/{os.getenv('MYSQL_DB')}?charset=utf8mb4"
)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)

class User(db.Model):
    __tablename__ = 'users' # 存储用户数据
    id = db.Column(db.String(80), primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(11), unique=True, nullable=False)

class SynthesisGrade(db.Model):
    __tablename__ = 'synthesis_grades'
    id = db.Column(db.String(80), db.ForeignKey('users.id'), primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    course_points = db.Column(db.Float, nullable=True)
    comprehensive_score = db.Column(db.Float, nullable=False)
    user = db.relationship('User', backref='synthesis_grades')

class StudyProgress(db.Model):
    __tablename__ = 'study_progress' # 学生学习进度详情
    id = db.Column(db.String(80), db.ForeignKey('users.id'), primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    task_completed = db.Column(db.Integer, nullable=False)  # 任务完成数
    completion_percent = db.Column(db.Float, nullable=False)  # 任务点完成百分比
    video_duration = db.Column(db.Integer)  # 视频观看时长(分钟)
    discussions = db.Column(db.Integer)  # 讨论数
    study_count = db.Column(db.Integer)  # 章节学习次数
    study_status = db.Column(db.String(255))  # 学习情况
    user = db.relationship('User', backref='study_progress')

# class ChapterStudyTime(db.Model): xlsx文件中的信息不明确, 故暂时搁置
#     __tablename__ = 'chapter_study_time' # 章节学习次数


# class MissionCompletion(db.Model): 暂时搁置
#     __tablename__ = 'mission_completion' # 任务点完成情况


# class VideoWatchTime(db.Model): 暂时搁置
#     __tablename__ = 'video_watch_time' # 音视频观看详情


class DiscussionParticipation(db.Model):
    __tablename__ = 'discussion_participation' # 章节学习次数
    id = db.Column(db.String(80), db.ForeignKey('users.id'), primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    total_discussions = db.Column(db.Integer, nullable=False)  # 总讨论数
    posted_discussions = db.Column(db.Integer)  # 发表讨论
    replied_discussions = db.Column(db.Integer)  # 回复讨论
    replied_topics = db.Column(db.Integer)  # 回复话题个数
    upvotes_received = db.Column(db.Integer)  # 获赞数
    user = db.relationship('User', backref='discussion_participation')

# class HomeworkCount(db.Model): 暂时搁置, 字段信息暂无法读取
#     __tablename__ = 'homework_count' # 作业统计


# class ExamResult(db.Model): 暂时搁置, 字段信息暂无法读取
#     __tablename__ = 'exam_results' # 考试统计


# class ChapterExamResult(db.Model): 表格信息缺失, 暂时搁置
#     __tablename__ = 'chapter_exam_results' # 章节测验统计


class OfflineGrade(db.Model):
    __tablename__ = 'offline_grades' # 线下成绩
    id = db.Column(db.String(80), db.ForeignKey('users.id'), primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    comprehensive_score = db.Column(db.Float, nullable=False)
    user = db.relationship('User', backref='offline_grades')


@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        # 验证必填字段
        if not all(key in data for key in ['id', 'password', 'name', 'phone_number']):
            return jsonify({"error": "缺少必要字段: id/password/name/phone_number"}), 400

        # 检查手机号唯一性
        if User.query.filter_by(phone_number=data['phone_number']).first():
            return jsonify({"error": "该手机号已被注册"}), 400
        if User.query.filter_by(id=data['id']).first():
            return jsonify({"error": "用户ID已被占用"}), 400

        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        new_user = User(
            id=data['id'],
            password=hashed_password,
            name=data['name'],
            phone_number=data['phone_number']
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "用户注册成功", "user_id": new_user.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"注册失败: {str(e)}"}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        user = User.query.filter_by(id=data['id']).first()
        
        if not user or not bcrypt.check_password_hash(user.password, data['password']):
            return jsonify({"error": "账号或密码错误"}), 401


        return jsonify({
            "message": "登录成功",
            "id": user.id,
            "token": jwt.encode({'user_id': user.id, 'exp': datetime.utcnow() + timedelta(hours=1)}, os.getenv('SECRET_KEY'), algorithm='HS256')
        }), 200
    except Exception as e:
        return jsonify({"error": "登录失败"}), 500

# 确保在应用上下文中创建数据库表
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)