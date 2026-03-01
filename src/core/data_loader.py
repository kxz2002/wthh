"""
数据加载模块
处理Excel文件，第一行是英文表头，第二行是中文表头，第三行开始是数据
"""
import pandas as pd
import numpy as np
from typing import Tuple, List

class DataLoader:
    def __init__(self, file_path: str):
        """
        初始化数据加载器
        
        Args:
            file_path: Excel文件路径
        """
        self.file_path = file_path
        self.xls = None
        self.train_df = None  # 带标签数据
        self.valid_df = None  # 验证数据（不带标签）
        self.test_df = None   # 测试数据（不带标签）
        
    def load_data(self):
        """加载所有sheet数据"""
        self.xls = pd.ExcelFile(self.file_path)
        
        # 读取第一个sheet（带标签数据）
        # header=[0,1]表示使用前两行作为多级表头
        self.train_df = pd.read_excel(self.xls, sheet_name=0, header=[0,1])
        
        # 读取第二个sheet（不带标签数据）
        self.valid_df = pd.read_excel(self.xls, sheet_name=1, header=[0,1])
        
        # 读取第三个sheet（不带标签数据）
        self.test_df = pd.read_excel(self.xls, sheet_name=2, header=[0,1])
        
        print(f"训练数据形状: {self.train_df.shape}")
        print(f"验证数据形状: {self.valid_df.shape}")
        print(f"测试数据形状: {self.test_df.shape}")
        
        return self.train_df, self.valid_df, self.test_df
    
    def get_column_info(self, df: pd.DataFrame) -> dict:
        """
        获取列信息，处理多级表头
        
        Returns:
            dict: 包含列名映射的字典
        """
        columns_info = {}
        for col in df.columns:
            if isinstance(col, tuple):
                eng_name = col[0]
                chn_name = col[1]
                columns_info[eng_name] = chn_name
            else:
                columns_info[col] = col
        return columns_info
    
    def flatten_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        扁平化多级表头，使用中文列名
        
        Args:
            df: 原始DataFrame
            
        Returns:
            扁平化后的DataFrame
        """
        df_flat = df.copy()
        new_columns = []
        
        for col in df.columns:
            if isinstance(col, tuple):
                # 使用中文列名，如果中文为空则使用英文
                chn_name = col[1] if pd.notna(col[1]) and col[1] != '' else col[0]
                new_columns.append(chn_name)
            else:
                new_columns.append(col)
        
        df_flat.columns = new_columns
        return df_flat
    
    def get_user_id_column(self, df: pd.DataFrame) -> str:
        """
        自动识别用户ID列
        
        Returns:
            用户ID列名
        """
        # 常见的用户ID列名
        possible_names = ['用户ID', 'user_id', '用户id', 'ID', 'id', '用户编号']
        
        for col in df.columns:
            if isinstance(col, tuple):
                col_name = col[1] if pd.notna(col[1]) else col[0]
            else:
                col_name = col
                
            if any(name in str(col_name) for name in possible_names):
                return col
        
        # 如果找不到，返回第一列
        return df.columns[0]

