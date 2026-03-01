"""
Flask Web应用 - 家庭圈用户识别可视化（含用户认证）
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
import pandas as pd
import numpy as np
import json

base_dir = '/home/liu/Code/Repos/wthh'

# 配置
app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///wthh.db'  # 默认 SQLite，可改为 MySQL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 导入认证模块
from core.database import db
from core.auth import login_manager
from apps.auth import auth_bp

# 初始化
db.init_app(app)
login_manager.init_app(app)

# 注册蓝图
app.register_blueprint(auth_bp)

# 导入数据模块
from core.data_loader import DataLoader
from core.feature_engineering import FeatureEngineer
from core.family_circle_model import FamilyCircleModel

# 全局变量
model = None
train_result = None
valid_result = None
test_result = None
train_df = None
valid_df = None
test_df = None

def load_model_and_data():
    """加载数据和模型"""
    global model, train_result, valid_result, test_result, train_df, valid_df, test_df
    
    data_path = os.path.join(base_dir, 'src', 'data', 'AI+数据1：数据应用开发-家庭圈用户识别模型.xlsx')
    loader = DataLoader(data_path)
    train_df, valid_df, test_df = loader.load_data()
    
    feature_engineer = FeatureEngineer()
    train_features = feature_engineer.create_features(train_df)
    valid_features = feature_engineer.create_features(valid_df)
    test_features = feature_engineer.create_features(test_df)
    
    model = FamilyCircleModel()
    train_result = model.predict(train_features)
    valid_result = model.predict(valid_features)
    test_result = model.predict(test_features)

# 首页
@app.route('/')
def index():
    return render_template('index.html')

# 受保护的路由示例
@app.route('/dashboard')
@login_required
def dashboard():
    """用户仪表板 - 需要登录"""
    return render_template('dashboard.html', user=current_user)

# API 路由...
@app.route('/api/statistics')
def get_statistics():
    # 可以选择是否需要登录
    if not train_result or not valid_result or not test_result:
        load_model_and_data()
    return jsonify({
        'train': {'total_users': len(train_result)},
        'valid': {'total_users': len(valid_result)},
        'test': {'total_users': len(test_result)}
    })

@app.route('/api/family_circles')
def get_family_circles():
    if not train_result:
        load_model_and_data()
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    
    family_circles = train_result.groupby('family_circle_id')
    total = len(family_circles)
    start = (page - 1) * per_page
    end = start + per_page
    
    circles = []
    for circle_id, group in list(family_circles)[start:end]:
        circles.append({
            'circle_id': int(circle_id),
            'size': len(group),
            'key_person': int(group[group['is_key_person'] == 1].iloc[0]['用户ID']) if len(group[group['is_key_person'] == 1]) > 0 else None
        })
    
    return jsonify({
        'circles': circles,
        'total': total,
        'page': page,
        'per_page': per_page
    })

@app.route('/api/user/<user_id>')
def get_user_info(user_id):
    if not train_result:
        load_model_and_data()
    
    user_data = train_df[train_df['用户ID'].astype(str) == str(user_id)]
    user_result = train_result[train_result['用户ID'].astype(str) == str(user_id)]
    
    if len(user_data) == 0:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'user_id': str(user_id),
        'family_circle_id': int(user_result.iloc[0]['family_circle_id']),
        'is_key_person': bool(user_result.iloc[0]['is_key_person']),
        'data': user_data.iloc[0].to_dict()
    })

@app.route('/api/search')
def search_users():
    if not train_result:
        load_model_and_data()
    
    query = request.args.get('q', '')
    if not query:
        return jsonify({'users': []})
    
    results = train_df[train_df['用户ID'].astype(str).str.contains(query)].head(10)
    users = [{'user_id': str(row['用户ID'])} for _, row in results.iterrows()]
    
    return jsonify({'users': users})

@app.route('/api/model_metrics')
def get_model_metrics():
    metrics_path = os.path.join(base_dir, 'src', 'output', 'model_metrics.json')
    if os.path.exists(metrics_path):
        with open(metrics_path, 'r') as f:
            return jsonify(json.load(f))
    return jsonify({})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # 创建数据库表
    app.run(debug=True, host='0.0.0.0', port=5000)
