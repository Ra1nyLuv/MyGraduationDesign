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
from flask import request, jsonify
from flask_jwt_extended import (
    JWTManager,
    jwt_required,
    get_jwt_identity,
    create_access_token
)
app = Flask(__name__)

print('正在加载环境变量文件路径:', os.path.join(os.path.dirname(__file__), '..', '.env'))
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
print(f'环境变量加载状态: JWT_SECRET_KEY={os.getenv("JWT_SECRET_KEY")}, MYSQL_HOST={os.getenv("MYSQL_HOST")}')

app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
jwt_manager = JWTManager(app)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}}, supports_credentials=True)

@app.route('/api/get', methods=['GET'])
def api_get():
    query = request.args
    response = jsonify({
        "status": 0, 
        "msg": "GET 请求成功！",
        "data": dict(query)
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response




app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@"
    f"{os.getenv('MYSQL_HOST')}/{os.getenv('MYSQL_DB')}?charset=utf8mb4"
)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)
if not os.getenv('JWT_SECRET_KEY'):
    raise ValueError('JWT_SECRET_KEY环境变量未配置')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
print(f'JWT_SECRET_KEY加载状态: {os.getenv("JWT_SECRET_KEY")}')
jwt_manager = JWTManager(app)

# 更新预检响应头配置
def _build_cors_preflight_response():
    response = jsonify({'msg': 'Preflight Request'})
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5173')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
    response.headers.add('Access-Control-Allow-Methods', 'POST, GET, OPTIONS, PUT, DELETE')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.headers.add('Access-Control-Max-Age', '86400')
    return response

class User(db.Model):
    __tablename__ = 'users' # 存储用户数据
    id = db.Column(db.String(80), primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(11), nullable=False)

