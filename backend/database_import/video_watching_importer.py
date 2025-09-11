import sys
import os
from sqlalchemy.exc import IntegrityError, DataError
import pandas as pd
from datetime import datetime

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
sys.path.append(project_root)
from backend.app import db, VideoWatchingDetail, app


def import_video_watching_details(file_path):
    try:
        df = pd.read_excel(file_path,
                         sheet_name='音视频观看详情',
                         header=4,
                         usecols=[0, 1, 8, 9, 12, 13, 16, 17, 20, 21, 24, 25, 28, 29, 32, 33],
                         names=[
                             'name', 'id',
                             'rumination_ratio1', 'watch_duration1',
                             'rumination_ratio2', 'watch_duration2',
                             'rumination_ratio3', 'watch_duration3',
                             'rumination_ratio4', 'watch_duration4',
                             'rumination_ratio5', 'watch_duration5',
                             'rumination_ratio6', 'watch_duration6',
                             'rumination_ratio7', 'watch_duration7'

                         ])

        print('前3行数据:')
        print(df.head(3))

        df['id'] = df['id'].astype(str).str.replace(r'[^\d]', '', regex=True)
        df = df[df['id'].str.len() > 0]

        score_columns = ['rumination_ratio1', 'watch_duration1',
                        'rumination_ratio2', 'watch_duration2',
                        'rumination_ratio3', 'watch_duration3',
                        'rumination_ratio4', 'watch_duration4',
                        'rumination_ratio5', 'watch_duration5',
                        'rumination_ratio6', 'watch_duration6',
                        'rumination_ratio7', 'watch_duration7']
        
        for col in score_columns:
            # 预处理特殊字符
            if 'rumination_ratio' in col:
                # 去除%符号并保留完整数值
                df[col] = df[col].astype(str).str.rstrip('%').str.strip()
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0) * 100  # 放大100倍存储
            
            elif 'watch_duration' in col:
                # 去除分钟单位并保留数值
                df[col] = df[col].astype(str).str.replace('分钟', '').str.strip()
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            # 转换前处理空字符串
            df[col] = df[col].replace(['', 'nan', 'NaT', 'None'], '0')
            
            # 安全转换为数值类型
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        print('\n前3行数值数据示例:')
        print(df[score_columns].head(3))
        print('\n有效记录数:', len(df))

        records = [
            VideoWatchingDetail(
                id=row['id'],
                name=row['name'],
                **{col: row[col] for col in score_columns}
            ) for _, row in df.iterrows()
        ]

        db.session.bulk_save_objects(records)
        db.session.commit()
        print(f"成功导入{len(records)}条音视频观看数据")

    except IntegrityError as e:
        db.session.rollback()
        print(f'主键冲突错误: {str(e)}')
    except DataError as e:
        db.session.rollback()
        print(f'数据类型错误: {str(e)}')
    except Exception as e:
        db.session.rollback()
        app.logger.exception(f'音视频数据导入异常: {str(e)}')
        print(f'系统错误: {str(e)}')
        raise


if __name__ == '__main__':
    with app.app_context():
        excel_path = os.path.join(project_root, 'data', 'BigData233-234(Python).xlsx')
        if not os.path.exists(excel_path):
            raise FileNotFoundError(f'Excel文件不存在: {excel_path}')
        import_video_watching_details(excel_path)