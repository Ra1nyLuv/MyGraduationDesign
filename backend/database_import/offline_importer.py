from sqlalchemy.exc import IntegrityError, DataError
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
sys.path.append(project_root)
from backend.app import db, OfflineGrade, app
import pandas as pd
# 根据xlsx中的工作表'线下成绩统计', 导入线下成绩数据
def import_offline_grades(file_path):
    try:
        df = pd.read_excel(file_path, sheet_name='线下成绩统计', header=2)

        # 字段映射与清洗
        df = df.rename(columns={
            '学号/工号': '学号',
            '综合成绩': 'comprehensive_score'
        })

        df = df.where(pd.notnull(df), None)
        df['学号'] = df['学号'].astype(str).str.replace(r'[^\d]', '', regex=True)

        # 数值转换与校验
        df['comprehensive_score'] = pd.to_numeric(df['comprehensive_score'], 
                                                 errors='coerce').fillna(0.0).clip(0, 100)

        # 唯一性校验
        duplicates = df[df.duplicated('学号', keep=False)]
        if not duplicates.empty:
            raise ValueError(f"发现重复学号: {duplicates['学号'].tolist()}")

        records = [
            OfflineGrade(
                id=row['学号'],
                name=row['学生姓名'],
                comprehensive_score=row['comprehensive_score']
            ) for _, row in df.iterrows()
        ]

        db.session.bulk_save_objects(records)
        db.session.commit()
        print(f'成功导入 {len(records)} 条线下成绩数据')

    except IntegrityError as e:
        db.session.rollback()
        app.logger.error(f'唯一性约束冲突: {str(e)}')
        print(f'错误: 学号已存在 - {e.orig.args[1]}')
    except ValueError as e:
        db.session.rollback()
        app.logger.warning(f'数据校验失败: {str(e)}')
        print(f'校验错误: {str(e)}')
    except Exception as e:
        db.session.rollback()
        app.logger.exception('线下成绩导入异常')
        print(f'系统错误: {str(e)}')
        raise

if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
    excel_path = os.path.join(project_root, 'data', 'BigData233-234(Python).xlsx')
    
    with app.app_context():
        import_offline_grades(excel_path)