import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

"""
Flask Web应用 - 家庭圈用户识别可视化
"""
from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import json
import os
from core.data_loader import DataLoader
\
base_dir = '/home/liu/Code/Repos/wthh'
from core.feature_engineering import FeatureEngineer
from core.family_circle_model import FamilyCircleModel

app = Flask(__name__)

# 全局变量存储模型和数据
model = None
train_result = None
valid_result = None
test_result = None
train_df = None
valid_df = None
test_df = None

def load_model_and_data():
    """加载模型和数据"""
    global model, train_result, valid_result, test_result, train_df, valid_df, test_df

    # 获取项目根目录（app.py所在目录）
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, 'src', 'data', 'AI+数据1：数据应用开发-家庭圈用户识别模型.xlsx')
    output_dir = os.path.join(base_dir, 'src', 'output')
    
    # 尝试加载已保存的结果
    if os.path.exists(os.path.join(output_dir, 'train_result.csv')):
        train_result = pd.read_csv(os.path.join(output_dir, 'train_result.csv'))
        valid_result = pd.read_csv(os.path.join(output_dir, 'valid_result.csv'))
        test_result = pd.read_csv(os.path.join(output_dir, 'test_result.csv'))
        print("已加载保存的结果")
    else:
        # 如果没有保存的结果，运行主程序
        from main import main
        train_result, valid_result, test_result, model = main()
    
    # 加载原始数据
    loader = DataLoader(file_path)
    train_df, valid_df, test_df = loader.load_data()
    train_df = loader.flatten_columns(train_df)
    valid_df = loader.flatten_columns(valid_df)
    test_df = loader.flatten_columns(test_df)
    
    # 初始化模型
    if model is None:
        model = FamilyCircleModel()
        model.define_relationship_rules()

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/api/statistics')
def get_statistics():
    """获取统计信息"""
    global train_result, valid_result, test_result
    
    if train_result is None:
        load_model_and_data()
    
    stats = {
        'train': {
            'total_users': len(train_result),
            'family_circles': int(train_result['family_circle_id'].nunique()),
            'key_persons': int(train_result['is_key_person'].sum())
        },
        'valid': {
            'total_users': len(valid_result),
            'family_circles': int(valid_result['family_circle_id'].nunique()),
            'key_persons': int(valid_result['is_key_person'].sum())
        },
        'test': {
            'total_users': len(test_result),
            'family_circles': int(test_result['family_circle_id'].nunique()),
            'key_persons': int(test_result['is_key_person'].sum())
        }
    }
    
    return jsonify(stats)

@app.route('/api/family_circles')
def get_family_circles():
    """获取家庭圈列表（支持分页和懒加载）"""
    global train_result
    
    if train_result is None:
        load_model_and_data()
    
    dataset = request.args.get('dataset', 'train')
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 20))  # 每页20个家庭圈
    
    if dataset == 'train':
        result = train_result
    elif dataset == 'valid':
        result = valid_result
    else:
        result = test_result
    
    # 查找用户ID列
    user_id_col = None
    possible_names = ['用户ID', 'user_id', '用户id', 'ID', 'id', '用户编号']
    for col in result.columns:
        if any(name in str(col).lower() for name in possible_names):
            user_id_col = col
            break
    if user_id_col is None:
        user_id_col = result.columns[0]
    
    # 按家庭圈分组
    all_circles = []
    for circle_id, group in result.groupby('family_circle_id'):
        members = group.to_dict('records')
        key_person = group[group['is_key_person'] == 1]
        key_person_id = key_person.iloc[0][user_id_col] if len(key_person) > 0 else None
        
        all_circles.append({
            'circle_id': int(circle_id),
            'member_count': len(members),
            'key_person_id': str(key_person_id) if key_person_id is not None else None,
            'members': [{'user_id': str(m[user_id_col]), 'is_key_person': bool(m['is_key_person'])} 
                       for m in members]
        })
    
    # 按成员数量排序（大的在前）
    all_circles.sort(key=lambda x: x['member_count'], reverse=True)
    
    # 分页
    total = len(all_circles)
    start = (page - 1) * page_size
    end = start + page_size
    circles = all_circles[start:end]
    
    return jsonify({
        'circles': circles,
        'total': total,
        'page': page,
        'page_size': page_size,
        'total_pages': (total + page_size - 1) // page_size
    })

@app.route('/api/user/<user_id>')
def get_user_info(user_id):
    """获取用户详细信息"""
    global train_df, valid_df, test_df, train_result, valid_result, test_result
    
    if train_result is None:
        load_model_and_data()
    
    dataset = request.args.get('dataset', 'train')
    
    if dataset == 'train':
        df = train_df
        result = train_result
    elif dataset == 'valid':
        df = valid_df
        result = valid_result
    else:
        df = test_df
        result = test_result
    
    # 查找用户ID列
    user_id_col = None
    possible_names = ['用户ID', 'user_id', '用户id', 'ID', 'id', '用户编号']
    for col in df.columns:
        if any(name in str(col).lower() for name in possible_names):
            user_id_col = col
            break
    if user_id_col is None:
        user_id_col = df.columns[0]
    
    # 查找用户
    user_data = df[df[user_id_col].astype(str) == str(user_id)]
    user_result = result[result[user_id_col].astype(str) == str(user_id)]
    
    if len(user_data) == 0:
        return jsonify({'error': '用户不存在'}), 404
    
    # 获取用户信息
    user_info = {
        'user_id': str(user_id),
        'data': {},
    }
    
    if len(user_data) > 0:
        # 处理NaT和NaN值，转换为JSON可序列化的类型
        user_row = user_data.iloc[0].copy()
        # 将NaT转换为None
        for col in user_row.index:
            if pd.api.types.is_datetime64_any_dtype(user_row[col]):
                if pd.isna(user_row[col]):
                    user_row[col] = None
            elif pd.isna(user_row[col]):
                user_row[col] = None
        user_info['data'] = user_row.to_dict()
    
    if len(user_result) > 0:
        result_user_id_col = None
        for col in result.columns:
            if any(name in str(col).lower() for name in possible_names):
                result_user_id_col = col
                break
        if result_user_id_col is None:
            result_user_id_col = result.columns[0]
        
        user_info['family_circle_id'] = int(user_result.iloc[0]['family_circle_id'])
        user_info['is_key_person'] = bool(user_result.iloc[0]['is_key_person'])
        
        # 获取同家庭圈的其他成员
        circle_id = user_result.iloc[0]['family_circle_id']
        circle_members = result[result['family_circle_id'] == circle_id]
        user_info['family_members'] = [
            str(mid) for mid in circle_members[result_user_id_col].values if str(mid) != str(user_id)
        ]
    
    return jsonify(user_info)

