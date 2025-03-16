import os
import subprocess
from datetime import datetime
from cryptography.fernet import Fernet
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 从环境变量读取配置
db_host = os.getenv('MYSQL_HOST')
db_user = os.getenv('MYSQL_USER')
db_pass = os.getenv('MYSQL_PASSWORD')
db_name = os.getenv('MYSQL_DB')

# 生成加密密钥
key = Fernet.generate_key()
cipher_suite = Fernet(key)

# 创建备份目录
backup_dir = os.path.join(os.path.dirname(__file__), 'backups')
os.makedirs(backup_dir, exist_ok=True)

# 生成带时间戳的文件名
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
backup_file = os.path.join(backup_dir, f'{db_name}_backup_{timestamp}.sql')
encrypted_file = backup_file + '.enc'

# 执行mysqldump命令
try:
    subprocess.run(
        f'mysqldump -h {db_host} -u {db_user} -p{db_pass} {db_name} > {backup_file}',
        shell=True,
        check=True
    )
    
    # 加密备份文件
    with open(backup_file, 'rb') as f:
        data = f.read()
    encrypted_data = cipher_suite.encrypt(data)
    
    with open(encrypted_file, 'wb') as f:
        f.write(encrypted_data)
    
    # 删除原始未加密文件
    os.remove(backup_file)
    
    print(f'备份成功！加密备份文件保存在：{encrypted_file}')
    print(f'请妥善保存加密密钥：{key.decode()}')

except subprocess.CalledProcessError as e:
    print(f'备份失败：{str(e)}')