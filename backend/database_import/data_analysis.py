import pandas as pd

try:
    excel_path = 'data/BigData233-234(Python).xlsx'
    xls = pd.ExcelFile(excel_path)
    
    print('Excel工作簿结构:')
    print(f'共有 {len(xls.sheet_names)} 个工作表')
    
    for sheet_name in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet_name, header=2)
        print(f'\n工作表名称: {sheet_name}')
        print('列名:', df.columns.tolist())
        print('前3行数据:\n', df.head(3))

except FileNotFoundError:
    print(f'错误：文件 {excel_path} 未找到')
except Exception as e:
    print(f'读取文件时发生错误: {str(e)}')