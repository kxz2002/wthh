import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(os.path.expanduser(__file__)))))

"""
快速查看结果脚本
用于查看和统计识别结果
"""
import pandas as pd
import json
import os

def get_output_dir():
    """获取输出目录"""
    return os.path.join(base_dir, 'src', 'output')

def view_results():
    """查看结果"""
    output_dir = get_output_dir()
    
    print("="*60)
    print("家庭圈用户识别结果查看")
    print("="*60)
    
    # 检查结果文件是否存在
    result_files = {
        '训练数据': 'train_result.csv',
        '验证数据': 'valid_result.csv',
        '测试数据': 'test_result.csv'
    }
    
    for name, filename in result_files.items():
        filepath = os.path.join(output_dir, filename)
        if os.path.exists(filepath):
            print(f"\n【{name}】")
            print("-"*60)
            df = pd.read_csv(filepath, encoding='utf-8-sig')
            
            # 基本统计
            total_users = len(df)
            total_circles = df['家庭圈ID'].nunique()
            key_persons = df['是否关键人'].sum()
            
            print(f"总用户数: {total_users}")
            print(f"家庭圈数量: {total_circles}")
            print(f"关键人数量: {key_persons}")
            
            if total_circles > 0:
                avg_size = total_users / total_circles
                print(f"平均家庭圈大小: {avg_size:.2f} 人")
                
                # 家庭圈大小分布
                circle_sizes = df.groupby('家庭圈ID').size()
                print(f"最大家庭圈: {circle_sizes.max()} 人")
                print(f"最小家庭圈: {circle_sizes.min()} 人")
            
            # 显示前几个家庭圈
            print(f"\n前5个家庭圈详情:")
            for circle_id, group in df.groupby('家庭圈ID').head(5).groupby('家庭圈ID'):
                members = group['用户ID'].tolist()
                key_person = group[group['是否关键人'] == 1]
                key_person_id = key_person['用户ID'].iloc[0] if len(key_person) > 0 else None
                
                print(f"  家庭圈 #{circle_id}: {members}")
                if key_person_id:
                    print(f"    关键人: {key_person_id} 👑")
        else:
            print(f"\n【{name}】")
            print(f"  文件不存在: {filepath}")
            print("  请先运行 main.py 生成结果")
    
    # 查看统计信息
    stats_file = os.path.join(output_dir, 'statistics.json')
    if os.path.exists(stats_file):
        print("\n" + "="*60)
        print("统计信息")
        print("="*60)
        with open(stats_file, 'r', encoding='utf-8') as f:
            stats = json.load(f)
            for key, value in stats.items():
                print(f"\n{key}:")
                for k, v in value.items():
                    print(f"  {k}: {v}")
    
    # 查看报告文件
    report_files = [
        '特征工程报告.txt',
        '模型评估报告.txt',
        '结果说明文档.txt'
    ]
    
    print("\n" + "="*60)
    print("报告文件")
    print("="*60)
    for report_file in report_files:
        filepath = os.path.join(output_dir, report_file)
        if os.path.exists(filepath):
            print(f"✓ {report_file} (已生成)")
        else:
            print(f"✗ {report_file} (未生成)")
    
    print("\n" + "="*60)
    print("查看完成！")
    print("="*60)
    print("\n提示:")
    print("1. 可以用Excel打开CSV文件查看详细结果")
    print("2. 可以用文本编辑器打开报告文件查看详情")
    print("3. 运行 'python app.py' 启动Web界面可视化查看")

def view_specific_user(user_id):
    """查看特定用户的信息"""
    output_dir = get_output_dir()
    
    result_files = ['train_result.csv', 'valid_result.csv', 'test_result.csv']
    
    for filename in result_files:
        filepath = os.path.join(output_dir, filename)
        if os.path.exists(filepath):
            df = pd.read_csv(filepath, encoding='utf-8-sig')
            user_info = df[df['用户ID'].astype(str) == str(user_id)]
            
            if len(user_info) > 0:
                print(f"\n找到用户 {user_id} (在 {filename} 中):")
                print("-"*60)
                
                circle_id = user_info.iloc[0]['家庭圈ID']
                is_key = user_info.iloc[0]['是否关键人']
                
                print(f"家庭圈ID: {circle_id}")
                print(f"是否关键人: {'是 👑' if is_key == 1 else '否'}")
                
                # 查找家庭成员
                family_members = df[df['家庭圈ID'] == circle_id]
                print(f"\n家庭成员 ({len(family_members)} 人):")
                for _, member in family_members.iterrows():
                    marker = "👑" if member['是否关键人'] == 1 else "  "
                    print(f"  {marker} {member['用户ID']}")
                
                return
    
    print(f"\n未找到用户 {user_id}")

def view_family_circle(circle_id):
    """查看特定家庭圈的信息"""
    output_dir = get_output_dir()
    
    result_files = ['train_result.csv', 'valid_result.csv', 'test_result.csv']
    
    for filename in result_files:
        filepath = os.path.join(output_dir, filename)
        if os.path.exists(filepath):
            df = pd.read_csv(filepath, encoding='utf-8-sig')
            circle_members = df[df['家庭圈ID'] == circle_id]
            
            if len(circle_members) > 0:
                print(f"\n家庭圈 #{circle_id} (在 {filename} 中):")
                print("-"*60)
                print(f"成员数量: {len(circle_members)} 人")
                
                key_person = circle_members[circle_members['是否关键人'] == 1]
                if len(key_person) > 0:
                    print(f"关键人: {key_person.iloc[0]['用户ID']} 👑")
                
                print(f"\n所有成员:")
                for _, member in circle_members.iterrows():
                    marker = "👑" if member['是否关键人'] == 1 else "  "
                    print(f"  {marker} 用户ID: {member['用户ID']}")
                
                return
    
    print(f"\n未找到家庭圈 #{circle_id}")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'user' and len(sys.argv) > 2:
            # 查看特定用户: python view_results.py user 1001
            view_specific_user(sys.argv[2])
        elif sys.argv[1] == 'circle' and len(sys.argv) > 2:
            # 查看特定家庭圈: python view_results.py circle 0
            view_family_circle(int(sys.argv[2]))
        else:
            print("用法:")
            print("  python view_results.py              # 查看所有结果")
            print("  python view_results.py user 1001    # 查看用户1001的信息")
            print("  python view_results.py circle 0     # 查看家庭圈0的信息")
    else:
        # 查看所有结果
        view_results()

