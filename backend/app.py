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

# 修复Windows下KMeans内存泄漏警告
if os.name == 'nt':  # Windows系统
    os.environ['OMP_NUM_THREADS'] = '1'
    print('🔧 Windows环境: 已设置 OMP_NUM_THREADS=1 以避免KMeans内存泄漏警告')

app = Flask(__name__)

# 加载 .env 文件
print('正在加载环境变量文件路径:', os.path.join(os.path.dirname(__file__), '..', '.env'))
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
print(f'环境变量加载状态: JWT_SECRET_KEY={os.getenv("JWT_SECRET_KEY")}, MYSQL_HOST={os.getenv("MYSQL_HOST")}')

# 配置JWT 密钥和数据库连接
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
jwt_manager = JWTManager(app)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
CORS(app, resources={r"/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173"]}}, supports_credentials=True)

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

# CORS辅助函数
def _add_cors_headers(response, origin=None):
    """为响应添加CORS头"""
    allowed_origins = ['http://localhost:5173', 'http://127.0.0.1:5173']
    
    # 获取请求的Origin
    if not origin:
        origin = request.headers.get('Origin')
    
    # 如果Origin在允许列表中，使用该Origin，否则使用默认的localhost
    if origin in allowed_origins:
        response.headers.add('Access-Control-Allow-Origin', origin)
    else:
        _add_cors_headers(response)
    
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.headers.add('Vary', 'Origin')
    return response

# 预检响应头配置
def _build_cors_preflight_response():
    response = jsonify({'msg': 'Preflight Request'})
    origin = request.headers.get('Origin')
    # 允许的源地址列表
    allowed_origins = ['http://localhost:5173', 'http://127.0.0.1:5173']
    if origin in allowed_origins:
        response.headers.add('Access-Control-Allow-Origin', origin)
    else:
        _add_cors_headers(response)
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
    response.headers.add('Access-Control-Allow-Methods', 'POST, GET, OPTIONS, PUT, DELETE')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.headers.add('Access-Control-Max-Age', '86400')
    response.headers.add('Vary', 'Origin')
    return response

# 数据库模型
class User(db.Model):
    __tablename__ = 'users' # 存储用户数据
    id = db.Column(db.String(80), primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(11), nullable=False)
    role = db.Column(db.String(15), default='user')

class SynthesisGrade(db.Model):
    __tablename__ = 'synthesis_grades' # 综合成绩
    id = db.Column(db.String(80), db.ForeignKey('users.id'), primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    course_points = db.Column(db.Float, nullable=True) 
    comprehensive_score = db.Column(db.Float, nullable=False)
    user = db.relationship('User', backref='synthesis_grades')

class VideoWatchingDetail(db.Model):
    __tablename__ = 'video_watching_details' #音视频观看详情
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

class OfflineGrade(db.Model):
    __tablename__ = 'offline_grades' # 线下成绩
    id = db.Column(db.String(80), db.ForeignKey('users.id'), primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    comprehensive_score = db.Column(db.Float, nullable=False)
    user = db.relationship('User', backref='offline_grades')

class HomeworkStatistic(db.Model):
    __tablename__ = 'homework_statistic' # 作业统计
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

with app.app_context():
    db.create_all()


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


# 登录接口
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
            "token": access_token,
            "role": user.role
        }), 200

    except Exception as e:
        app.logger.error(f"登录异常: {str(e)}", exc_info=True)
        return jsonify({"error": "登录失败"}), 500

# 注册接口
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

