"""
认证基类 - 支持未来扩展到 Redis Token
"""
from abc import ABC, abstractmethod

class TokenManager(ABC):
    """Token 管理器抽象基类"""
    
    @abstractmethod
    def create_token(self, user_id: int) -> str:
        """创建 Token"""
        pass
    
    @abstractmethod
    def verify_token(self, token: str) -> int:
        """验证 Token，返回用户 ID"""
        pass
    
    @abstractmethod
    def delete_token(self, token: str):
        """删除 Token"""
        pass
    
    @abstractmethod
    def get_user_id_from_request(self, request) -> int:
        """从请求中获取用户 ID"""
        pass
