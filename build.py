import os
import shutil
from pathlib import Path

def build():
    """构建 WFrame 包"""
    # 清理旧的构建文件
    for dir_name in ['dist', 'build', 'wframe.egg-info']:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
    
    # 创建 wframe 包目录
    os.makedirs('wframe', exist_ok=True)
    
    # 复制核心文件
    files_to_copy = [
        'framework.py',
        'security.py',
        'models.py',
        'cli.py'
    ]
    
    for file in files_to_copy:
        shutil.copy2(file, f'wframe/{file}')
    
    # 创建 __init__.py
    with open('wframe/__init__.py', 'w', encoding='utf-8') as f:
        f.write('''from .framework import WebFramework, Response
from .security import token_required
from .models import User, get_db

__version__ = "0.1.9"
''')
    
    # 构建包
    os.system('python setup.py sdist bdist_wheel')
    
    print("\n构建完成！")
    print("\n要发布到 PyPI，请运行：")
    print("twine upload dist/*")

if __name__ == '__main__':
    build() 