from sqlalchemy.exc import IntegrityError
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from backend.app import db, bcrypt, User, app
import pandas as pd
import os

def import_users_from_excel(file_path):
    try:
        df = pd.read_excel(file_path, sheet_name='综合成绩', header=2)
        df = df.rename(columns={'学号/工号': '学号', '学生姓名': '姓名'})
        
        # 数据清洗与格式转换
        df = df.where(pd.notnull(df), None)
        df['密码'] = '1234'
        df['密码'] = df['密码'].apply(lambda x: bcrypt.generate_password_hash(x).decode('utf-8'))
        df['联系电话'] = '13900000000'

        # 批量插入
        users = [
            User(
                id=str(row['学号']).split('.')[0],
                name=row['姓名'],
                password=row['密码'],
                phone_number=str(row['联系电话'])[:11]
            )
            for _, row in df.iterrows()
        ]

        db.session.bulk_save_objects(users)
        db.session.commit()
        print(f'成功导入 {len(users)} 条用户数据')

    except IntegrityError as e:
        db.session.rollback()
        print(f'数据唯一性冲突: {str(e)}')
    except Exception as e:
        print(f'导入失败: {str(e)}')

if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
    excel_path = os.path.join(project_root, 'data', 'BigData233-234(Python).xlsx')
    with app.app_context():
        import_users_from_excel(excel_path)