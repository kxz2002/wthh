"""
特征工程模块
根据赛题要求构建多维度特征：
1. 地址关联性特征
2. 缴费账户关联性特征
3. 终端共享特征
4. 通信行为特征
"""
import pandas as pd
import numpy as np
from typing import List, Dict
from collections import defaultdict

class FeatureEngineer:
    def __init__(self):
        """初始化特征工程器"""
        self.feature_names = []
        
    def extract_all_features(self, df: pd.DataFrame, user_id_col: str = None) -> pd.DataFrame:
        """
        提取所有特征
        
        Args:
            df: 输入数据框
            user_id_col: 用户ID列名
            
        Returns:
            包含所有特征的DataFrame
        """
        if user_id_col is None:
            # 自动识别用户ID列
            possible_names = ['用户ID', 'user_id', '用户id', 'ID', 'id', '用户编号']
            for col in df.columns:
                if any(name in str(col) for name in possible_names):
                    user_id_col = col
                    break
            if user_id_col is None:
                user_id_col = df.columns[0]
        
        features_df = pd.DataFrame()
        features_df[user_id_col] = df[user_id_col].copy()
        
        # 提取各类特征
        print("开始特征工程...")
        
        # 1. 地址关联性特征
        print("提取地址关联性特征...")
        addr_features = self.extract_address_features(df, user_id_col)
        features_df = pd.merge(features_df, addr_features, on=user_id_col, how='left')
        
        # 2. 缴费账户关联性特征
        print("提取缴费账户关联性特征...")
        account_features = self.extract_account_features(df, user_id_col)
        features_df = pd.merge(features_df, account_features, on=user_id_col, how='left')
        
        # 3. 终端共享特征
        print("提取终端共享特征...")
        device_features = self.extract_device_features(df, user_id_col)
        features_df = pd.merge(features_df, device_features, on=user_id_col, how='left')
        
        # 4. 通信行为特征
        print("提取通信行为特征...")
        comm_features = self.extract_communication_features(df, user_id_col)
        features_df = pd.merge(features_df, comm_features, on=user_id_col, how='left')
        
        # 5. 基础信息特征
        print("提取基础信息特征...")
        basic_features = self.extract_basic_features(df, user_id_col)
        features_df = pd.merge(features_df, basic_features, on=user_id_col, how='left')
        
        print(f"特征工程完成，共生成 {len(features_df.columns) - 1} 个特征")
        
        return features_df
    
    def extract_address_features(self, df: pd.DataFrame, user_id_col: str) -> pd.DataFrame:
        """
        提取地址关联性特征
        - 相同地址的用户数量
        - 节假日驻留基站相似度
        - 地址稳定性
        """
        features = pd.DataFrame()
        features[user_id_col] = df[user_id_col].unique()
        
        # 查找地址相关列
        addr_cols = [col for col in df.columns if any(keyword in str(col).lower() 
                    for keyword in ['地址', 'address', '基站', 'station', '位置', 'location'])]
        
        if addr_cols:
            # 相同地址用户数
            for addr_col in addr_cols[:3]:  # 最多处理3个地址列
                if addr_col in df.columns:
                    addr_counts = df.groupby(addr_col)[user_id_col].count()
                    df[f'{addr_col}_count'] = df[addr_col].map(addr_counts)
                    features[f'{addr_col}_same_addr_count'] = df.groupby(user_id_col)[f'{addr_col}_count'].first().values
        
        # 默认特征（如果找不到地址列）
        if len([col for col in features.columns if 'addr' in col.lower()]) == 1:
            features['address_stability'] = 1.0
            features['same_address_users'] = 1
        
        return features
    
    def extract_account_features(self, df: pd.DataFrame, user_id_col: str) -> pd.DataFrame:
        """
        提取缴费账户关联性特征
        - 相同缴费账户的用户数量
        - 账户共享关系强度
        """
        features = pd.DataFrame()
        features[user_id_col] = df[user_id_col].unique()
        
        # 查找账户相关列
        account_cols = [col for col in df.columns if any(keyword in str(col).lower() 
                       for keyword in ['账户', 'account', '缴费', 'payment', '付费'])]
        
        if account_cols:
            for account_col in account_cols[:3]:
                if account_col in df.columns:
                    account_counts = df.groupby(account_col)[user_id_col].count()
                    df[f'{account_col}_count'] = df[account_col].map(account_counts)
                    features[f'{account_col}_same_account_count'] = df.groupby(user_id_col)[f'{account_col}_count'].first().values
        
        # 默认特征
        if len([col for col in features.columns if 'account' in col.lower()]) == 1:
            features['same_payment_account_users'] = 1
            features['account_sharing_strength'] = 0.0
        
        return features
    
    def extract_device_features(self, df: pd.DataFrame, user_id_col: str) -> pd.DataFrame:
        """
        提取终端共享特征
        - 共享设备数量
        - 设备共享关系
        """
        features = pd.DataFrame()
        features[user_id_col] = df[user_id_col].unique()
        
        # 查找设备相关列
        device_cols = [col for col in df.columns if any(keyword in str(col).lower() 
                      for keyword in ['设备', 'device', '终端', 'terminal', '共享', 'share'])]
        
        if device_cols:
            for device_col in device_cols[:3]:
                if device_col in df.columns:
                    device_counts = df.groupby(device_col)[user_id_col].count()
                    df[f'{device_col}_count'] = df[device_col].map(device_counts)
                    features[f'{device_col}_shared_device_count'] = df.groupby(user_id_col)[f'{device_col}_count'].first().values
        
        # 默认特征
        if len([col for col in features.columns if 'device' in col.lower()]) == 1:
            features['shared_devices_count'] = 0
            features['device_sharing_ratio'] = 0.0
        
        return features
    
    def extract_communication_features(self, df: pd.DataFrame, user_id_col: str) -> pd.DataFrame:
        """
        提取通信行为特征
        - 通话频率
        - 联系人重叠度
        - 通信时间模式相似度
        """
        features = pd.DataFrame()
        features[user_id_col] = df[user_id_col].unique()
        
        # 查找通信相关列
        comm_cols = [col for col in df.columns if any(keyword in str(col).lower() 
                    for keyword in ['通话', 'call', '联系人', 'contact', '通信', 'communication'])]
        
        if comm_cols:
            # 通话频率特征
            for comm_col in comm_cols[:2]:
                if comm_col in df.columns:
                    comm_stats = df.groupby(user_id_col)[comm_col].agg(['count', 'mean', 'std']).fillna(0)
                    for stat in ['count', 'mean', 'std']:
                        features[f'{comm_col}_{stat}'] = comm_stats[stat].values
        
        # 默认特征
        if len([col for col in features.columns if 'comm' in col.lower() or 'call' in col.lower()]) == 1:
            features['call_frequency'] = 0.0
            features['contact_overlap_ratio'] = 0.0
            features['communication_similarity'] = 0.0
        
        return features
    
    def extract_basic_features(self, df: pd.DataFrame, user_id_col: str) -> pd.DataFrame:
        """
        提取基础信息特征
        - 性别、年龄等
        """
        features = pd.DataFrame()
        features[user_id_col] = df[user_id_col].unique()
        
        # 查找基础信息列
        basic_cols = [col for col in df.columns if any(keyword in str(col).lower() 
                    for keyword in ['性别', 'gender', '年龄', 'age', '性别', 'sex'])]
        
        if basic_cols:
            for basic_col in basic_cols:
                if basic_col in df.columns:
                    # 数值型特征取均值，分类型特征取众数
                    if df[basic_col].dtype in ['int64', 'float64']:
                        basic_stats = df.groupby(user_id_col)[basic_col].first()
                        features[basic_col] = basic_stats.values
                    else:
                        # 编码分类特征
                        df[basic_col + '_encoded'] = pd.Categorical(df[basic_col]).codes
                        basic_stats = df.groupby(user_id_col)[basic_col + '_encoded'].first()
                        features[basic_col + '_encoded'] = basic_stats.values
        
        return features
    
    def build_relationship_graph(self, df: pd.DataFrame, user_id_col: str) -> Dict:
        """
        构建用户关系图
        
        Returns:
            关系图字典，key为用户ID，value为关联用户列表
        """
        graph = defaultdict(set)
        
        # 基于地址关联
        addr_cols = [col for col in df.columns if '地址' in str(col) or 'address' in str(col).lower()]
        for addr_col in addr_cols[:2]:
            if addr_col in df.columns:
                for addr, group in df.groupby(addr_col):
                    users = group[user_id_col].unique()
                    for i, u1 in enumerate(users):
                        for u2 in users[i+1:]:
                            graph[u1].add(u2)
                            graph[u2].add(u1)
        
        # 基于账户关联
        account_cols = [col for col in df.columns if '账户' in str(col) or 'account' in str(col).lower()]
        for account_col in account_cols[:2]:
            if account_col in df.columns:
                for account, group in df.groupby(account_col):
                    users = group[user_id_col].unique()
                    for i, u1 in enumerate(users):
                        for u2 in users[i+1:]:
                            graph[u1].add(u2)
                            graph[u2].add(u1)
        
        return dict(graph)

