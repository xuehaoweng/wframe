from framework import WebFramework, FileSystemSessionInterface
from werkzeug.wrappers import Response
from werkzeug.exceptions import NotFound, Unauthorized
from schemas import (
    UserSchema, LoginResponseSchema, LogoutResponseSchema,
    ProfileResponseSchema, CreateUserResponseSchema,
    ErrorSchema, HelloResponseSchema
)
from security import (
    hash_password, verify_password, create_access_token,
    create_refresh_token, token_required, generate_csrf_token,
    verify_csrf_token, RateLimiter
)
from models import User, init_db, get_db
import json
import time
import os

app = WebFramework()

# 配置会话接口
app.session_interface = FileSystemSessionInterface()

# 创建速率限制器
login_limiter = RateLimiter(max_requests=5, time_window=300)  # 5分钟内最多5次尝试

# 初始化数据库
init_db()

# 创建初始管理员用户
def create_admin_user():
    db = next(get_db())
    admin = db.query(User).filter(User.username == 'admin').first()
    if not admin:
        admin = User(
            username='admin',
            password=hash_password('admin123'),
            email='admin@example.com'
        )
        db.add(admin)
        db.commit()
        print("\n=== 初始用户信息 ===")
        print("用户名: admin")
        print("密码: admin123")
        print("==================\n")

# 日志中间件
def logger_middleware(request):
    start_time = time.time()
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {request.method} {request.path}")
    return request

# CSRF 中间件
def csrf_middleware(request):
    # 排除登录接口的 CSRF 验证
    if request.path == '/api/login':
        return request
        
    if request.method in ['POST', 'PUT', 'DELETE']:
        csrf_token = request.headers.get('X-CSRF-Token')
        stored_token = request.session.data.get('csrf_token')
        
        if not csrf_token or not stored_token or not verify_csrf_token(csrf_token, stored_token):
            return Response(
                json.dumps({'error': 'CSRF 验证失败'}, ensure_ascii=False),
                status=403,
                mimetype='application/json'
            )
    return request

# 性能监控中间件
def performance_middleware(request):
    start_time = time.time()
    response = request
    if isinstance(response, Response):
        process_time = time.time() - start_time
        print(f"请求处理时间: {process_time:.3f}秒")
    return response

# 注册中间件
app.use(logger_middleware)
app.use(csrf_middleware)
app.use(performance_middleware)

# 错误处理器
@app.errorhandler(404)
def not_found(error):
    """处理404错误"""
    return Response(
        json.dumps({
            'error': '页面未找到',
            'code': 404
        }, ensure_ascii=False),
        status=404,
        mimetype='application/json'
    )

@app.errorhandler(401)
def unauthorized(error):
    """处理401错误"""
    return Response(
        json.dumps({
            'error': '未授权访问',
            'code': 401
        }, ensure_ascii=False),
        status=401,
        mimetype='application/json'
    )

@app.errorhandler(500)
def internal_error(error):
    """处理500错误"""
    return Response(
        json.dumps({
            'error': '服务器内部错误',
            'code': 500
        }, ensure_ascii=False),
        status=500,
        mimetype='application/json'
    )

@app.route('/')
def index(request):
    """首页"""
    # 生成 CSRF 令牌
    csrf_token = generate_csrf_token()
    request.session.data['csrf_token'] = csrf_token
    request.session.modified = True
    
    return Response(
        json.dumps({
            'message': '欢迎使用我们的Web框架！',
            'csrf_token': csrf_token
        }, ensure_ascii=False),
        mimetype='application/json'
    )

@app.route('/api/hello/<name>', schema=HelloResponseSchema)
def hello(request, name):
    """发送问候消息"""
    data = {
        'message': f'你好, {name}!',
        'status': 'success'
    }
    return Response(
        json.dumps(data, ensure_ascii=False),
        mimetype='application/json'
    )

