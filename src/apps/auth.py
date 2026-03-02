"""
认证蓝图 - Vue3 前端版
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from core.repository.user_repo import UserRepository
from core.user import User
from core.database import db

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """登录页面"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('请输入用户名和密码', 'error')
            return render_template('login.html')
        
        user = UserRepository.verify_password(username, password)
        if user:
            login_user(user)
            next_page = request.args.get('next')
            flash(f'欢迎回来，{user.username}！', 'success')
            return redirect(next_page or url_for('index'))
        else:
            flash('用户名或密码错误', 'error')
    
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """注册页面"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')
        
        if not username or not password:
            flash('请输入用户名和密码', 'error')
            return render_template('register.html')
        
        if password != password_confirm:
            flash('两次密码不一致', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('密码长度至少6位', 'error')
            return render_template('register.html')
        
        if UserRepository.get_by_username(username):
            flash('用户名已存在', 'error')
            return render_template('register.html')
        
        user = UserRepository.create(username, password, role='user')
        flash('注册成功，请登录', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """登出"""
    logout_user()
    flash('已退出登录', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile')
@login_required
def profile():
    """用户资料页面"""
    return render_template('dashboard.html', user=current_user)

# API 端点 - 供 Vue3 前端调用
@auth_bp.route('/api/userinfo')
def api_userinfo():
    """获取当前用户信息 API"""
    if not current_user.is_authenticated:
        return jsonify({'error': 'Not logged in'}), 401
    
    return jsonify(current_user.to_dict())

@auth_bp.route('/api/login', methods=['POST'])
def api_login():
    """API 登录"""
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    if not username or not password:
        return jsonify({'error': '请输入用户名和密码'}), 400
    
    user = UserRepository.verify_password(username, password)
    if user:
        login_user(user)
        return jsonify({'success': True, 'user': user.to_dict()})
    
    return jsonify({'error': '用户名或密码错误'}), 401

@auth_bp.route('/api/register', methods=['POST'])
def api_register():
    """API 注册"""
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')
    password_confirm = data.get('password_confirm', '')
    
    if not username or not password:
        return jsonify({'error': '请输入用户名和密码'}), 400
    
    if password != password_confirm:
        return jsonify({'error': '两次密码不一致'}), 400
    
    if len(password) < 6:
        return jsonify({'error': '密码长度至少6位'}), 400
    
    if UserRepository.get_by_username(username):
        return jsonify({'error': '用户名已存在'}), 400
    
    user = UserRepository.create(username, password, role='user')
    return jsonify({'success': True, 'user': user.to_dict()}), 201
