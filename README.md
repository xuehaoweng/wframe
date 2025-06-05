# WFrame

一个轻量级的 Python Web 框架，专注于简单性和可扩展性。

## 特性

- 轻量级路由系统
- 中间件支持
- 会话管理
- JWT 认证
- CSRF 保护
- 数据库集成（SQLAlchemy）
- OpenAPI 文档
- 请求速率限制
- 错误处理

## 安装

```bash
pip install wframe
```

## 快速开始

1. 创建新项目：

```bash
wframe new myapp
cd myapp
```

2. 运行应用：

```bash
wframe run
```

## 示例代码

```python
from wframe import WebFramework, Response
from wframe.security import token_required

app = WebFramework()

@app.route('/')
def index(request):
    return Response('Hello, WFrame!')

@app.route('/api/profile')
@token_required
def profile(request):
    return Response({
        'username': request.user.username
    })

if __name__ == '__main__':
    app.run()
```

## 主要功能

### 路由

```python
@app.route('/users/<id>', methods=['GET', 'POST'])
def user(request, id):
    return Response(f'User {id}')
```

### 中间件

```python
def logger_middleware(request):
    print(f'Request: {request.method} {request.path}')
    return request

app.use(logger_middleware)
```

### 数据库

```python
from wframe.models import User

@app.route('/users')
def users(request):
    db = next(get_db())
    users = db.query(User).all()
    return Response([user.username for user in users])
```

### 认证

```python
@app.route('/login', methods=['POST'])
def login(request):
    data = json.loads(request.get_data())
    token = create_access_token({'username': data['username']})
    return Response({'token': token})
```

## 文档

访问 `http://localhost:5000/docs` 查看 API 文档。

## 许可证

MIT License 