@app.route('/api/users', methods=['POST'], schema=CreateUserResponseSchema)
def create_user(request):
    """创建新用户"""
    data = json.loads(request.get_data())
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    
    db = next(get_db())
    if db.query(User).filter(User.username == username).first():
        return Response(
            json.dumps({'error': '用户名已存在'}, ensure_ascii=False),
            status=400,
            mimetype='application/json'
        )
    
    if email and db.query(User).filter(User.email == email).first():
        return Response(
            json.dumps({'error': '邮箱已被使用'}, ensure_ascii=False),
            status=400,
            mimetype='application/json'
        )
    
    hashed_password = hash_password(password)
    user = User(
        username=username,
        password=hashed_password,
        email=email
    )
    
    db.add(user)
    db.commit()
    
    return Response(
        json.dumps({
            'message': '用户创建成功',
            'username': username
        }, ensure_ascii=False),
        mimetype='application/json'
    )

@app.route('/api/login', methods=['POST'], schema=LoginResponseSchema)
def login(request):
    """用户登录"""
    # 检查登录尝试次数
    client_ip = request.remote_addr
    if not login_limiter.is_allowed(client_ip):
        return Response(
            json.dumps({
                'error': '登录尝试次数过多，请稍后再试'
            }, ensure_ascii=False),
            status=429,
            mimetype='application/json'
        )
    
    data = json.loads(request.get_data())
    username = data.get('username')
    password = data.get('password')
    
    db = next(get_db())
    user = db.query(User).filter(User.username == username).first()
    
    if not user or not verify_password(password, user.password):
        return Response(
            json.dumps({'error': '用户名或密码错误'}, ensure_ascii=False),
            status=401,
            mimetype='application/json'
        )
    
    # 创建访问令牌和刷新令牌
    access_token = create_access_token({'username': username})
    refresh_token = create_refresh_token({'username': username})
    
    # 存储刷新令牌
    request.session.data['refresh_token'] = refresh_token
    request.session.modified = True
    
    return Response(
        json.dumps({
            'message': '登录成功',
            'access_token': access_token,
            'refresh_token': refresh_token
        }, ensure_ascii=False),
        mimetype='application/json'
    )

@app.route('/api/refresh', methods=['POST'])
def refresh_token(request):
    """刷新访问令牌"""
    refresh_token = request.session.data.get('refresh_token')
    if not refresh_token:
        return Response(
            json.dumps({'error': '无效的刷新令牌'}, ensure_ascii=False),
            status=401,
            mimetype='application/json'
        )
    
    try:
        payload = verify_token(refresh_token)
        access_token = create_access_token({'username': payload['username']})
        return Response(
            json.dumps({
                'access_token': access_token
            }, ensure_ascii=False),
            mimetype='application/json'
        )
    except ValueError as e:
        return Response(
            json.dumps({'error': str(e)}, ensure_ascii=False),
            status=401,
            mimetype='application/json'
        )

@app.route('/api/logout', schema=LogoutResponseSchema)
@token_required
def logout(request):
    """用户退出登录"""
    request.session.data.clear()
    request.session.modified = True
    return Response(
        json.dumps({'message': '已退出登录'}, ensure_ascii=False),
        mimetype='application/json'
    )

@app.route('/api/profile', schema=ProfileResponseSchema)
@token_required
def profile(request):
    """获取用户信息"""
    username = request.user.get('username')
    db = next(get_db())
    user = db.query(User).filter(User.username == username).first()
    
    if not user:
        return Response(
            json.dumps({'error': '用户不存在'}, ensure_ascii=False),
            status=404,
            mimetype='application/json'
        )
    
    return Response(
        json.dumps({
            'username': user.username,
            'email': user.email,
            'created_at': user.created_at.isoformat(),
            'message': '获取用户信息成功'
        }, ensure_ascii=False),
        mimetype='application/json'
    )

if __name__ == '__main__':
    create_admin_user()
    app.run(debug=True) 