# 获取用户数据接口
@app.route('/api/my-data', methods=['GET', 'OPTIONS'])
@jwt_required()
def get_user_data():
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    try:
        student_id = request.args.get('id')
        current_user_id = get_jwt_identity()
        
        query_id = student_id if (current_user_id.startswith('admin') and student_id) else current_user_id
        
        user = User.query.options(
            db.joinedload(User.synthesis_grades),
            db.joinedload(User.homework_statistic),
            db.joinedload(User.exam_statistic),
            db.joinedload(User.discussion_participation),
            db.joinedload(User.video_watching_details),
            db.joinedload(User.offline_grades)
        ).get(query_id)
        
        if not user:
            app.logger.warning(f"用户数据查询失败 - 无效用户ID: {current_user_id}")
            return jsonify({'error': '用户不存在'}), 404

        homework = user.homework_statistic[0] if user.homework_statistic else HomeworkStatistic()
        exam = user.exam_statistic[0] if user.exam_statistic else ExamStatistic(score=0)
        synthesis = user.synthesis_grades[0] if user.synthesis_grades else SynthesisGrade(comprehensive_score=0)
        
        exam = ExamStatistic.query.filter_by(id=user.id).first() or ExamStatistic(score=0)
        synthesis = SynthesisGrade.query.filter_by(id=user.id).first() or SynthesisGrade(comprehensive_score=0)
        discussion = DiscussionParticipation.query.filter_by(id=user.id).first()
        video_watching = VideoWatchingDetail.query.filter_by(id=user.id).first()
        offline_grade = OfflineGrade.query.filter_by(id=user.id).first()
        
        # 提取作业成绩计算逻辑
        def get_homework_scores(hw):
            return [
                getattr(hw, 'score2', 0) if hw else 0,
                getattr(hw, 'score3', 0) if hw else 0,
                getattr(hw, 'score4', 0) if hw else 0,
                getattr(hw, 'score5', 0) if hw else 0,
                getattr(hw, 'score6', 0) if hw else 0,
                getattr(hw, 'score7', 0) if hw else 0,
                getattr(hw, 'score8', 0) if hw else 0,
                getattr(hw, 'score9', 0) if hw else 0
            ]

        homework_scores = get_homework_scores(homework)
        missing_hw_count = sum(1 for score in homework_scores if score == 0)
        eligible_for_exam = missing_hw_count < 4
        
        # 计算排名
        all_scores = [s.comprehensive_score for s in SynthesisGrade.query.all()]
        all_scores_sorted = sorted(all_scores, reverse=True)
        rank = all_scores_sorted.index(synthesis.comprehensive_score) + 1 if synthesis else 0
        return jsonify({
            'user': {
                'id': user.id,
                'name': user.name
            },
            'scores': {
                'comprehensive': synthesis.comprehensive_score if synthesis else 0,
                'course_points': synthesis.course_points if synthesis else 0,
                'homework': homework_scores,
                'missing_homework_count': missing_hw_count,
                'eligible_for_exam': eligible_for_exam,
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
            },
            'rank': rank,
            'total_students': len(all_scores_sorted)
        }), 200
    except Exception as e:
        app.logger.error(f'数据查询失败: {str(e)}')
        return jsonify({'error': '获取数据失败', 'detail': str(e)}), 500



# 用户图表可视化数据接口
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



