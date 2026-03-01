"""
Redis Token 认证实现 (未来扩展)

当前为预留实现，需要安装 Redis 后启用
"""
import uuid
import json
from datetime import timedelta
from core.auth.base import TokenManager

class RedisTokenManager(TokenManager):
    """
    基于 Redis 的 Token 管理器
    
    切换方式：
    1. 安装 Redis
    2. 安装 redis 库: pip install redis
    3. 在 config.py 中设置 REDIS_HOST 等配置
    4. 修改 auth 初始化代码使用此类
    """
    
    def __init__(self, app=None):
        self.redis_client = None
        self.token_prefix = 'auth:token:'
        self.token_expire = app.config.get('TOKEN_EXPIRE_SECONDS', 3600 * 24 * 7) if app else 3600 * 24 * 7
    
    def _get_redis(self):
        """获取 Redis 客户端"""
        if self.redis_client is None:
            try:
                import redis
                from flask import current_app
                self.redis_client = redis.Redis(
                    host=current_app.config.get('REDIS_HOST', 'localhost'),
                    port=current_app.config.get('REDIS_PORT', 6379),
                    db=current_app.config.get('REDIS_DB', 0),
                    decode_responses=True
                )
            except ImportError:
                raise RuntimeError("请安装 redis 库: pip install redis")
        return self.redis_client
    
    def create_token(self, user_id: int) -> str:
        """创建 Token"""
        token = str(uuid.uuid4())
        redis = self._get_redis()
        key = f"{self.token_prefix}{token}"
        redis.setex(key, self.token_expire, json.dumps({'user_id': user_id}))
        return token
    
    def verify_token(self, token: str) -> int:
        """验证 Token"""
        redis = self._get_redis()
        key = f"{self.token_prefix}{token}"
        data = redis.get(key)
        if data:
            return json.loads(data).get('user_id')
        return None
    
    def delete_token(self, token: str):
        """删除 Token"""
        redis = self._get_redis()
        key = f"{self.token_prefix}{token}"
        redis.delete(key)
    
    def get_user_id_from_request(self, request) -> int:
        """从请求头获取 Token"""
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header[7:]
            return self.verify_token(token)
        return None
