import sys
import os
from sqlalchemy.exc import IntegrityError, DataError
import pandas as pd
from datetime import datetime

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
sys.path.append(project_root)
from backend.app import db, ExamStatistic, app


def import_exam_statistics(file_path):
    try:
        df = pd.read_excel(file_path,
                         sheet_name='考试统计',
                         header=3,
                         usecols=[1,0,6],
                         names=['name', 'id', 'score'])

        # 数据清洗
        print('原始数据格式:')
        print(f'列名: {df.columns.tolist()}')
        print('前3行数据:')
        print(df.head(3))

        df['id'] = df['id'].astype(str).str.replace(r'[^\d]', '', regex=True)
        df = df[df['id'].str.len() > 0]
        df['score'] = pd.to_numeric(df['score'], errors='coerce').fillna(0).clip(0, 100)

        records = [
            ExamStatistic(
                id=row['id'],
                name=row['name'],
                score=row['score']
            ) for _, row in df.iterrows()
        ]

        db.session.bulk_save_objects(records)
        db.session.commit()
        print(f"成功导入{len(records)}条考试统计数据")

    except IntegrityError as e:
        db.session.rollback()
        print(f'主键冲突错误: {str(e)}')
    except DataError as e:
        db.session.rollback()
        print(f'数据类型错误: {str(e)}')
    except Exception as e:
        db.session.rollback()
        app.logger.exception(f'考试统计导入异常: {str(e)}')
        print(f'系统错误: {str(e)}')
        raise


if __name__ == '__main__':
    with app.app_context():
        excel_path = os.path.join(project_root, 'data', 'BigData233-234(Python).xlsx')
        if not os.path.exists(excel_path):
            raise FileNotFoundError(f'Excel文件不存在: {excel_path}')
        import_exam_statistics(excel_path)