# 管理员数据看板接口
@app.route('/api/admin-stats', methods=['GET', 'OPTIONS'])
@jwt_required()
def get_admin_dashboard_stats():
    if request.method == 'OPTIONS':
        response = _build_cors_preflight_response()
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response
    
    try:
        # 验证管理员权限
        current_user_id = get_jwt_identity()
        print(f'[get_admin_dashboard_stats] 当前管理员ID: {current_user_id}')
        
        # 获取排序参数
        sort_by = request.args.get('sort_by', 'comprehensive_score')
        sort_order = request.args.get('sort_order', 'desc')
        print(f'[get_admin_dashboard_stats] 排序参数: sort_by={sort_by}, sort_order={sort_order}')
        
        # 使用单个查询获取所有统计数据（排除管理员用户）
        stats = db.session.query(
            db.func.count(User.id).label('user_count'),
            db.func.avg(SynthesisGrade.comprehensive_score).label('avg_comprehensive_score'),
            db.func.max(SynthesisGrade.comprehensive_score).label('max_comprehensive_score'),
            db.func.min(SynthesisGrade.comprehensive_score).label('min_comprehensive_score'),
            db.func.avg(ExamStatistic.score).label('avg_exam_score'),
            db.func.max(ExamStatistic.score).label('max_exam_score'),
            db.func.min(ExamStatistic.score).label('min_exam_score'),
            db.func.sum(
                db.case(
                    (DiscussionParticipation.total_discussions > 3, 1),
                    else_=0
                )
            ).label('active_users')
        ).filter(User.role != 'admin')\
         .join(SynthesisGrade, User.id == SynthesisGrade.id, isouter=True)\
         .join(ExamStatistic, User.id == ExamStatistic.id, isouter=True)\
         .join(DiscussionParticipation, User.id == DiscussionParticipation.id, isouter=True)\
         .first()
        
        print(f'[get_admin_dashboard_stats] 数据库查询结果: {stats}')
        
        # 获取所有学生数据（排除管理员）
        query = db.session.query(
            User.id,
            User.name,
            User.phone_number,
            SynthesisGrade.comprehensive_score,
            ExamStatistic.score.label('exam_score'),
            DiscussionParticipation.total_discussions
        ).filter(User.role != 'admin')\
         .join(SynthesisGrade, User.id == SynthesisGrade.id, isouter=True)\
         .join(ExamStatistic, User.id == ExamStatistic.id, isouter=True)\
         .join(DiscussionParticipation, User.id == DiscussionParticipation.id, isouter=True)
        
        # 添加搜索条件
        search_id = request.args.get('search_id')
        search_name = request.args.get('search_name')
        
        if search_id:
            query = query.filter(User.id.like(f'%{search_id}%'))
        if search_name:
            query = query.filter(User.name.like(f'%{search_name}%'))
        
        # 应用排序
        if sort_by == 'comprehensive_score':
            query = query.order_by(SynthesisGrade.comprehensive_score.desc() if sort_order == 'desc' else SynthesisGrade.comprehensive_score.asc())
        elif sort_by == 'exam_score':
            query = query.order_by(ExamStatistic.score.desc() if sort_order == 'desc' else ExamStatistic.score.asc())
        elif sort_by == 'activity':
            query = query.order_by(DiscussionParticipation.total_discussions.desc() if sort_order == 'desc' else DiscussionParticipation.total_discussions.asc())
        
        students = query.all()
        
        # 获取成绩分布（排除管理员）
        score_distribution = db.session.query(
            db.case(
                (SynthesisGrade.comprehensive_score >= 90, '优秀'),
                (SynthesisGrade.comprehensive_score >= 80, '良好'),
                (SynthesisGrade.comprehensive_score >= 70, '中等'),
                (SynthesisGrade.comprehensive_score >= 60, '及格'),
                (db.true(), '不及格'),
                else_='不及格'
            ).label('level'),
            db.func.count().label('count')
        ).filter(User.role != 'admin')\
         .join(User, User.id == SynthesisGrade.id)\
         .group_by(db.case(
            (SynthesisGrade.comprehensive_score >= 90, '优秀'),
            (SynthesisGrade.comprehensive_score >= 80, '良好'),
            (SynthesisGrade.comprehensive_score >= 70, '中等'),
            (SynthesisGrade.comprehensive_score >= 60, '及格'),
            (db.true(), '不及格'),
            else_='不及格'
        )).all()
        # 构建标准化响应
        response_data = {
            "status": 0,
            "msg": "获取管理员数据成功",
            "data": {
                "userCount": stats.user_count or 0,
                "avgComprehensiveScore": float(stats.avg_comprehensive_score) if stats and stats.avg_comprehensive_score else 0,
                "maxComprehensiveScore": float(stats.max_comprehensive_score) if stats and stats.max_comprehensive_score else 0,
                "minComprehensiveScore": float(stats.min_comprehensive_score) if stats and stats.min_comprehensive_score else 0,
                "avgExamScore": float(stats.avg_exam_score) if stats and stats.avg_exam_score else 0,
                "maxExamScore": float(stats.max_exam_score) if stats and stats.max_exam_score else 0,
                "minExamScore": float(stats.min_exam_score) if stats and stats.min_exam_score else 0,
                "scoreDistribution": {level: count for level, count in score_distribution} if score_distribution else {},
                "activeUsers": stats.active_users or 0,
                "inactiveUsers": (stats.user_count or 0) - (stats.active_users or 0),
                "students": [{
                    "id": student.id,
                    "name": student.name,
                    "phone_number": student.phone_number or '0',
                    "comprehensive_score": student.comprehensive_score or 0,
                    "exam_score": student.exam_score or 0
                } for student in students]
            }
        }
        
        response = jsonify(response_data)
        _add_cors_headers(response)
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        return response, 200
    except Exception as e:
        app.logger.error(f"获取管理员数据失败: {str(e)}", exc_info=True)
        app.logger.error(f"当前用户ID: {current_user_id}")
        app.logger.error(f"排序参数: sort_by={sort_by}, sort_order={sort_order}")
        response = jsonify({"status": 1, "msg": f"获取管理员数据失败: {str(e)}"})
        _add_cors_headers(response)
        return response, 500



