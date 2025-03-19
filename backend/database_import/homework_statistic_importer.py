from sqlalchemy.exc import IntegrityError, DataError
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
sys.path.append(project_root)
from backend.app import db, HomeworkStatistic, app, User
import pandas as pd
from datetime import datetime

def import_homework_statistics(file_path):
    try:
        df = pd.read_excel(file_path,
                         sheet_name='作业统计',
                         header=3,
                         usecols=[0,1,6,9,12,15,18,21,24,27], 
                         names=[
                             'name', 'id', 
                             'score2', 'score3', 'score4', 'score5',
                             'score6', 'score7', 'score8', 'score9'
                         ])
        print('原始数据格式:')
        print(f'列名: {df.columns.tolist()}')
        print('前3行数据:')
        print(df.head(3))
  
        # 数据清洗与转换
        df['id'] = df['id'].astype(str).str.replace(r'[^\d]', '', regex=True)
        print('清洗后数据样本:')
        print(df[['id', 'name']].head(5))
        df = df[df['id'].str.len() > 0]
        print(f'有效记录数: {len(df)}')
        
        # 转换分数列为数值类型
        score_columns = ['score2','score3','score4','score5','score6','score7','score8','score9']
        for col in score_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).clip(0, 100)
        
        # 构建记录并批量插入
        records = [
            HomeworkStatistic(
                id=row['id'],
                name=row['name'],
                **{col: row[col] for col in score_columns}
            ) for _, row in df.iterrows()
        ]
        
        db.session.bulk_save_objects(records)
        db.session.commit()
        print(f'成功导入 {len(records)} 条作业统计数据')

    except IntegrityError as e:
        db.session.rollback()
        print(f'数据库错误: {str(e)}')
    except Exception as e:
        db.session.rollback()
        app.logger.exception(f'作业统计导入异常: {str(e)}')
        print(f'系统错误: {str(e)}')
        raise

if __name__ == '__main__':
    with app.app_context():
        excel_path = os.path.join(project_root, 'data', 'BigData233-234(Python).xlsx')
        if not os.path.exists(excel_path):
            raise FileNotFoundError(f'Excel文件不存在: {excel_path}')
        import_homework_statistics(excel_path)
