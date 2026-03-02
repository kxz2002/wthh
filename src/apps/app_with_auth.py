"""
Flask Web应用 - 家庭圈用户识别可视化（含用户认证）
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_cors import CORS
from flask_login import login_required, current_user
import pandas as pd
import numpy as np
import json

base_dir = '/home/liu/Code/Repos/wthh'

# 配置 - 使用统一的 instance 文件夹
instance_path = os.path.join(base_dir, 'instance')
os.makedirs(instance_path, exist_ok=True)

app = Flask(__name__, template_folder='../templates', instance_path=instance_path)
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(instance_path, "wthh.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 启用 CORS - 允许开发环境的前端
CORS(app, supports_credentials=True, origins=['http://localhost:5173', 'http://127.0.0.1:5173'])

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

# 首页 - 重定向到 Vue 前端
@app.route('/')
@login_required
def index():
    """首页 - 重定向到 Vue 前端"""
    return redirect('http://localhost:5173')

# 仪表板 - 重定向到 Vue 前端
@app.route('/dashboard')
@login_required
def dashboard():
    """仪表板 - 重定向到 Vue 前端"""
    return redirect('http://localhost:5173/dashboard')

# API 路由...
@app.route('/api/statistics')
def get_statistics():
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

@app.route('/api/circle_graph/<circle_id>')
def get_circle_graph(circle_id):
    """获取家庭圈的知识图谱数据"""
    global train_result, valid_result, test_result, train_df, valid_df, test_df

    if train_result is None:
        load_model_and_data()

    dataset = request.args.get('dataset', 'train')

    if dataset == 'train':
        result = train_result
        df = train_df
    elif dataset == 'valid':
        result = valid_result
        df = valid_df
    else:
        result = test_result
        df = test_df

    # 查找用户ID列
    user_id_col = None
    possible_names = ['用户ID', 'user_id', '用户id', 'ID', 'id', '用户编号']
    for col in result.columns:
        if any(name in str(col).lower() for name in possible_names):
            user_id_col = col
            break
    if user_id_col is None:
        user_id_col = result.columns[0]

    # 获取该家庭圈的所有成员
    circle_members = result[result['family_circle_id'] == int(circle_id)]

    if len(circle_members) == 0:
        return jsonify({'error': '家庭圈不存在'}), 404

    # 构建节点（用户）
    nodes = []
    edges = []

    for idx, row in circle_members.iterrows():
        user_id = str(row[user_id_col])
        is_key = bool(row['is_key_person'])

        nodes.append({
            'id': user_id,
            'label': user_id + (' (关键人)' if is_key else ''),
            'group': 'key_person' if is_key else 'member',
            'title': f'用户: {user_id}\n{"关键人" if is_key else "成员"}'
        })

    # 构建边（基于地址、账户等关联）
    user_ids = circle_members[user_id_col].astype(str).tolist()

    # 基于地址关联
    addr_cols = [col for col in df.columns
                if any(kw in str(col).lower() for kw in ['地址', 'address', '基站', 'station'])]
    for addr_col in addr_cols[:2]:
        if addr_col in df.columns:
            for addr, group in df.groupby(addr_col):
                if pd.notna(addr):
                    group_users = group[user_id_col].astype(str).tolist()
                    group_users = [u for u in group_users if u in user_ids]
                    if len(group_users) > 1:
                        for i, u1 in enumerate(group_users):
                            for u2 in group_users[i+1:]:
                                edges.append({
                                    'from': u1,
                                    'to': u2,
                                    'label': '地址关联',
                                    'color': {'color': '#97C2FC'}
                                })

    # 基于账户关联
    account_cols = [col for col in df.columns
                   if any(kw in str(col).lower() for kw in ['账户', 'account', '缴费', 'payment'])]
    for account_col in account_cols[:2]:
        if account_col in df.columns:
            for account, group in df.groupby(account_col):
                if pd.notna(account):
                    group_users = group[user_id_col].astype(str).tolist()
                    group_users = [u for u in group_users if u in user_ids]
                    if len(group_users) > 1:
                        for i, u1 in enumerate(group_users):
                            for u2 in group_users[i+1:]:
                                edges.append({
                                    'from': u1,
                                    'to': u2,
                                    'label': '账户关联',
                                    'color': {'color': '#FFB84D'}
                                })

    # 去重边
    seen_edges = set()
    unique_edges = []
    for edge in edges:
        edge_key = tuple(sorted([edge['from'], edge['to']]))
        if edge_key not in seen_edges:
            seen_edges.add(edge_key)
            unique_edges.append(edge)

    return jsonify({
        'nodes': nodes,
        'edges': unique_edges
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
