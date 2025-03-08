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

class VisitLog(db.Model):
    __tablename__ = 'visit_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    visit_time = db.Column(db.DateTime, default=db.func.current_timestamp())

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), unique=True, comment='学号')
    name = db.Column(db.String(50), comment='姓名')
    course = db.Column(db.String(100), comment='课程名称')
    score = db.Column(db.Float, comment='考试成绩')
    submit_time = db.Column(db.DateTime, default=db.func.current_timestamp(), comment='提交时间')

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        new_user = User(username=data['username'], password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "注册成功"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        user = User.query.filter_by(username=data['username']).first()
        
        if not user or not bcrypt.check_password_hash(user.password, data['password']):
            return jsonify({"error": "用户名或密码错误"}), 401

                # 暂时移除登录日志记录
        # new_log = VisitLog(user_id=user.id)
        # db.session.add(new_log)
        # db.session.commit()

        return jsonify({
            "message": "登录成功",
            "username": user.username,
            "token": jwt.encode({'user_id': user.id, 'exp': datetime.utcnow() + timedelta(hours=1)}, os.getenv('SECRET_KEY'), algorithm='HS256')
        }), 200
    except Exception as e:
        return jsonify({"error": "登录失败"}), 500

@app.route('/api/data', methods=['GET'])
def get_chart_data():
    from sqlalchemy import func, extract
    # 获取最近6个月数据
    monthly_data = db.session.query(
        func.date_format(VisitLog.visit_time, '%Y-%m').label('month'),
        func.count(VisitLog.id)
    ).group_by('month').order_by(func.year(VisitLog.visit_time), func.month(VisitLog.visit_time)).limit(6).all()

    return jsonify({
        "stats": {
            "totalUsers": User.query.count(),
            "todayVisits": VisitLog.query.filter(func.date(VisitLog.visit_time) == func.curdate()).count()
        },
        "chartData": {
            "months": [item[0] for item in monthly_data],
            "values": [item[1] for item in monthly_data]
        }
    })
@app.route('/api/import', methods=['POST'])
def import_data():
    try:
        if 'file' not in request.files:
            return jsonify({'error': '未选择文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '空文件名'}), 400
        
        df = pd.read_excel(file)
        for _, row in df.iterrows():
            student = Student(
                student_id=row['学号'],
                name=row['姓名'],
                course=row['课程名称'],
                score=row['考试成绩']
            )
            db.session.add(student)
        db.session.commit()
        return jsonify({'message': f'成功导入{len(df)}条数据'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# 确保在应用上下文中创建数据库表
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)