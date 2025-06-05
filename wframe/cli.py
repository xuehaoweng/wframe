import os
import click
from pathlib import Path
from marshmallow import Schema, fields

@click.group()
def main():
    """WFrame - 一个轻量级的 Python Web 框架"""
    pass

@main.command()
@click.argument('project_name')
def new(project_name):
    """创建一个新的 WFrame 项目"""
    # 创建项目目录
    os.makedirs(project_name, exist_ok=True)
    os.makedirs(os.path.join(project_name, 'static'), exist_ok=True)
    
    # 创建基本文件结构
    files = {
        'app.py': '''from wframe import WebFramework, Response
from wframe.security import token_required
from wframe.models import User, get_db
from marshmallow import Schema, fields

# 定义响应模式
class ProfileResponseSchema(Schema):
    username = fields.Str(required=True)

app = WebFramework()

@app.route('/')
def index(request):
    return Response('Hello, WFrame!')

@app.route('/api/profile', methods=['GET'], schema=ProfileResponseSchema)
@token_required
def profile(request):
    return Response({
        'username': request.user.username
    })

if __name__ == '__main__':
    app.run()
''',
        'requirements.txt': '''wframe>=0.1.9
''',
        '.env': '''DATABASE_URL=sqlite:///app.db
SECRET_KEY=your-secret-key-here
''',
        '.gitignore': '''__pycache__/
*.pyc
.env
*.db
sessions/
''',
        'static/swagger-ui.html': '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>WFrame API Documentation</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@4.1.3/swagger-ui.css">
    <style>
        body {
            margin: 0;
            background: #fafafa;
        }
        .swagger-ui .topbar {
            background-color: #2c3e50;
        }
        .swagger-ui .topbar .download-url-wrapper .select-label {
            color: #fff;
        }
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@4.1.3/swagger-ui-bundle.js"></script>
    <script>
        window.onload = function() {
            const ui = SwaggerUIBundle({
                url: "/openapi.json",
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIBundle.SwaggerUIStandalonePreset
                ],
                plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl
                ],
                layout: "BaseLayout",
                syntaxHighlight: {
                    activated: true,
                    theme: "monokai"
                }
            });
            window.ui = ui;
        };
    </script>
</body>
</html>'''
    }
    
    for filename, content in files.items():
        filepath = os.path.join(project_name, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    click.echo(f'项目 {project_name} 创建成功！')
    click.echo(f'cd {project_name}')
    click.echo('python app.py')

@main.command()
def run():
    """运行 WFrame 应用"""
    if not os.path.exists('app.py'):
        click.echo('错误：未找到 app.py 文件')
        return
    
    os.system('python app.py')

if __name__ == '__main__':
    main() 