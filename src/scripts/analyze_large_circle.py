import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
import os
import numpy as np
base_dir = "/home/liu/Code/Repos/wthh"
from core.family_circle_model import FamilyCircleModel

def analyze_large_circle():
    """分析大型家庭圈形成的原因"""
    # 检查是否有测试数据
    test_file = 'output/test_result.csv'
    if not os.path.exists(test_file):
        print('未找到测试结果文件，请先运行主程序')
        return
    
    # 读取测试结果
    test_result = pd.read_csv(test_file)
    
    # 找出最大的家庭圈
    circle_sizes = test_result.groupby('family_circle_id').size().sort_values(ascending=False)
    max_circle_id = circle_sizes.idxmax()
    max_circle_size = circle_sizes.max()
    
    print(f'最大的家庭圈ID: {max_circle_id}，大小: {max_circle_size}')
    
    # 提取最大家庭圈中的用户
    large_circle_users = test_result[test_result['family_circle_id'] == max_circle_id]
    
    # 读取原始测试数据
    from core.data_loader import DataLoader
    data_file = r'data\AI+数据1：数据应用开发-家庭圈用户识别模型.xlsx'
    if os.path.exists(data_file):
        loader = DataLoader(data_file)
        _, _, test_df = loader.load_data()
        test_df = loader.flatten_columns(test_df)
        
        # 获取用户ID列
        user_id_col = loader.get_user_id_column(test_df)
        
        # 合并原始数据和预测结果
        merged_data = pd.merge(
            large_circle_users,
            test_df,
            on=user_id_col,
            how='inner'
        )
        
        print(f'合并后的数据量: {len(merged_data)}')
        
        # 分析可能导致过度连接的字段
        print('\n分析可能导致过度连接的字段:')
        
        # 1. 分析地址字段
        addr_cols = [col for col in test_df.columns 
                    if any(keyword in str(col).lower() 
                          for keyword in ['地址', 'address', '基站', 'station', '位置', 'location'])]
        
        print(f'\n地址相关字段: {addr_cols}')
        for addr_col in addr_cols[:3]:  # 最多分析3个地址字段
            if addr_col in merged_data.columns:
                print(f'\n{addr_col}字段值分布:')
                value_counts = merged_data[addr_col].value_counts().head(10)
                print(value_counts)
                
                # 检查是否有一个值被大量用户共享
                if len(value_counts) > 0:
                    top_value_count = value_counts.iloc[0]
                    if top_value_count > max_circle_size * 0.5:
                        print(f'警告: {addr_col}字段中，值 "{value_counts.index[0]}" 被 {top_value_count} 个用户共享，占家庭圈用户的 {top_value_count/max_circle_size*100:.2f}%')
        
        # 2. 分析账户字段
        account_cols = [col for col in test_df.columns 
                       if any(keyword in str(col).lower() 
                             for keyword in ['账户', 'account', '缴费', 'payment', '付费'])]
        
        print(f'\n账户相关字段: {account_cols}')
        for account_col in account_cols[:3]:  # 最多分析3个账户字段
            if account_col in merged_data.columns:
                print(f'\n{account_col}字段值分布:')
                value_counts = merged_data[account_col].value_counts().head(10)
                print(value_counts)
                
                if len(value_counts) > 0:
                    top_value_count = value_counts.iloc[0]
                    if top_value_count > max_circle_size * 0.5:
                        print(f'警告: {account_col}字段中，值 "{value_counts.index[0]}" 被 {top_value_count} 个用户共享，占家庭圈用户的 {top_value_count/max_circle_size*100:.2f}%')
        
        # 3. 分析设备字段
        device_cols = [col for col in test_df.columns 
                      if any(keyword in str(col).lower() 
                            for keyword in ['设备', 'device', '终端', 'terminal', '共享', 'share'])]
        
        print(f'\n设备相关字段: {device_cols}')
        for device_col in device_cols[:3]:  # 最多分析3个设备字段
            if device_col in merged_data.columns:
                print(f'\n{device_col}字段值分布:')
                value_counts = merged_data[device_col].value_counts().head(10)
                print(value_counts)
                
                if len(value_counts) > 0:
                    top_value_count = value_counts.iloc[0]
                    if top_value_count > max_circle_size * 0.5:
                        print(f'警告: {device_col}字段中，值 "{value_counts.index[0]}" 被 {top_value_count} 个用户共享，占家庭圈用户的 {top_value_count/max_circle_size*100:.2f}%')
    else:
        print('未找到原始数据文件，无法进行详细分析')

if __name__ == '__main__':
    analyze_large_circle()