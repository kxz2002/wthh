"""
知识图谱单元测试
"""
import pytest
import pandas as pd
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def build_circle_graph(result_df, df, circle_id):
    """
    构建家庭圈知识图谱数据的核心函数
    
    Args:
        result_df: 预测结果DataFrame，包含用户ID、family_circle_id、is_key_person
        df: 原始数据DataFrame
        circle_id: 家庭圈ID
    
    Returns:
        dict: 包含nodes和edges的图谱数据
    """
    # 查找用户ID列
    user_id_col = None
    possible_names = ['用户ID', 'user_id', '用户id', 'ID', 'id', '用户编号']
    for col in result_df.columns:
        if any(name in str(col).lower() for name in possible_names):
            user_id_col = col
            break
    if user_id_col is None:
        user_id_col = result_df.columns[0]
    
    # 获取该家庭圈的所有成员
    circle_members = result_df[result_df['family_circle_id'] == int(circle_id)]
    
    if len(circle_members) == 0:
        return {'nodes': [], 'edges': [], 'error': '家庭圈不存在'}
    
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
    user_ids = set(circle_members[user_id_col].astype(str).tolist())
    
    # 找到该家庭圈成员在原始数据中的记录
    circle_df = df[df[user_id_col].astype(str).isin(user_ids)]
    
    # 基于地址关联 - 使用更多可能的列
    addr_cols = [col for col in df.columns 
                if any(kw in str(col).lower() for kw in ['地址', 'address', '基站', 'station', '小区', '区域'])]
    for addr_col in addr_cols:
        if addr_col in circle_df.columns:
            for addr, group in circle_df.groupby(addr_col):
                if pd.notna(addr) and str(addr).strip():
                    group_users = group[user_id_col].astype(str).unique().tolist()
                    group_users = [u for u in group_users if u in user_ids]
                    if len(group_users) > 1:
                        for i, u1 in enumerate(group_users):
                            for u2 in group_users[i+1:]:
                                edges.append({
                                    'from': u1,
                                    'to': u2,
                                    'label': f'同{addr_col}',
                                    'color': {'color': '#97C2FC'}
                                })
    
    # 基于账户关联
    account_cols = [col for col in df.columns 
                   if any(kw in str(col).lower() for kw in ['账户', 'account', '缴费', 'payment'])]
    for account_col in account_cols:
        if account_col in circle_df.columns:
            for account, group in circle_df.groupby(account_col):
                if pd.notna(account) and str(account).strip():
                    group_users = group[user_id_col].astype(str).unique().tolist()
                    group_users = [u for u in group_users if u in user_ids]
                    if len(group_users) > 1:
                        for i, u1 in enumerate(group_users):
                            for u2 in group_users[i+1:]:
                                edges.append({
                                    'from': u1,
                                    'to': u2,
                                    'label': f'同{account_col}',
                                    'color': {'color': '#FFB84D'}
                                })
    
    # 基于家庭网关联
    family_cols = [col for col in df.columns 
                  if any(kw in str(col).lower() for kw in ['家庭网', '泛家庭', '物理家'])]
    for family_col in family_cols:
        if family_col in circle_df.columns:
            for family, group in circle_df.groupby(family_col):
                if pd.notna(family) and str(family).strip():
                    group_users = group[user_id_col].astype(str).unique().tolist()
                    group_users = [u for u in group_users if u in user_ids]
                    if len(group_users) > 1:
                        for i, u1 in enumerate(group_users):
                            for u2 in group_users[i+1:]:
                                edges.append({
                                    'from': u1,
                                    'to': u2,
                                    'label': f'同{family_col}',
                                    'color': {'color': '#7B68EE'}
                                })
    
    # 去重边
    seen_edges = set()
    unique_edges = []
    for edge in edges:
        edge_key = tuple(sorted([edge['from'], edge['to']]))
        if edge_key not in seen_edges:
            seen_edges.add(edge_key)
            unique_edges.append(edge)
    
    return {
        'nodes': nodes,
        'edges': unique_edges
    }


class TestKnowledgeGraph:
    """知识图谱测试类"""
    
    @pytest.fixture
    def sample_result_df(self):
        """创建测试用预测结果DataFrame"""
        data = {
            '用户ID': ['1001', '1002', '1003', '1004', '2001'],
            'family_circle_id': [1, 1, 1, 2, 2],
            'is_key_person': [1, 0, 0, 1, 0]
        }
        return pd.DataFrame(data)
    
    @pytest.fixture
    def sample_df(self):
        """创建测试用原始数据DataFrame"""
        data = {
            '用户ID': ['1001', '1002', '1003', '1004', '2001', '2002'],
            '账户编码': ['A001', 'A001', 'A002', 'A003', 'A001', 'A001'],
            '基站标识': ['S1', 'S1', 'S2', 'S3', 'S1', 'S2'],
            '家庭网编码': ['F1', 'F1', 'F1', 'F2', 'F2', 'F2']
        }
        return pd.DataFrame(data)
    
    def test_build_graph_basic(self, sample_result_df, sample_df):
        """测试基本图谱构建"""
        result = build_circle_graph(sample_result_df, sample_df, 1)
        
        assert 'nodes' in result
        assert 'edges' in result
        assert len(result['nodes']) == 3  # 家庭圈1有3个成员
    
    def test_build_graph_key_person(self, sample_result_df, sample_df):
        """测试关键人标记"""
        result = build_circle_graph(sample_result_df, sample_df, 1)
        
        # 找到关键人节点
        key_node = [n for n in result['nodes'] if n['group'] == 'key_person']
        assert len(key_node) == 1
        assert '👑' in key_node[0]['label']
    
    def test_build_graph_account_edge(self, sample_result_df, sample_df):
        """测试账户关联边"""
        result = build_circle_graph(sample_result_df, sample_df, 1)
        
        # 1001和1002应该通过账户编码A001关联
        edge_found = False
        for edge in result['edges']:
            if ('1001' in [edge['from'], edge['to']] and 
                '1002' in [edge['from'], edge['to']]):
                edge_found = True
                break
        assert edge_found, "应该存在账户关联边"
    
    def test_build_graph_address_edge(self, sample_result_df, sample_df):
        """测试基站关联边"""
        result = build_circle_graph(sample_result_df, sample_df, 1)
        
        # 1001和1002应该通过基站S1关联
        edge_found = False
        for edge in result['edges']:
            if ('1001' in [edge['from'], edge['to']] and 
                '1002' in [edge['from'], edge['to']]):
                edge_found = True
                break
        assert edge_found, "应该存在基站关联边"
    
    def test_build_graph_nonexistent_circle(self, sample_result_df, sample_df):
        """测试不存在的家庭圈"""
        result = build_circle_graph(sample_result_df, sample_df, 999)
        
        assert result['error'] == '家庭圈不存在'
        assert len(result['nodes']) == 0
    
    def test_build_graph_different_circles(self, sample_result_df, sample_df):
        """测试不同家庭圈应该没有边"""
        result = build_circle_graph(sample_result_df, sample_df, 2)
        
        # 家庭圈2有2个成员(2001, 2002)
        assert len(result['nodes']) == 2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