@app.route('/api/ml/predict-grade', methods=['POST', 'OPTIONS'])
@jwt_required(optional=True)
def predict_grade():
    """预测学生成绩"""
    if request.method == 'OPTIONS':
        response = _build_cors_preflight_response()
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response
    
    try:
        from ml_services import GradePredictionModel
        
        data = request.get_json()
        student_id = data.get('student_id')
        
        if not student_id:
            response = jsonify({'error': '缺少学生ID'})
            _add_cors_headers(response)
            return response, 400
        
        # 获取用户数据
        user = User.query.options(
            db.joinedload(User.synthesis_grades),
            db.joinedload(User.homework_statistic),
            db.joinedload(User.exam_statistic),
            db.joinedload(User.discussion_participation),
            db.joinedload(User.video_watching_details)
        ).get(student_id)
        
        if not user:
            response = jsonify({'error': '用户不存在'})
            _add_cors_headers(response)
            return response, 404
        
        # 训练并预测
        predictor = GradePredictionModel()
        all_users = User.query.filter(User.role != 'admin').options(
            db.joinedload(User.synthesis_grades),
            db.joinedload(User.homework_statistic),
            db.joinedload(User.discussion_participation),
            db.joinedload(User.video_watching_details)
        ).all()
        
        if predictor.train_model(all_users):
            prediction = predictor.predict_grade(user)
            if prediction:
                response = jsonify({
                    'success': True,
                    'prediction': prediction
                })
                _add_cors_headers(response)
                return response
        
        response = jsonify({'error': '预测失败'})
        _add_cors_headers(response)
        return response, 500
        
    except Exception as e:
        app.logger.error(f'成绩预测失败: {str(e)}')
        response = jsonify({'error': '服务暂时不可用'})
        _add_cors_headers(response)
        return response, 500

@app.route('/api/ml/cluster-analysis', methods=['GET', 'OPTIONS'])
@jwt_required(optional=True)
def cluster_analysis():
    """学习行为聚类分析"""
    if request.method == 'OPTIONS':
        response = _build_cors_preflight_response()
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        return response
    
    try:
        from ml_services import LearningBehaviorClustering
        
        # 获取所有用户数据（排除管理员）
        users = User.query.filter(User.role != 'admin').options(
            db.joinedload(User.synthesis_grades),
            db.joinedload(User.homework_statistic),
            db.joinedload(User.discussion_participation),
            db.joinedload(User.video_watching_details)
        ).all()
        
        if len(users) < 3:
            response = jsonify({'error': f'数据量不足进行聚类分析，当前有{len(users)}个用户，至少需要3个'})
            _add_cors_headers(response)
            return response, 400
        
        clustering = LearningBehaviorClustering()
        if clustering.train_model(users):
            analysis = clustering.get_all_clusters_analysis(users)
            if analysis:
                response = jsonify({
                    'success': True,
                    'analysis': analysis
                })
                _add_cors_headers(response)
                return response
        
        response = jsonify({'error': '聚类分析失败'})
        _add_cors_headers(response)
        return response, 500
        
    except Exception as e:
        app.logger.error(f'聚类分析失败: {str(e)}')
        response = jsonify({'error': '服务暂时不可用'})
        _add_cors_headers(response)
        return response, 500

@app.route('/api/ml/recommendations', methods=['POST', 'OPTIONS'])
@jwt_required(optional=True)
def get_recommendations():
    """获取个性化推荐"""
    if request.method == 'OPTIONS':
        response = _build_cors_preflight_response()
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response
    
    try:
        from ml_services import PersonalizedRecommendation
        
        data = request.get_json()
        student_id = data.get('student_id')
        
        if not student_id:
            response = jsonify({'error': '缺少学生ID'})
            _add_cors_headers(response)
            return response, 400
        
        user = User.query.options(
            db.joinedload(User.synthesis_grades),
            db.joinedload(User.homework_statistic),
            db.joinedload(User.discussion_participation),
            db.joinedload(User.video_watching_details)
        ).get(student_id)
        
        if not user:
            response = jsonify({'error': '用户不存在'})
            _add_cors_headers(response)
            return response, 404
        
        recommender = PersonalizedRecommendation()
        recommendations = recommender.generate_personalized_recommendations(user)
        
        if recommendations:
            response = jsonify({
                'success': True,
                'recommendations': recommendations
            })
            _add_cors_headers(response)
            return response
        
        response = jsonify({'error': '推荐生成失败'})
        _add_cors_headers(response)
        return response, 500
        
    except Exception as e:
        app.logger.error(f'推荐生成失败: {str(e)}')
        response = jsonify({'error': '服务暂时不可用'})
        _add_cors_headers(response)
        return response, 500

