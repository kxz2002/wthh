"""
用户仓库
"""
from core.user import User
from core.database import db

class UserRepository:
    """用户仓库"""
    
    @staticmethod
    def create(username: str, password: str, role: str = 'user') -> User:
        """创建用户"""
        user = User(username=username, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user
    
    @staticmethod
    def get_by_id(user_id: int) -> User:
        """根据 ID 获取用户"""
        return User.query.get(user_id)
    
    @staticmethod
    def get_by_username(username: str) -> User:
        """根据用户名获取用户"""
        return User.query.filter_by(username=username).first()
    
    @staticmethod
    def verify_password(username: str, password: str) -> User:
        """验证用户名密码"""
        user = UserRepository.get_by_username(username)
        if user and user.check_password(password):
            return user
        return None
    
    @staticmethod
    def get_all(role: str = None, page: int = 1, per_page: int = 20):
        """获取所有用户"""
        query = User.query
        if role:
            query = query.filter_by(role=role)
        return query.order_by(User.created_at.desc()).paginate(page=page, per_page=per_page)
    
    @staticmethod
    def delete(user_id: int) -> bool:
        """删除用户"""
        user = UserRepository.get_by_id(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            return True
        return False
