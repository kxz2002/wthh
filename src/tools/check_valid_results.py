import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(os.path.expanduser(__file__)))))

import pandas as pd
import os

# 检查结果文件是否存在
output_file = 'output/valid_result.csv'
if os.path.exists(output_file):
    df = pd.read_csv(output_file)
    print('验证集结果:')
    print(f'总用户数: {len(df)}')
    print(f'家庭圈数量: {df["family_circle_id"].nunique()}')
    
    # 计算家庭圈大小并排序
    circle_sizes = df.groupby('family_circle_id').size().sort_values(ascending=False)
    print('\n家庭圈大小前10名:')
    print(circle_sizes.head(10))
    
    print('\n家庭圈大小统计:')
    print(circle_sizes.describe())
    
    # 检查最大的家庭圈
    max_circle_id = circle_sizes.idxmax()
    max_circle_size = circle_sizes.max()
    print(f'\n最大的家庭圈ID: {max_circle_id}，大小: {max_circle_size}')
    
    # 检查是否有异常大的家庭圈
    if max_circle_size > 1000:
        print(f'警告: 存在异常大的家庭圈，大小为 {max_circle_size}')
else:
    print(f'未找到结果文件: {output_file}')
    print('请先运行主程序生成结果文件')
