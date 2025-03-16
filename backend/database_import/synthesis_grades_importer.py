from sqlalchemy.exc import IntegrityError, DataError, DatabaseError
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
sys.path.append(project_root)
from flask import current_app
from backend.app import db, OfflineGrade, app, SynthesisGrade
import pandas as pd

def import_synthesis_grades(file_path):
    try:
        df = pd.read_excel(file_path, sheet_name='综合成绩', header=2)
        
        df = df.rename(columns={
            '学号/工号': '学号',
            '课程积分(100%)': 'course_points',
            '综合成绩': 'comprehensive_score'
        })
        
        df = df.where(pd.notnull(df), None)
        df['学号'] = df['学号'].astype(str).str.replace(r'[^\d]', '', regex=True)

        # 转换为浮点型数据并处理异常值
        df['course_points'] = pd.to_numeric(df['course_points'], errors='coerce').fillna(0.0).astype(float)
        df['comprehensive_score'] = pd.to_numeric(df['comprehensive_score'], errors='coerce').fillna(0.0).astype(float)
        
        # 数据校验
        if df['学号'].isnull().any():
            raise ValueError("学号字段存在空值")
        if (df['comprehensive_score'] < 0).any() or (df['comprehensive_score'] > 100).any():
            raise ValueError("综合成绩超出合理范围(0-100)")

        records = [
            SynthesisGrade(
                id=row['学号'],
                name=row['学生姓名'],
                course_points=row['course_points'],
                comprehensive_score=row['comprehensive_score']
            ) for _, row in df.iterrows()
        ]

        db.session.bulk_save_objects(records)
        db.session.commit()
        print(f'成功导入 {len(records)} 条综合成绩数据')

    except (IntegrityError, DataError, DatabaseError) as e:
        db.session.rollback()
        app.logger.error(f'数据冲突: {str(e)}，受影响记录: {record.__dict__ if 'record' in locals() else '未知'}')
        print(f'详细错误: {e.orig.args[1] if hasattr(e, "orig") else str(e)}')
    except ValueError as e:
        db.session.rollback()
        current_app.logger.warning(f'数据校验失败: {str(e)}')
        print(f'数据问题: {str(e)}')
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception("未预期错误")
        print(f'系统异常: {str(e)}')
        raise
    except Exception as e:
        print(f'导入失败: {str(e)}')

if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
    excel_path = os.path.join(project_root, 'data', 'BigData233-234(Python).xlsx')
    with app.app_context():
        import_synthesis_grades(excel_path)