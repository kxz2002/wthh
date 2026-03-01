import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(os.path.expanduser(__file__)))))

import pandas as pd
import os

def check_results(file_name, data_name):
    """检查结果文件"""
    output_file = f'output/{file_name}'
    if os.path.exists(output_file):
        df = pd.read_csv(output_file)
        print(f'\n{data_name}结果:')
        print(f'总用户数: {len(df)}')
        print(f'家庭圈数量: {df["family_circle_id"].nunique()}')
        
        # 计算家庭圈大小并排序
        circle_sizes = df.groupby('family_circle_id').size().sort_values(ascending=False)
        print(f'家庭圈大小前5名:')
        print(circle_sizes.head(5))
        
        print(f'家庭圈大小统计:')
        print(circle_sizes.describe())
        
        # 检查最大的家庭圈
        max_circle_id = circle_sizes.idxmax()
        max_circle_size = circle_sizes.max()
        print(f'最大的家庭圈ID: {max_circle_id}，大小: {max_circle_size}')
        
        # 检查是否有异常大的家庭圈
        if max_circle_size > 1000:
            print(f'警告: 存在异常大的家庭圈，大小为 {max_circle_size}')
            return True
    else:
        print(f'未找到{data_name}结果文件: {output_file}')
    return False

# 检查所有结果文件
has_large_circle = False
has_large_circle |= check_results('train_result.csv', '训练集')
has_large_circle |= check_results('valid_result.csv', '验证集')
has_large_circle |= check_results('test_result.csv', '测试集')

if not has_large_circle:
    print('\n所有数据集未发现异常大的家庭圈（>1000人）')