@app.route('/api/search')
def search_users():
    """搜索用户（增强版）"""
    global train_df, valid_df, test_df, train_result, valid_result, test_result
    
    if train_df is None:
        load_model_and_data()
    
    query = request.args.get('q', '').strip()
    dataset = request.args.get('dataset', 'train')
    limit = int(request.args.get('limit', 20))
    
    if not query:
        return jsonify({'results': []})
    
    if dataset == 'train':
        df = train_df
        result = train_result
    elif dataset == 'valid':
        df = valid_df
        result = valid_result
    else:
        df = test_df
        result = test_result
    
    # 查找用户ID列
    user_id_col = None
    possible_names = ['用户ID', 'user_id', '用户id', 'ID', 'id', '用户编号']
    for col in df.columns:
        if any(name in str(col).lower() for name in possible_names):
            user_id_col = col
            break
    if user_id_col is None:
        user_id_col = df.columns[0]
    
    # 搜索用户ID
    matches = df[df[user_id_col].astype(str).str.contains(query, na=False, case=False)]
    
    # 合并结果信息
    results = []
    for idx, row in matches.head(limit).iterrows():
        user_id = str(row[user_id_col])
        # 查找该用户的家庭圈信息
        user_result = result[result[user_id_col].astype(str) == user_id]
        circle_id = int(user_result.iloc[0]['family_circle_id']) if len(user_result) > 0 else None
        is_key = bool(user_result.iloc[0]['is_key_person']) if len(user_result) > 0 else False
        
        results.append({
            'user_id': user_id,
            'display': user_id,
            'circle_id': circle_id,
            'is_key_person': is_key
        })
    
    return jsonify({'results': results})

@app.route('/api/relationship')
def check_relationship():
    """检查两个用户的关系"""
    global train_result, valid_result, test_result
    
    if train_result is None:
        load_model_and_data()
    
    user1_id = request.args.get('user1')
    user2_id = request.args.get('user2')
    dataset = request.args.get('dataset', 'train')
    
    if not user1_id or not user2_id:
        return jsonify({'error': '缺少用户ID参数'}), 400
    
    # 如果两个用户ID相同，直接返回是同一家庭圈
    if str(user1_id) == str(user2_id):
        return jsonify({
            'user1_id': user1_id,
            'user2_id': user2_id,
            'is_family': True,
            'confidence': 1.0,
            'message': '同一用户'
        })
    
    if dataset == 'train':
        result = train_result
    elif dataset == 'valid':
        result = valid_result
    else:
        result = test_result
    
    # 查找用户ID列
    user_id_col = None
    possible_names = ['用户ID', 'user_id', '用户id', 'ID', 'id', '用户编号']
    for col in result.columns:
        if any(name in str(col).lower() for name in possible_names):
            user_id_col = col
            break
    if user_id_col is None:
        user_id_col = result.columns[0]
    
    # 查找两个用户的家庭圈ID
    user1_result = result[result[user_id_col].astype(str) == str(user1_id)]
    user2_result = result[result[user_id_col].astype(str) == str(user2_id)]
    
    if len(user1_result) == 0:
        return jsonify({'error': f'用户 {user1_id} 不存在'}), 404
    if len(user2_result) == 0:
        return jsonify({'error': f'用户 {user2_id} 不存在'}), 404
    
    circle1_id = user1_result.iloc[0]['family_circle_id']
    circle2_id = user2_result.iloc[0]['family_circle_id']
    
    is_family = (circle1_id == circle2_id)
    confidence = 1.0 if is_family else 0.0
    
    return jsonify({
        'user1_id': user1_id,
        'user2_id': user2_id,
        'user1_circle_id': int(circle1_id),
        'user2_circle_id': int(circle2_id),
        'is_family': bool(is_family),
        'confidence': float(confidence),
        'message': '是同一家庭圈成员' if is_family else '不是同一家庭圈成员'
    })

@app.route('/api/model_metrics')
def get_model_metrics():
    """获取模型评估指标"""
    import json
    import os

    base_dir = os.path.dirname(os.path.abspath(__file__))
    metrics_file = os.path.join(base_dir, 'output', 'model_metrics.json')
    if os.path.exists(metrics_file):
        with open(metrics_file, 'r', encoding='utf-8') as f:
            metrics = json.load(f)
        return jsonify(metrics)
    else:
        return jsonify({'accuracy': 0, 'precision': 0, 'recall': 0, 'f1_score': 0})

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
            'label': user_id + (' 👑' if is_key else ''),
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
    # 初始化时加载数据
    load_model_and_data()
    
    print("\n启动Web服务器...")
    print("访问 http://127.0.0.1:5000 查看可视化界面")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

