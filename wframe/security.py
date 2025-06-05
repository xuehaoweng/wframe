import bcrypt
import jwt
import os
import time
from datetime import datetime, timedelta
from functools import wraps
from werkzeug.wrappers import Response
import json

# 从环境变量加载密钥
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', os.urandom(24).hex())
JWT_ALGORITHM = 'HS256'
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30
JWT_REFRESH_TOKEN_EXPIRE_DAYS = 7

def hash_password(password: str) -> str:
    """使用 bcrypt 加密密码"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )

def create_access_token(data: dict) -> str:
    """创建访问令牌"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def create_refresh_token(data: dict) -> str:
    """创建刷新令牌"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def verify_token(token: str) -> dict:
    """验证令牌"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("令牌已过期")
    except jwt.JWTError:
        raise ValueError("无效的令牌")

def token_required(f):
    """令牌验证装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        request = args[0]
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return Response(
                json.dumps({'error': '缺少认证令牌'}, ensure_ascii=False),
                status=401,
                mimetype='application/json'
            )
            
        try:
            token = auth_header.split(" ")[1]
            payload = verify_token(token)
            request.user = payload
        except (IndexError, ValueError) as e:
            return Response(
                json.dumps({'error': str(e)}, ensure_ascii=False),
                status=401,
                mimetype='application/json'
            )
            
        return f(*args, **kwargs)
    return decorated

def generate_csrf_token() -> str:
    """生成 CSRF 令牌"""
    return os.urandom(32).hex()

def verify_csrf_token(token: str, stored_token: str) -> bool:
    """验证 CSRF 令牌"""
    return token == stored_token

class RateLimiter:
    """请求频率限制器"""
    def __init__(self, max_requests: int, time_window: int):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = {}
        
    def is_allowed(self, key: str) -> bool:
        """检查请求是否允许"""
        now = time.time()
        if key not in self.requests:
            self.requests[key] = []
            
        # 清理过期的请求记录
        self.requests[key] = [t for t in self.requests[key] if now - t < self.time_window]
        
        if len(self.requests[key]) >= self.max_requests:
            return False
            
        self.requests[key].append(now)
        return True 