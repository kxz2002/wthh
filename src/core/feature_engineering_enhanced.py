"""
增强版特征工程模块
提取更多有效特征用于家庭圈识别
"""
import pandas as pd
import numpy as np
from typing import List, Dict
from collections import defaultdict
from core.feature_engineering import FeatureEngineer

class EnhancedFeatureEngineer(FeatureEngineer):
    """增强版特征工程器"""
    
    def extract_all_features(self, df: pd.DataFrame, user_id_col: str = None) -> pd.DataFrame:
        """
        提取所有特征（增强版）
        
        Args:
            df: 输入数据框
            user_id_col: 用户ID列名
            
        Returns:
            包含所有特征的DataFrame
        """
        if user_id_col is None:
            possible_names = ['用户ID', 'user_id', '用户id', 'ID', 'id', '用户编号']
            for col in df.columns:
                if any(name in str(col).lower() for name in possible_names):
                    user_id_col = col
                    break
            if user_id_col is None:
                user_id_col = df.columns[0]
        
        # 先调用基础特征工程
        features_df = super().extract_all_features(df, user_id_col)
        
        # 不在这里打印，让主程序统一控制输出
        
        # 1. 提取更多地址相关特征
        addr_features = self.extract_enhanced_address_features(df, user_id_col)
        features_df = pd.merge(features_df, addr_features, on=user_id_col, how='left')
        
        # 2. 提取更多账户相关特征
        account_features = self.extract_enhanced_account_features(df, user_id_col)
        features_df = pd.merge(features_df, account_features, on=user_id_col, how='left')
        
        # 3. 提取更多通信相关特征
        comm_features = self.extract_enhanced_communication_features(df, user_id_col)
        features_df = pd.merge(features_df, comm_features, on=user_id_col, how='left')
        
        # 4. 提取统计特征
        stats_features = self.extract_statistical_features(df, user_id_col)
        features_df = pd.merge(features_df, stats_features, on=user_id_col, how='left')
        
        # 5. 提取交互特征
        interaction_features = self.extract_interaction_features(df, user_id_col)
        features_df = pd.merge(features_df, interaction_features, on=user_id_col, how='left')
        
        print(f"增强特征工程完成，共生成 {len(features_df.columns) - 1} 个特征")
        
        return features_df
    
    def extract_enhanced_address_features(self, df: pd.DataFrame, user_id_col: str) -> pd.DataFrame:
        """提取增强的地址特征"""
        features = pd.DataFrame()
        all_users = df[user_id_col].unique()
        features[user_id_col] = all_users
        
        addr_cols = [col for col in df.columns 
                    if any(keyword in str(col).lower() 
                          for keyword in ['地址', 'address', '基站', 'station', '位置', 'location'])]
        
        for addr_col in addr_cols[:5]:  # 处理更多地址列
            if addr_col in df.columns:
                # 地址唯一性（使用reindex确保所有用户都有值）
                addr_unique = df.groupby(user_id_col)[addr_col].nunique()
                features[f'{addr_col}_unique_count'] = addr_unique.reindex(all_users, fill_value=0).values
                
                # 地址频率（使用reindex确保所有用户都有值）
                addr_freq = df.groupby([user_id_col, addr_col]).size().reset_index(name='freq')
                addr_max_freq = addr_freq.groupby(user_id_col)['freq'].max()
                features[f'{addr_col}_max_freq'] = addr_max_freq.reindex(all_users, fill_value=0).values
        
        return features.fillna(0)
    
    def extract_enhanced_account_features(self, df: pd.DataFrame, user_id_col: str) -> pd.DataFrame:
        """提取增强的账户特征"""
        features = pd.DataFrame()
        all_users = df[user_id_col].unique()
        features[user_id_col] = all_users
        
        account_cols = [col for col in df.columns 
                       if any(keyword in str(col).lower() 
                             for keyword in ['账户', 'account', '缴费', 'payment', '付费'])]
        
        for account_col in account_cols[:5]:
            if account_col in df.columns:
                # 账户唯一性（使用reindex确保所有用户都有值）
                account_unique = df.groupby(user_id_col)[account_col].nunique()
                features[f'{account_col}_unique_count'] = account_unique.reindex(all_users, fill_value=0).values
                
                # 账户共享度（优化版本，避免循环）
                account_sharing = df.groupby(account_col)[user_id_col].nunique()
                # 使用更高效的方法
                user_account_df = df.groupby(user_id_col)[account_col].agg(list).reset_index()
                sharing_scores = []
                for idx, row in user_account_df.iterrows():
                    accounts = row[account_col]
                    if accounts and len(accounts) > 0:
                        score = sum(account_sharing.get(acc, 0) for acc in accounts if pd.notna(acc)) / len(accounts)
                    else:
                        score = 0
                    sharing_scores.append(score)
                # 创建完整的sharing_scores列表（包含所有用户）
                sharing_dict = dict(zip(user_account_df[user_id_col], sharing_scores))
                features[f'{account_col}_sharing_score'] = [sharing_dict.get(uid, 0) for uid in all_users]
        
        return features.fillna(0)
    
    def extract_enhanced_communication_features(self, df: pd.DataFrame, user_id_col: str) -> pd.DataFrame:
        """提取增强的通信特征"""
        features = pd.DataFrame()
        all_users = df[user_id_col].unique()
        features[user_id_col] = all_users
        
        comm_cols = [col for col in df.columns 
                    if any(keyword in str(col).lower() 
                          for keyword in ['通话', 'call', '联系人', 'contact', '通信', 'communication'])]
        
        for comm_col in comm_cols[:5]:
            if comm_col in df.columns:
                # 只对数值型列进行统计
                if df[comm_col].dtype in ['int64', 'float64']:
                    # 通信统计（使用reindex确保所有用户都有值）
                    comm_stats = df.groupby(user_id_col)[comm_col].agg(['sum', 'mean', 'std', 'count']).fillna(0)
                    comm_stats = comm_stats.reindex(all_users, fill_value=0)
                    for stat in ['sum', 'mean', 'std', 'count']:
                        if stat in comm_stats.columns:
                            features[f'{comm_col}_{stat}'] = comm_stats[stat].values
                else:
                    # 对于非数值型列，只统计计数
                    comm_count = df.groupby(user_id_col)[comm_col].count()
                    features[f'{comm_col}_count'] = comm_count.reindex(all_users, fill_value=0).values
        
        return features.fillna(0)
    
    def extract_statistical_features(self, df: pd.DataFrame, user_id_col: str) -> pd.DataFrame:
        """提取统计特征（优化版本）"""
        features = pd.DataFrame()
        all_users = df[user_id_col].unique()
        features[user_id_col] = all_users
        
        # 每个用户的记录数（使用reindex确保所有用户都有值）
        record_counts = df.groupby(user_id_col).size()
        features['record_count'] = record_counts.reindex(all_users, fill_value=0).values
        
        # 每个用户的非空字段数（优化：避免apply，使用更高效的方法）
        print("  计算非空字段数...")
        non_null_counts = df.groupby(user_id_col).apply(lambda x: x.notna().sum().sum())
        features['non_null_field_count'] = non_null_counts.reindex(all_users, fill_value=0).values
        
        # 每个用户的唯一值数量（优化：只计算数值列，避免计算所有列）
        print("  计算唯一值数量...")
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if user_id_col in numeric_cols:
            numeric_cols.remove(user_id_col)
        if len(numeric_cols) > 0:
            unique_value_counts = df.groupby(user_id_col)[numeric_cols].nunique().sum(axis=1)
        else:
            unique_value_counts = pd.Series(0, index=all_users)
        features['unique_value_count'] = unique_value_counts.reindex(all_users, fill_value=0).values
        
        return features.fillna(0)
    
    def extract_interaction_features(self, df: pd.DataFrame, user_id_col: str) -> pd.DataFrame:
        """提取交互特征（地址×账户等）"""
        features = pd.DataFrame()
        all_users = df[user_id_col].unique()
        features[user_id_col] = all_users
        
        addr_cols = [col for col in df.columns 
                    if any(keyword in str(col).lower() 
                          for keyword in ['地址', 'address', '基站', 'station'])]
        account_cols = [col for col in df.columns 
                       if any(keyword in str(col).lower() 
                             for keyword in ['账户', 'account', '缴费', 'payment'])]
        
        # 地址和账户的组合特征（优化：减少循环）
        if addr_cols and account_cols:
            for addr_col in addr_cols[:2]:
                for account_col in account_cols[:2]:
                    if addr_col in df.columns and account_col in df.columns:
                        # 相同地址和账户的用户数（优化版本）
                        combo = df.groupby([addr_col, account_col])[user_id_col].nunique()
                        # 为每个用户获取第一个地址和账户组合
                        user_combo = df.groupby(user_id_col).first()[[addr_col, account_col]]
                        user_combo_scores = []
                        for idx, row in user_combo.iterrows():
                            addr_val = row[addr_col]
                            acc_val = row[account_col]
                            if pd.notna(addr_val) and pd.notna(acc_val):
                                score = combo.get((addr_val, acc_val), 0)
                            else:
                                score = 0
                            user_combo_scores.append(score)
                        # 创建完整的scores列表
                        combo_dict = dict(zip(user_combo.index, user_combo_scores))
                        features[f'{addr_col}_{account_col}_combo'] = [combo_dict.get(uid, 0) for uid in all_users]
        
        return features.fillna(0)

