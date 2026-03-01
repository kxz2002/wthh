import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(os.path.expanduser(__file__)))))

"""
检查数据中的标签列
"""
import pandas as pd
import os
from core.data_loader import DataLoader
\
base_dir = '/home/liu/Code/Repos/wthh'
file_path = os.path.join(base_dir, 'src', 'data', 'AI+数据1：数据应用开发-家庭圈用户识别模型.xlsx')

loader = DataLoader(file_path)
train_df, valid_df, test_df = loader.load_data()

# 扁平化列名
train_df = loader.flatten_columns(train_df)

print("训练数据列名:")
print(train_df.columns.tolist())
print("\n训练数据前5行:")
print(train_df.head())
print("\n训练数据形状:", train_df.shape)

