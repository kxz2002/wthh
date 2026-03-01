"""
家庭圈识别模型
实现家庭圈用户识别和关键人识别算法
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Set
from collections import defaultdict
from sklearn.ensemble import RandomForestClassifier, IsolationForest, GradientBoostingClassifier
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.feature_selection import SelectKBest, f_classif
import networkx as nx

# 尝试导入XGBoost和LightGBM（如果可用）
try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

try:
    import lightgbm as lgb
    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False

class FamilyCircleModel:
    def __init__(self):
        """初始化家庭圈模型"""
        self.scaler = StandardScaler()
        self.cluster_model = None
        self.classifier = None  # 分类模型
        self.label_encoder = LabelEncoder()
        self.relationship_rules = {}
        self.family_circles = {}  # 用户ID -> 家庭圈ID
        self.key_persons = {}     # 家庭圈ID -> 关键人ID
        self.use_supervised = False  # 是否使用监督学习
        
    def train_supervised_model(self, train_df: pd.DataFrame, train_features: pd.DataFrame,
                               user_id_col: str, label_col: str):
        """
        使用带标签数据训练监督学习模型
        
        Args:
            train_df: 训练数据（包含标签）
            train_features: 训练特征
            user_id_col: 用户ID列名
            label_col: 标签列名
        """
        print("使用监督学习方法训练模型...")
        
        # 合并特征和标签
        train_data = pd.merge(train_features, train_df[[user_id_col, label_col]], 
                             on=user_id_col, how='inner')
        
        # 准备特征和标签
        feature_cols = [col for col in train_features.columns if col != user_id_col]
        X = train_data[feature_cols].fillna(0).values
        y = train_data[label_col].values
        
        # 编码标签（如果是字符串）
        if y.dtype == 'object' or pd.api.types.is_string_dtype(y):
            y_encoded = self.label_encoder.fit_transform(y)
        else:
            y_encoded = y
            # 创建标签编码器映射
            unique_labels = sorted(pd.Series(y).unique())
            self.label_encoder.fit(unique_labels)
        
        # 标准化特征
        X_scaled = self.scaler.fit_transform(X)
        
        # 特征选择（选择最重要的特征）
        print(f"原始特征数: {X_scaled.shape[1]}")
        n_features = min(50, X_scaled.shape[1])  # 最多选择50个特征
        if X_scaled.shape[1] > 10:
            try:
                selector = SelectKBest(f_classif, k=n_features)
                X_selected = selector.fit_transform(X_scaled, y_encoded)
                self.feature_selector = selector
                print(f"特征选择后特征数: {X_selected.shape[1]}")
            except Exception as e:
                print(f"特征选择失败: {e}，使用所有特征")
                X_selected = X_scaled
                self.feature_selector = None
        else:
            X_selected = X_scaled
            self.feature_selector = None
        
        # 计算类别权重（处理类别不平衡）- 对于多分类问题，直接使用'balanced'
        # 不需要手动计算，模型会自动处理
        
        # 尝试使用更好的模型，如果失败则回退
        model_trained = False
        
        if LIGHTGBM_AVAILABLE:
            try:
                print("尝试使用LightGBM模型...")
                self.classifier = lgb.LGBMClassifier(
                    n_estimators=100,  # 减少估计器数量
                    max_depth=6,       # 减少树的深度
                    learning_rate=0.1,
                    num_leaves=20,     # 减少叶子节点数量
                    min_child_samples=10,
                    subsample=0.8,
                    colsample_bytree=0.8,
                    random_state=42,
                    n_jobs=1,          # 减少并行度
                    class_weight='balanced',
                    verbose=-1,
                    force_col_wise=True
                )
                self.classifier.fit(X_selected, y_encoded)
                model_trained = True
                print("LightGBM模型训练成功")
            except Exception as e:
                print(f"LightGBM训练失败: {e}")
                print("回退到其他模型...")
        
        if not model_trained and XGBOOST_AVAILABLE:
            try:
                print("尝试使用XGBoost模型...")
                self.classifier = xgb.XGBClassifier(
                    n_estimators=100,  # 减少估计器数量
                    max_depth=6,       # 减少树的深度
                    learning_rate=0.1,
                    min_child_weight=3,
                    subsample=0.8,
                    colsample_bytree=0.8,
                    random_state=42,
                    n_jobs=1,          # 减少并行度
                    eval_metric='mlogloss',
                    tree_method='hist',
                    reg_alpha=0.1,     # 添加正则化，减少过拟合
                    reg_lambda=0.1
                )
                self.classifier.fit(X_selected, y_encoded)
                model_trained = True
                print("XGBoost模型训练成功")
            except Exception as e:
                print(f"XGBoost训练失败: {e}")
                print("回退到随机森林模型...")
        
        if not model_trained:
            print("使用增强的随机森林模型...")
            self.classifier = RandomForestClassifier(
                n_estimators=200,  # 增加树的数量
                max_depth=20,       # 增加树的深度
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1,
                max_features='sqrt',
                class_weight='balanced'  # 处理类别不平衡
            )
            self.classifier.fit(X_selected, y_encoded)
            print("随机森林模型训练成功")
        
        self.use_supervised = True
        
        print(f"模型训练完成，共 {len(self.label_encoder.classes_)} 个家庭圈类别")
    
    def identify_family_circles(self, df: pd.DataFrame, user_id_col: str, 
                                features: List[str] = None, 
                                original_df: pd.DataFrame = None,
                                label_col: str = None) -> pd.DataFrame:
        """
        识别家庭圈
        使用基于规则的图聚类方法，基于地址、账户等直接关联关系
        
        Args:
            df: 包含特征的数据框
            user_id_col: 用户ID列名
            features: 特征列名列表（此参数保留兼容性，实际使用原始数据）
            original_df: 原始数据框，用于提取关联关系
            
        Returns:
            包含家庭圈ID的结果数据框
        """
        # 如果已训练监督学习模型，使用分类器预测
        if self.use_supervised and self.classifier is not None:
            return self._predict_with_classifier(df, features, user_id_col)
        
        # 否则使用基于规则的图聚类方法
        if original_df is None:
            original_df = df
        
        # 构建用户关系图
        relationship_graph = self._build_relationship_graph(original_df, user_id_col)
        
        # 使用图算法进行聚类（连通分量）
        cluster_labels = self._graph_clustering(relationship_graph, original_df[user_id_col].unique())
        
        # 构建结果
        result_df = pd.DataFrame()
        result_df[user_id_col] = original_df[user_id_col].values
        
        # 将图聚类结果映射到用户（处理类型一致性）
        user_to_cluster = {}
        for cluster_id, users in enumerate(cluster_labels):
            for user in users:
                # 确保键的类型一致
                user_to_cluster[str(user)] = cluster_id
        
        # 为每个用户分配家庭圈ID
        result_df['family_circle_id'] = result_df[user_id_col].astype(str).map(
            lambda x: user_to_cluster.get(x, -1)
        ).astype(int)
        
        # 处理未分组的用户（独立用户）
        independent_mask = result_df['family_circle_id'] == -1
        independent_count = independent_mask.sum()
        if independent_count > 0:
            max_circle_id = result_df['family_circle_id'].max()
            if max_circle_id >= 0:
                result_df.loc[independent_mask, 'family_circle_id'] = range(
                    max_circle_id + 1, max_circle_id + 1 + independent_count
                )
            else:
                result_df.loc[independent_mask, 'family_circle_id'] = range(independent_count)
        
        # 保存映射关系
        for idx, row in result_df.iterrows():
            self.family_circles[row[user_id_col]] = row['family_circle_id']
        
        total_circles = result_df['family_circle_id'].nunique()
        print(f"识别出 {total_circles} 个家庭圈")
        print(f"包含 {len(result_df) - independent_count} 个用户，{independent_count} 个独立用户")
        
        return result_df
    
    def _build_relationship_graph(self, df: pd.DataFrame, user_id_col: str) -> Dict:
        """
        基于规则构建用户关系图
        
        Returns:
            关系图字典，key为用户ID，value为关联用户集合
        """
        graph = defaultdict(set)
        
        # 1. 基于地址关联（相同地址的用户）
        addr_cols = [col for col in df.columns 
                    if any(keyword in str(col).lower() 
                          for keyword in ['地址', 'address', '位置', 'location'])]
        
        # 特殊处理基站标识，避免过度连接
        station_cols = [col for col in df.columns 
                      if any(keyword in str(col).lower() 
                            for keyword in ['基站', 'station'])]
        
        # 处理普通地址列（严格匹配）
        for addr_col in addr_cols[:2]:  # 最多处理2个普通地址列
            if addr_col in df.columns:
                for addr_value, group in df.groupby(addr_col):
                    if pd.notna(addr_value) and len(group) > 1:
                        users = group[user_id_col].unique()
                        # 为同一地址的所有用户建立连接
                        for i, u1 in enumerate(users):
                            for u2 in users[i+1:]:
                                graph[u1].add(u2)
                                graph[u2].add(u1)
        
        # 处理基站标识列（宽松匹配，仅当基站关联用户数小于阈值时才建立连接）
        station_user_limit = 50  # 基站关联用户数阈值，超过则不建立连接
        for station_col in station_cols[:1]:  # 最多处理1个基站列
            if station_col in df.columns:
                for station_value, group in df.groupby(station_col):
                    if pd.notna(station_value) and len(group) > 1 and len(group) <= station_user_limit:
                        users = group[user_id_col].unique()
                        # 为同一基站且用户数合理的用户建立连接
                        for i, u1 in enumerate(users):
                            for u2 in users[i+1:]:
                                graph[u1].add(u2)
                                graph[u2].add(u1)
        
        # 2. 基于账户关联（相同缴费账户的用户）
        account_cols = [col for col in df.columns 
                       if any(keyword in str(col).lower() 
                             for keyword in ['账户', 'account', '缴费', 'payment', '付费'])]
        
        for account_col in account_cols[:3]:  # 最多处理3个账户列
            if account_col in df.columns:
                for account_value, group in df.groupby(account_col):
                    if pd.notna(account_value) and len(group) > 1:
                        users = group[user_id_col].unique()
                        # 为同一账户的所有用户建立连接
                        for i, u1 in enumerate(users):
                            for u2 in users[i+1:]:
                                graph[u1].add(u2)
                                graph[u2].add(u1)
        
        # 3. 基于设备共享（共享设备的用户）
        device_cols = [col for col in df.columns 
                      if any(keyword in str(col).lower() 
                            for keyword in ['设备', 'device', '终端', 'terminal', '共享', 'share'])]
        
        for device_col in device_cols[:3]:  # 最多处理3个设备列
            if device_col in df.columns:
                for device_value, group in df.groupby(device_col):
                    if pd.notna(device_value) and len(group) > 1:
                        users = group[user_id_col].unique()
                        # 为共享同一设备的用户建立连接
                        for i, u1 in enumerate(users):
                            for u2 in users[i+1:]:
                                graph[u1].add(u2)
                                graph[u2].add(u1)
        
        return dict(graph)
    
    def _predict_with_classifier(self, df: pd.DataFrame, features: pd.DataFrame, 
                                user_id_col: str) -> pd.DataFrame:
        """
        使用训练好的分类器进行预测（分批处理以避免内存问题）
        
        Args:
            df: 数据框
            features: 特征数据框
            user_id_col: 用户ID列名
            
        Returns:
            包含家庭圈ID的结果数据框
        """
        # 合并特征，去重（避免重复数据）
        data = pd.merge(features, df[[user_id_col]], on=user_id_col, how='inner')
        data = data.drop_duplicates(subset=[user_id_col], keep='first')
        
        print(f"预测数据量: {len(data)} 条")
        
        # 准备特征
        feature_cols = [col for col in features.columns if col != user_id_col]
        X = data[feature_cols].fillna(0).values
        
        # 标准化
        X_scaled = self.scaler.transform(X)
        
        # 特征选择（如果训练时使用了）
        if self.feature_selector is not None:
            X_scaled = self.feature_selector.transform(X_scaled)
        
        # 分批预测以避免内存问题
        batch_size = 10000  # 每批处理1万条
        n_samples = len(X_scaled)
        y_pred_encoded = np.zeros(n_samples, dtype=int)
        
        print(f"开始分批预测，共 {n_samples} 条数据，每批 {batch_size} 条...")
        
        for i in range(0, n_samples, batch_size):
            end_idx = min(i + batch_size, n_samples)
            batch_X = X_scaled[i:end_idx]
            
            # 直接预测类别，不计算概率（节省内存）
            batch_pred = self.classifier.predict(batch_X)
            y_pred_encoded[i:end_idx] = batch_pred
            
            if (i // batch_size + 1) % 10 == 0:
                print(f"  已处理 {end_idx}/{n_samples} 条 ({end_idx/n_samples*100:.1f}%)")
        
        # 解码标签（将编码后的预测结果转换回原始标签）
        if hasattr(self.label_encoder, 'inverse_transform'):
            try:
                y_pred_labels = self.label_encoder.inverse_transform(y_pred_encoded)
            except:
                y_pred_labels = y_pred_encoded
        else:
            y_pred_labels = y_pred_encoded
        
        # 构建结果
        result_df = pd.DataFrame()
        result_df[user_id_col] = data[user_id_col].values
        
        # 保存原始标签（用于评估）
        result_df['predicted_label'] = y_pred_labels
        
        # 将预测结果转换为家庭圈ID（使用标签编码，保持与训练时一致的编码方式）
        # 这里直接使用编码后的数值作为family_circle_id，因为评估时需要与真实标签的编码对应
        result_df['family_circle_id'] = y_pred_encoded
        
        # 保存映射关系
        for idx, row in result_df.iterrows():
            self.family_circles[row[user_id_col]] = row['family_circle_id']
        
        total_circles = result_df['family_circle_id'].nunique()
        print(f"识别出 {total_circles} 个家庭圈")
        print(f"包含 {len(result_df)} 个用户")
        
        return result_df
    
    def _graph_clustering(self, graph: Dict, all_users: np.ndarray) -> List[List]:
        """
        使用图的连通分量进行聚类（迭代版本，避免递归深度问题）
        
        Args:
            graph: 关系图字典
            all_users: 所有用户ID数组
            
        Returns:
            聚类结果列表，每个元素是一个用户列表（一个家庭圈）
        """
        visited = set()
        clusters = []
        
        # 确保用户ID类型一致（统一转换为字符串）
        graph_typed = {}
        user_str_to_orig = {}  # 字符串ID到原始ID的映射
        
        for k, v in graph.items():
            key_str = str(k)
            graph_typed[key_str] = {str(u) for u in v}
            user_str_to_orig[key_str] = k
        
        # 为所有用户建立映射
        for user in all_users:
            user_str = str(user)
            if user_str not in user_str_to_orig:
                user_str_to_orig[user_str] = user
        
        # 使用迭代版本的DFS（使用栈）
        for user in all_users:
            user_str = str(user)
            if user_str not in visited:
                cluster = []
                stack = [user_str]
                
                while stack:
                    current = stack.pop()
                    if current not in visited:
                        visited.add(current)
                        # 添加原始用户ID到cluster
                        if current in user_str_to_orig:
                            cluster.append(user_str_to_orig[current])
                        
                        # 添加邻居到栈
                        for neighbor in graph_typed.get(current, set()):
                            if neighbor not in visited:
                                stack.append(neighbor)
                
                if len(cluster) > 0:
                    clusters.append(cluster)
        
        return clusters
    
    def identify_key_persons(self, df: pd.DataFrame, family_circle_df: pd.DataFrame,
                            user_id_col: str) -> pd.DataFrame:
        """
        识别家庭关键人
        关键人特征：账户主、缴费人、通信中心度高等
        
        Args:
            df: 原始数据框
            family_circle_df: 包含家庭圈ID的数据框
            
        Returns:
            包含关键人标识的结果数据框
        """
        result_df = family_circle_df.copy()
        result_df['is_key_person'] = 0
        
        # 为每个家庭圈识别关键人
        for circle_id, group in family_circle_df.groupby('family_circle_id'):
            user_ids = group[user_id_col].values
            
            # 计算每个用户的"关键度"得分
            key_scores = {}
            
            for user_id in user_ids:
                score = 0
                user_data = df[df[user_id_col] == user_id]
                
                if len(user_data) > 0:
                    # 1. 账户主特征（如果有账户相关列）
                    account_cols = [col for col in df.columns 
                                  if '账户' in str(col) or 'account' in str(col).lower()]
                    if account_cols:
                        # 账户数量多或账户共享多的用户更可能是关键人
                        score += len(account_cols) * 2
                    
                    # 2. 缴费特征（如果有缴费相关列）
                    payment_cols = [col for col in df.columns 
                                  if '缴费' in str(col) or 'payment' in str(col).lower()]
                    if payment_cols:
                        score += len(payment_cols) * 3
                    
                    # 3. 通信中心度（如果有通信相关列）
                    comm_cols = [col for col in df.columns 
                               if '通话' in str(col) or 'call' in str(col).lower()]
                    if comm_cols:
                        # 通信频率高的用户更可能是关键人
                        for col in comm_cols:
                            if col in user_data.columns:
                                score += user_data[col].sum() if user_data[col].dtype in ['int64', 'float64'] else 1
                    
                    # 4. 地址稳定性（地址相关列）
                    addr_cols = [col for col in df.columns 
                               if '地址' in str(col) or 'address' in str(col).lower()]
                    if addr_cols:
                        score += len(addr_cols) * 1
                
                key_scores[user_id] = score
            
            # 选择得分最高的用户作为关键人
            if key_scores:
                key_person = max(key_scores, key=key_scores.get)
                result_df.loc[result_df[user_id_col] == key_person, 'is_key_person'] = 1
                self.key_persons[circle_id] = key_person
        
        key_person_count = result_df['is_key_person'].sum()
        print(f"识别出 {key_person_count} 个家庭关键人")
        
        return result_df
    
    def define_relationship_rules(self) -> Dict:
        """
        定义家庭成员关系判定规则
        
        Returns:
            关系判定规则字典
        """
        rules = {
            'same_address': {
                'threshold': 0.8,  # 地址相似度阈值
                'weight': 0.3
            },
            'same_account': {
                'threshold': 1.0,  # 完全相同的账户
                'weight': 0.4
            },
            'shared_device': {
                'threshold': 1,    # 至少共享1个设备
                'weight': 0.2
            },
            'communication': {
                'threshold': 0.5,  # 通信频率阈值
                'weight': 0.1
            }
        }
        
        self.relationship_rules = rules
        return rules
    
    def predict_relationships(self, user1_id: str, user2_id: str, 
                            df: pd.DataFrame, user_id_col: str) -> Tuple[bool, float]:
        """
        预测两个用户是否为家庭成员
        
        Args:
            user1_id: 用户1 ID
            user2_id: 用户2 ID
            df: 数据框
            user_id_col: 用户ID列名
            
        Returns:
            (是否为家庭成员, 置信度)
        """
        if not self.relationship_rules:
            self.define_relationship_rules()
        
        user1_data = df[df[user_id_col] == user1_id]
        user2_data = df[df[user_id_col] == user2_id]
        
        if len(user1_data) == 0 or len(user2_data) == 0:
            return False, 0.0
        
        total_score = 0.0
        total_weight = 0.0
        
        # 检查地址关联
        addr_cols = [col for col in df.columns 
                    if '地址' in str(col) or 'address' in str(col).lower()]
        if addr_cols:
            for col in addr_cols[:2]:
                if col in user1_data.columns and col in user2_data.columns:
                    addr1 = user1_data[col].iloc[0] if len(user1_data) > 0 else None
                    addr2 = user2_data[col].iloc[0] if len(user2_data) > 0 else None
                    if pd.notna(addr1) and pd.notna(addr2) and addr1 == addr2:
                        total_score += self.relationship_rules['same_address']['weight']
                    total_weight += self.relationship_rules['same_address']['weight']
        
        # 检查账户关联
        account_cols = [col for col in df.columns 
                       if '账户' in str(col) or 'account' in str(col).lower()]
        if account_cols:
            for col in account_cols[:2]:
                if col in user1_data.columns and col in user2_data.columns:
                    acc1 = user1_data[col].iloc[0] if len(user1_data) > 0 else None
                    acc2 = user2_data[col].iloc[0] if len(user2_data) > 0 else None
                    if pd.notna(acc1) and pd.notna(acc2) and acc1 == acc2:
                        total_score += self.relationship_rules['same_account']['weight']
                    total_weight += self.relationship_rules['same_account']['weight']
        
        # 计算置信度
        if total_weight > 0:
            confidence = total_score / total_weight
            is_family = confidence >= 0.5  # 综合得分阈值
        else:
            confidence = 0.0
            is_family = False
        
        return is_family, confidence
    
    def evaluate_model(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict:
        """
        评估模型性能
        
        Args:
            y_true: 真实标签
            y_pred: 预测标签
            
        Returns:
            评估指标字典
        """
        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred, average='weighted', zero_division=0)
        recall = recall_score(y_true, y_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_true, y_pred, average='weighted', zero_division=0)
        
        metrics = {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1
        }
        
        print("\n模型评估结果:")
        print(f"准确率 (Accuracy): {accuracy:.4f}")
        print(f"精确率 (Precision): {precision:.4f}")
        print(f"召回率 (Recall): {recall:.4f}")
        print(f"F1值 (F1-Score): {f1:.4f}")
        
        return metrics

