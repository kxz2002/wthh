"""
Session 认证实现
"""
from flask import session, request
from flask_login import LoginManager
from core.auth.base import TokenManager
from core.user import User
from core.database import db

# Flask-Login 配置
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = '请先登录'

@login_manager.user_loader
def load_user(user_id):
    """加载用户"""
    return User.query.get(int(user_id))

class SessionTokenManager(TokenManager):
    """基于 Session 的 Token 管理器"""
    
    def __init__(self, app=None):
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """初始化应用"""
        login_manager.init_app(app)
    
    def create_token(self, user_id: int) -> str:
        """Session 不需要手动创建 token"""
        return session.get('_user_id')
    
    def verify_token(self, token: str) -> int:
        """Session 不需要验证 token"""
        user_id = session.get('_user_id')
        return int(user_id) if user_id else None
    
    def delete_token(self, token: str):
        """删除 Session"""
        session.clear()
    
    def get_user_id_from_request(self, request) -> int:
        """从 Session 获取用户 ID"""
        return session.get('_user_id')
