import os
import sys
import click
from pathlib import Path

@click.group()
def cli():
    """Wash Web 框架命令行工具"""
    pass

@cli.command()
@click.argument('name')
def new(name):
    """创建新的 Wash 项目"""
    project_dir = Path(name)
    if project_dir.exists():
        click.echo(f"错误：目录 '{name}' 已存在")
        sys.exit(1)
        
    # 创建项目目录
    project_dir.mkdir()
    
    # 创建基本文件结构
    (project_dir / 'app.py').write_text('''from wash import WebFramework, Response

app = WebFramework()

@app.route('/')
def index(request):
    return Response('Hello, Wash!')

if __name__ == '__main__':
    app.run()
''')
    
    (project_dir / 'requirements.txt').write_text('wash>=0.1.0\n')
    
    # 创建 .gitignore
    (project_dir / '.gitignore').write_text('''__pycache__/
*.py[cod]
*$py.class
*.so
.env
.venv
env/
venv/
ENV/
.idea/
.vscode/
*.db
''')
    
    click.echo(f"项目 '{name}' 创建成功！")
    click.echo(f"cd {name}")
    click.echo("pip install -r requirements.txt")
    click.echo("python app.py")

@cli.command()
def run():
    """运行 Wash 应用"""
    if not Path('app.py').exists():
        click.echo("错误：未找到 app.py 文件")
        sys.exit(1)
        
    os.system('python app.py')

def main():
    cli() 