class SynthesisGrade(db.Model):
    __tablename__ = 'synthesis_grades' # 综合成绩
    id = db.Column(db.String(80), db.ForeignKey('users.id'), primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    course_points = db.Column(db.Float, nullable=True) 
    comprehensive_score = db.Column(db.Float, nullable=False)
    user = db.relationship('User', backref='synthesis_grades')

# class StudyProgress(db.Model): # 数据文件中无姓名和id信息, 暂时搁置
#     __tablename__ = 'study_progress' # 学生学习进度详情
#     name = db.Column(db.String(80), nullable=False)
#     task_completed = db.Column(db.Integer, nullable=False)  # 任务完成数
#     completion_percent = db.Column(db.Float, nullable=False)  # 任务点完成百分比
#     video_duration = db.Column(db.Integer)  # 视频观看时长(分钟)
#     discussions = db.Column(db.Integer)  # 讨论数
#     study_count = db.Column(db.Integer)  # 章节学习次数
#     study_status = db.Column(db.String(255))  # 学习情况
#     user = db.relationship('User', backref='study_progress')

# class ChapterStudyTime(db.Model): xlsx文件中的信息不明确, 故暂时搁置
#     __tablename__ = 'chapter_study_time' # 章节学习次数


# class MissionCompletion(db.Model): 暂时搁置
#     __tablename__ = 'mission_completion' # 任务点完成情况


class VideoWatchingDetail(db.Model):
    __tablename__ = 'video_watching_details'
    id = db.Column(db.String(80), db.ForeignKey('users.id'), primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    rumination_ratio1 = db.Column(db.Float)
    watch_duration1 = db.Column(db.Float)  
    rumination_ratio2 = db.Column(db.Float)
    watch_duration2 = db.Column(db.Float)
    rumination_ratio3 = db.Column(db.Float)
    watch_duration3 = db.Column(db.Float)
    rumination_ratio4 = db.Column(db.Float)
    watch_duration4 = db.Column(db.Float)
    rumination_ratio5 = db.Column(db.Float)
    watch_duration5 = db.Column(db.Float)
    rumination_ratio6 = db.Column(db.Float)
    watch_duration6 = db.Column(db.Float)
    rumination_ratio7 = db.Column(db.Float)
    watch_duration7 = db.Column(db.Float)
    user = db.relationship('User', backref='video_watching_details')


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


class ExamStatistic(db.Model):
    __tablename__ = 'exam_statistic' # 考试统计
    id = db.Column(db.String(80), db.ForeignKey('users.id'), primary_key=True) # 学号/工号
    name = db.Column(db.String(80), nullable=False) # 姓名
    score = db.Column(db.Float, nullable=True) # 成绩
    user = db.relationship('User', backref='exam_statistic')



# class ChapterExamResult(db.Model): 表格信息缺失, 暂时搁置
#     __tablename__ = 'chapter_exam_results' # 章节测验统计


class OfflineGrade(db.Model):
    __tablename__ = 'offline_grades' # 线下成绩
    id = db.Column(db.String(80), db.ForeignKey('users.id'), primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    comprehensive_score = db.Column(db.Float, nullable=False)
    user = db.relationship('User', backref='offline_grades')


class HomeworkStatistic(db.Model):
    __tablename__ = 'homework_statistic'
    id = db.Column(db.String(80), db.ForeignKey('users.id'), primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    score2 = db.Column(db.Float)
    score3 = db.Column(db.Float)
    score4 = db.Column(db.Float)
    score5 = db.Column(db.Float)
    score6 = db.Column(db.Float)
    score7 = db.Column(db.Float)
    score8 = db.Column(db.Float)
    score9 = db.Column(db.Float)
    user = db.relationship('User', backref='homework_statistic')



@app.route('/api/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    try:
        data = request.get_json()
        user = User.query.filter_by(id=data['id']).first()
        
        if not user or not bcrypt.check_password_hash(user.password, data['password']):
            return jsonify({"error": "账号或密码错误"}), 401, {'Access-Control-Allow-Origin': 'http://localhost:5173'}


        return jsonify({
            "message": "登录成功",
            "id": user.id,
            "token": jwt.encode({'user_id': user.id, 'exp': datetime.utcnow() + timedelta(hours=1)}, os.getenv('JWT_SECRET_KEY'), algorithm='HS256')
        }), 200, {'Access-Control-Allow-Origin': 'http://localhost:5173'}
        app.logger.info(f'登录请求数据: {data}')
        app.logger.info(f'当前环境变量状态: MYSQL_HOST={os.getenv("MYSQL_HOST")}, MYSQL_DB={os.getenv("MYSQL_DB")}')
    except Exception as e:
        app.logger.error(f'登录失败异常详情: {str(e)}', exc_info=True)
        app.logger.error(f'数据库查询语句: {str(db.session.query(User).filter_by(id=data["id"]))}')
        return jsonify({"error": "登录失败"}), 500, {'Access-Control-Allow-Origin': 'http://localhost:5173'}

@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        # 验证必填字段
        if not all(key in data for key in ['id', 'password', 'name', 'phone_number']):
            return jsonify({"error": "缺少必要字段: id/password/name/phone_number"}), 400


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


@app.route('/my-data', methods=['GET', 'OPTIONS'])


@jwt_required()
def get_user_data():
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    current_user = get_jwt_identity()
    try:
        user = User.query.get(int(current_user))
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        synthesis = SynthesisGrade.query.filter_by(id=user.id).first()
        homework = HomeworkStatistic.query.filter_by(id=user.id).first() or HomeworkStatistic()
        
        # 处理空值情况
        homework_scores = [
            homework.score2 or 0,
            homework.score3 or 0, 
            homework.score4 or 0,
            homework.score5 or 0,
            homework.score6 or 0,
            homework.score7 or 0,
            getattr(homework, 'score8', 0) or 0,
            getattr(homework, 'score9', 0) or 0
        ]

        # 添加密钥检查
        if not os.getenv('JWT_SECRET_KEY'):
            app.logger.error('JWT_SECRET_KEY未配置')
            return jsonify({'error': '服务器配置错误'}), 500
        exam = ExamStatistic.query.filter_by(id=user.id).first() or ExamStatistic(score=0)
        synthesis = SynthesisGrade.query.filter_by(id=user.id).first() or SynthesisGrade(comprehensive_score=0)
        discussion = DiscussionParticipation.query.filter_by(id=user.id).first()
        video_watching = VideoWatchingDetail.query.filter_by(id=user.id).first()
        offline_grade = OfflineGrade.query.filter_by(id=user.id).first()

        return jsonify({
            'user': {
                'id': user.id,
                'name': user.name
            },
            'scores': {
                'comprehensive': synthesis.comprehensive_score if synthesis else 0,
                'course_points': synthesis.course_points if synthesis else 0,
                'homework': [
                    getattr(homework, 'score2', 0) if homework else 0,
                    getattr(homework, 'score3', 0) if homework else 0,
                    getattr(homework, 'score4', 0) if homework else 0,
                    getattr(homework, 'score5', 0) if homework else 0,
                    getattr(homework, 'score6', 0) if homework else 0,
                    getattr(homework, 'score7', 0) if homework else 0
                ],
                'offline': offline_grade.comprehensive_score if offline_grade else 0,
                'exam': exam.score if exam else 0
            },
            'behavior': {
                'discussions': discussion.total_discussions if discussion else 0,
                'posted': discussion.posted_discussions if discussion else 0,
                'replied': discussion.replied_discussions if discussion else 0,
                'topics': discussion.replied_topics if discussion else 0,
                'upvotes': discussion.upvotes_received if discussion else 0
            },
            'progress': {
                'video_durations': [
                    getattr(video_watching, 'watch_duration1', 0) or 0,
                    getattr(video_watching, 'watch_duration2', 0) or 0,
                    getattr(video_watching, 'watch_duration3', 0) or 0,
                    getattr(video_watching, 'watch_duration4', 0) or 0,
                    getattr(video_watching, 'watch_duration5', 0) or 0,
                    getattr(video_watching, 'watch_duration6', 0) or 0,
                    getattr(video_watching, 'watch_duration7', 0) or 0
                ],
                'rumination_ratios': [
                    getattr(video_watching, 'rumination_ratio1', 0) or 0,
                    getattr(video_watching, 'rumination_ratio2', 0) or 0,
                    getattr(video_watching, 'rumination_ratio3', 0) or 0,
                    getattr(video_watching, 'rumination_ratio4', 0) or 0,
                    getattr(video_watching, 'rumination_ratio5', 0) or 0,
                    getattr(video_watching, 'rumination_ratio6', 0) or 0,
                    getattr(video_watching, 'rumination_ratio7', 0) or 0
                ]
            }
        }), 200
    except Exception as e:
        app.logger.error(f'数据查询失败: {str(e)}')
        return jsonify({'error': '获取数据失败', 'detail': str(e)}), 500

@app.route('/data', methods=['GET'])
@jwt_required()
def get_chart_data():
    current_user = get_jwt_identity()
    user_data = HomeworkStatistic.query.get(current_user)
    if not user_data:
        return jsonify({'error': '未找到作业数据'}), 404
    
    exam_data = ExamStatistic.query.get(current_user)
    
    return jsonify({
        'chartData': {
            'labels': ['作业2', '作业3', '作业4', '作业5', '作业6', '作业7'],
            'datasets': [{
                'label': '作业成绩',
                'data': homework_scores,
                'backgroundColor': 'rgba(54, 162, 235, 0.5)'
            }]
        }}), 200


with app.app_context():
    db.create_all()


jwt_manager = JWTManager(app)

# 预检请求响应构建函数
def _build_cors_preflight_response():
    response = jsonify({'msg': 'Preflight Request'})
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5173')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response


if __name__ == '__main__':
    app.run(debug=True)

    