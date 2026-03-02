"""
登录功能单元测试
"""
import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

import pytest
from apps.app_with_auth import app, db
from core.user import User


@pytest.fixture(scope='function')
def client():
    """每个测试使用独立的内存数据库"""
    # 使用内存数据库，但添加唯一的数据库名称来强制创建新的数据库
    import uuid
    db_name = f'test_{uuid.uuid4().hex}'

    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_name}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    with app.test_client() as client:
        with app.app_context():
            # 清除任何现有连接
            db.drop_all()
            db.create_all()

            # 创建测试用户
            admin = User(username='admin', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)

            user = User(username='testuser', role='user')
            user.set_password('test123')
            db.session.add(user)

            db.session.commit()

        yield client

    # 清理 - 需要在 app context 中
    with app.app_context():
        db.session.remove()
        db.engine.dispose()


@pytest.fixture
def authenticated_client(client):
    with client.session_transaction() as sess:
        sess['_user_id'] = '1'
    return client


class TestLogin:
    def test_login_page(self, client):
        response = client.get('/auth/login')
        assert response.status_code == 200

    def test_login_empty_username(self, client):
        response = client.post('/auth/login', data={'username': '', 'password': 'test123'})
        assert response.status_code == 200

    def test_login_empty_password(self, client):
        response = client.post('/auth/login', data={'username': 'admin', 'password': ''})
        assert response.status_code == 200

    def test_login_success(self, client):
        response = client.post('/auth/login', data={'username': 'admin', 'password': 'admin123'}, follow_redirects=False)
        assert response.status_code == 302  # 重定向到首页

    def test_login_wrong_password(self, client):
        response = client.post('/auth/login', data={'username': 'admin', 'password': 'wrongpass'})
        assert response.status_code == 200

    def test_login_nonexistent_user(self, client):
        response = client.post('/auth/login', data={'username': 'nonexistent', 'password': 'test123'})
        assert response.status_code == 200

    def test_sql_injection(self, client):
        response = client.post('/auth/login', data={"username": "admin' OR '1'='1", 'password': 'anything'})
        assert response.status_code == 200


class TestRegister:
    def test_register_page(self, client):
        response = client.get('/auth/register')
        assert response.status_code == 200

    def test_register_success(self, client):
        import random
        username = f'newuser{random.randint(1000,9999)}'
        response = client.post('/auth/register', data={'username': username, 'password': 'test123', 'password_confirm': 'test123'}, follow_redirects=True)
        assert response.status_code == 200

    def test_register_password_mismatch(self, client):
        response = client.post('/auth/register', data={'username': 'newuser', 'password': 'pass1', 'password_confirm': 'pass2'})
        assert response.status_code == 200

    def test_register_duplicate_username(self, client):
        response = client.post('/auth/register', data={'username': 'admin', 'password': 'test123', 'password_confirm': 'test123'})
        assert response.status_code == 200

    def test_register_short_password(self, client):
        response = client.post('/auth/register', data={'username': 'newuser', 'password': '123', 'password_confirm': '123'})
        assert response.status_code == 200


class TestProtectedRoutes:
    def test_dashboard_requires_login(self, client):
        response = client.get('/dashboard', follow_redirects=False)
        assert response.status_code in [302, 401]

    def test_dashboard_with_auth(self, authenticated_client):
        response = authenticated_client.get('/dashboard', follow_redirects=False)
        assert response.status_code == 302  # 重定向到 Vue 前端


class TestAPI:
    def test_userinfo_unauthorized(self, client):
        response = client.get('/auth/api/userinfo')
        assert response.status_code == 401

    def test_userinfo_authorized(self, authenticated_client):
        response = authenticated_client.get('/auth/api/userinfo')
        assert response.status_code == 200
        import json
        data = json.loads(response.data)
        assert 'username' in data


class TestLogout:
    def test_logout(self, authenticated_client):
        response = authenticated_client.get('/auth/logout', follow_redirects=True)
        assert response.status_code == 200


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
