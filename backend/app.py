from flask import Flask, jsonify, request
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
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
        
        app.logger.debug(f"尝试登录用户: {data.get('id')}")
        
        if not user or not bcrypt.check_password_hash(user.password, data['password']):
            app.logger.warning(f"登录失败 - 用户ID: {data.get('id')}, 错误类型: 账号或密码错误")
            return jsonify({"error": "账号或密码错误"}), 401
        
        access_token = create_access_token(identity=user.id)
        app.logger.info(f"用户登录成功: {user.id}, Token已生成")
        
        return jsonify({
            "message": "登录成功",
            "id": user.id,
            "token": access_token
        }), 200

    except Exception as e:
        app.logger.error(f"登录异常: {str(e)}", exc_info=True)
        return jsonify({"error": "登录失败"}), 500
@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
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


@app.route('/api/my-data', methods=['GET', 'OPTIONS'])
@jwt_required()
def get_user_data():
    logger.info('开始处理用户数据请求')
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    try:
        current_user_id = get_jwt_identity()  
        
        user = User.query.options(
            db.joinedload(User.synthesis_grades),
            db.joinedload(User.homework_statistic),
            db.joinedload(User.exam_statistic),
            db.joinedload(User.discussion_participation),
            db.joinedload(User.video_watching_details),
            db.joinedload(User.offline_grades)
        ).get(current_user_id)
        
        if not user:
            logger.warning(f"用户数据查询失败 - 无效用户ID: {current_user_id}")
            return jsonify({'error': '用户不存在'}), 404

        homework = user.homework_statistic[0] if user.homework_statistic else HomeworkStatistic()
        exam = user.exam_statistic[0] if user.exam_statistic else ExamStatistic(score=0)
        synthesis = user.synthesis_grades[0] if user.synthesis_grades else SynthesisGrade(comprehensive_score=0)
        
        exam = ExamStatistic.query.filter_by(id=user.id).first() or ExamStatistic(score=0)
        synthesis = SynthesisGrade.query.filter_by(id=user.id).first() or SynthesisGrade(comprehensive_score=0)
        discussion = DiscussionParticipation.query.filter_by(id=user.id).first()
        video_watching = VideoWatchingDetail.query.filter_by(id=user.id).first()
        offline_grade = OfflineGrade.query.filter_by(id=user.id).first()

        logger.info(f'返回用户数据: {user.id}')
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
                    getattr(homework, 'score7', 0) if homework else 0,
                    getattr(homework, 'score8', 0) if homework else 0,
                    getattr(homework, 'score9', 0) if homework else 0
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
        logger.error(f'数据查询失败: {str(e)}')
        return jsonify({'error': '获取数据失败', 'detail': str(e)}), 500



with app.app_context():
    db.create_all()


jwt_manager = JWTManager(app)

# 预检请求响应构建函数
def _build_cors_preflight_response():
    response = jsonify({'msg': 'Preflight Request'})
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5173')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

@app.route('/api/chart-data', methods=['GET', 'OPTIONS'])
def get_chart_data():
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    # 获取当前用户ID
    user_id = request.args.get('id')
    if not user_id:
        return jsonify({"status": 1, "msg": "缺少用户ID参数"})
    
    # 查询数据库获取数据
    homework = HomeworkStatistic.query.get(user_id)
    exam = ExamStatistic.query.get(user_id)
    offline = OfflineGrade.query.get(user_id)
    
    if not homework or not exam or not offline:
        return jsonify({"status": 1, "msg": "用户数据不存在"})
    
    # 构建返回数据结构
    data = {
        "user": {
            "id": user_id,
            "name": homework.name
        },
        "scores": {
            "comprehensive": offline.comprehensive_score,
            "course_points": 0,  
            "exam": exam.score,
            "rank": 0,  # 需要根据实际业务逻辑计算
            "homework": [homework.score2, homework.score3, homework.score4, 
                         homework.score5, homework.score6, homework.score7,
                         homework.score8, homework.score9]
        },
        "behavior": {
            "posted": 0,  # 需要从讨论表获取
            "replied": 0,  # 需要从讨论表获取
            "upvotes": 0  # 需要从讨论表获取
        },
        "progress": {
            "rumination_ratios": [0] * 42  # 需要从视频观看表获取
        }
    }
    
    return jsonify({"status": 0, "msg": "获取图表数据成功", "data": data})


if __name__ == '__main__':
    app.run(debug=True)

    