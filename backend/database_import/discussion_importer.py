from sqlalchemy.exc import IntegrityError, DataError
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
sys.path.append(project_root)
from backend.app import db, DiscussionParticipation, app
import pandas as pd

def import_discussions_from_excel(file_path):
    try:
        excel_file = pd.ExcelFile(file_path)
        sheet_names = excel_file.sheet_names
        target_sheet = next((name for name in sheet_names if '讨论' in name), None)
        
        if not target_sheet:
            raise ValueError("Excel文件中未找到包含'讨论'关键词的工作表")
        
        df = excel_file.parse(sheet_name=target_sheet, header=2)
        
        # 字段映射与清洗
        df = df.rename(columns={
            '学号/工号': '学号',
            '总讨论数': 'total_discussions',
            '发表讨论': 'posted_discussions',
            '回复讨论': 'replied_discussions'
        })
        
        df = df.where(pd.notnull(df), None)
        # 统一学号格式处理
        df['学号'] = df['学号'].astype(str).str.replace(r'[^\d]', '', regex=True)
        df = df[df['学号'].str.len() > 0]  # 新增空学号过滤
        if df.empty:
            raise ValueError("清洗后学号字段全部为空，请检查原始数据")

        # 增强数值转换（处理异常值并设置默认值）
        int_columns = ['total_discussions', 'posted_discussions', 'replied_discussions']
        for col in int_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).clip(lower=0).astype(int)

        # 数据校验
        if df['学号'].isnull().any():
            raise ValueError("学号字段存在空值")
        if (df[int_columns] < 0).any().any():
            raise ValueError("讨论数存在负值，请检查数据源")

        # 批量插入
        records = [
            DiscussionParticipation(
                id=row['学号'],
                name=row['学生姓名'],
                total_discussions=row['total_discussions'],
                posted_discussions=row['posted_discussions'],
                replied_discussions=row['replied_discussions']
            ) for _, row in df.iterrows()
        ]

        db.session.bulk_save_objects(records)
        db.session.commit()
        print(f'成功导入 {len(records)} 条讨论数据')

    except (IntegrityError, DataError, DatabaseError) as e:
        db.session.rollback()
        current_app.logger.error(f'数据库操作失败: {str(e)} 错误记录: {row}' if 'row' in locals() else str(e))
        print(f'详细错误: {e.orig.args[1] if hasattr(e, "orig") else str(e)}')
    except ValueError as e:
        db.session.rollback()
        current_app.logger.warning(f'数据校验失败: {str(e)}')
        print(f'校验错误: {str(e)}')
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception('未处理异常')
        print(f'系统错误: {str(e)}')
        raise

if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
    excel_path = os.path.join(project_root, 'data', 'BigData233-234(Python).xlsx')
    with app.app_context():
        import_discussions_from_excel(excel_path)