@app.route('/api/ml/anomaly-detection', methods=['GET', 'OPTIONS'])
@jwt_required(optional=True)
def anomaly_detection():
    """异常行为检测"""
    if request.method == 'OPTIONS':
        response = _build_cors_preflight_response()
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        return response
    
    try:
        from ml_services import AnomalyDetector
        
        users = User.query.filter(User.role != 'admin').options(
            db.joinedload(User.synthesis_grades),
            db.joinedload(User.homework_statistic),
            db.joinedload(User.discussion_participation),
            db.joinedload(User.video_watching_details)
        ).all()
        
        if len(users) < 3:
            response = jsonify({'error': f'数据量不足进行异常检测，当前有{len(users)}个用户，至少需要3个'})
            _add_cors_headers(response)
            return response, 400
        
        detector = AnomalyDetector()
        if detector.train_model(users):
            results = detector.batch_detect_anomalies(users)
            if results:
                response = jsonify({
                    'success': True,
                    'results': results
                })
                _add_cors_headers(response)
                return response
        
        response = jsonify({'error': '异常检测失败'})
        _add_cors_headers(response)
        return response, 500
        
    except Exception as e:
        app.logger.error(f'异常检测失败: {str(e)}')
        response = jsonify({'error': '服务暂时不可用'})
        _add_cors_headers(response)
        return response, 500

@app.route('/api/ml/train-models', methods=['POST', 'OPTIONS'])
@jwt_required(optional=True)
def train_ml_models():
    """训练所有ML模型"""
    if request.method == 'OPTIONS':
        response = _build_cors_preflight_response()
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response
    
    try:
        # 验证管理员权限
        current_user_id = get_jwt_identity()
        app.logger.info(f'模型训练请求 - 用户ID: {current_user_id}')
        
        if current_user_id and not current_user_id.startswith('admin'):
            app.logger.warning(f'非管理员用户尝试训练模型: {current_user_id}')
            response = jsonify({'error': '无权限执行此操作'})
            _add_cors_headers(response)
            return response, 403
        
        app.logger.info('开始导入ML模块...')
        try:
            from ml_services import GradePredictionModel, LearningBehaviorClustering, AnomalyDetector
            app.logger.info('ML模块导入成功')
        except ImportError as e:
            app.logger.error(f'ML模块导入失败: {str(e)}')
            response = jsonify({'error': f'ML模块导入失败: {str(e)}'})
            _add_cors_headers(response)
            return response, 500
        
        app.logger.info('开始查询用户数据...')
        users = User.query.filter(User.role != 'admin').options(
            db.joinedload(User.synthesis_grades),
            db.joinedload(User.homework_statistic),
            db.joinedload(User.discussion_participation),
            db.joinedload(User.video_watching_details)
        ).all()
        
        app.logger.info(f'查询到 {len(users)} 个用户')
        
        if len(users) < 3:
            app.logger.warning(f'用户数量不足: {len(users)} < 3')
            response = jsonify({'error': f'数据量不足进行模型训练，当前有{len(users)}个用户，至少需要3个'})
            _add_cors_headers(response)
            return response, 400
        
        results = {
            'prediction_model': False,
            'clustering_model': False,
            'anomaly_model': False
        }
        
        errors = []
        
        # 训练预测模型
        app.logger.info('开始训练预测模型...')
        try:
            predictor = GradePredictionModel()
            results['prediction_model'] = predictor.train_model(users)
            app.logger.info(f'预测模型训练结果: {results["prediction_model"]}')
        except Exception as e:
            error_msg = f'预测模型训练失败: {str(e)}'
            app.logger.error(error_msg, exc_info=True)
            errors.append(error_msg)
        
        # 训练聚类模型
        app.logger.info('开始训练聚类模型...')
        try:
            clustering = LearningBehaviorClustering()
            results['clustering_model'] = clustering.train_model(users)
            app.logger.info(f'聚类模型训练结果: {results["clustering_model"]}')
        except Exception as e:
            error_msg = f'聚类模型训练失败: {str(e)}'
            app.logger.error(error_msg, exc_info=True)
            errors.append(error_msg)
        
        # 训练异常检测模型
        app.logger.info('开始训练异常检测模型...')
        try:
            detector = AnomalyDetector()
            results['anomaly_model'] = detector.train_model(users)
            app.logger.info(f'异常检测训练结果: {results["anomaly_model"]}')
        except Exception as e:
            error_msg = f'异常检测模型训练失败: {str(e)}'
            app.logger.error(error_msg, exc_info=True)
            errors.append(error_msg)
        
        success_count = sum(results.values())
        
        if success_count == 0:
            # 如果所有模型都训练失败
            app.logger.error('所有模型训练失败')
            response = jsonify({
                'error': '所有模型训练失败',
                'details': errors,
                'results': results
            })
            _add_cors_headers(response)
            return response, 500
        
        app.logger.info(f'模型训练完成: {success_count}/3 个模型成功')
        response = jsonify({
            'success': True,
            'results': results,
            'message': f'模型训练完成，成功训练 {success_count}/3 个模型',
            'errors': errors if errors else None
        })
        _add_cors_headers(response)
        return response
        
    except Exception as e:
        app.logger.error(f'模型训练过程异常: {str(e)}', exc_info=True)
        response = jsonify({
            'error': '模型训练过程异常',
            'detail': str(e)
        })
        _add_cors_headers(response)
        return response, 500

# 数据导入API接口
@app.route('/api/import-data', methods=['POST', 'OPTIONS'])
@jwt_required(optional=True)
def import_data():
    if request.method == 'OPTIONS':
        response = _build_cors_preflight_response()
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response
    
    try:
        # 验证管理员权限
        current_user_id = get_jwt_identity()
        if current_user_id and not current_user_id.startswith('admin'):
            response = jsonify({'error': '无权限执行此操作'})
            _add_cors_headers(response)
            return response, 403
            
        # 检查文件是否存在
        if 'file' not in request.files:
            response = jsonify({'error': '未上传文件'})
            _add_cors_headers(response)
            return response, 400
            
        file = request.files['file']
        if file.filename == '':
            response = jsonify({'error': '未选择文件'})
            _add_cors_headers(response)
            return response, 400
            
        # 保存临时文件
        import tempfile
        import os
        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, file.filename)
        file.save(file_path)
        
        # 根据工作表名称调用对应的导入器
        results = []
        excel_file = pd.ExcelFile(file_path)
        
        for sheet_name in excel_file.sheet_names:
            try:
                if sheet_name == '考试统计':
                    from backend.database_import.exam_statistic_importer import import_exam_statistics
                    import_exam_statistics(file_path)
                    results.append({'sheet': sheet_name, 'success': True, 'message': '导入成功'})
                elif sheet_name == '作业统计':
                    from backend.database_import.homework_statistic_importer import import_homework_statistics
                    import_homework_statistics(file_path)
                    results.append({'sheet': sheet_name, 'success': True, 'message': '导入成功'})
                elif sheet_name == '讨论参与':
                    from backend.database_import.discussion_importer import import_discussion_data
                    import_discussion_data(file_path)
                    results.append({'sheet': sheet_name, 'success': True, 'message': '导入成功'})
                else:
                    results.append({'sheet': sheet_name, 'success': False, 'message': '不支持的工作表类型'})
            except Exception as e:
                app.logger.error(f'工作表{sheet_name}导入失败: {str(e)}', exc_info=True)
                results.append({'sheet': sheet_name, 'success': False, 'message': f'导入失败: {str(e)}'})
        
        # 清理临时文件
        try:
            os.remove(file_path)
            os.rmdir(temp_dir)
        except Exception as e:
            app.logger.warning(f'临时文件清理失败: {str(e)}')
        
        response = jsonify({
            'success': True,
            'message': '文件处理完成',
            'results': results
        })
        _add_cors_headers(response)
        return response
        
    except Exception as e:
        app.logger.error(f'数据导入异常: {str(e)}', exc_info=True)
        response = jsonify({'error': '数据处理失败', 'detail': str(e)})
        _add_cors_headers(response)
        return response, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)