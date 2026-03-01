import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

"""
主程序 - 家庭圈用户识别模型
"""
import pandas as pd
import numpy as np
import os
from core.data_loader import DataLoader
\
base_dir = '/home/liu/Code/Repos/wthh'
from core.feature_engineering import FeatureEngineer
from core.feature_engineering_enhanced import EnhancedFeatureEngineer
from core.family_circle_model import FamilyCircleModel
from tools.report_generator import ReportGenerator
import json

def main():
    """主函数"""
    print("="*60)
    print("家庭圈用户识别模型")
    print("="*60)
    
    # 1. 加载数据
    print("\n[步骤1] 加载数据...")
    # 获取项目根目录（main.py所在目录）
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, 'data', 'AI+数据1：数据应用开发-家庭圈用户识别模型.xlsx')
    
    if not os.path.exists(file_path):
        print(f"错误：找不到数据文件 {file_path}")
        return
    
    loader = DataLoader(file_path)
    train_df, valid_df, test_df = loader.load_data()
    
    # 扁平化列名
    train_df = loader.flatten_columns(train_df)
    valid_df = loader.flatten_columns(valid_df)
    test_df = loader.flatten_columns(test_df)
    
    # 识别用户ID列
    user_id_col = loader.get_user_id_column(train_df)
    print(f"用户ID列: {user_id_col}")
    
    # 2. 特征工程（使用增强版）
    print("\n[步骤2] 特征工程（增强版）...")
    feature_engineer = EnhancedFeatureEngineer()
    
    # 为训练数据提取特征
    print("\n[2.1] 为训练数据提取特征...")
    train_features = feature_engineer.extract_all_features(train_df, user_id_col)
    print(f"训练数据特征提取完成，共 {len(train_features.columns) - 1} 个特征，{len(train_features)} 条记录")
    
    # 为验证数据提取特征
    print("\n[2.2] 为验证数据提取特征...")
    valid_features = feature_engineer.extract_all_features(valid_df, user_id_col)
    print(f"验证数据特征提取完成，共 {len(valid_features.columns) - 1} 个特征，{len(valid_features)} 条记录")
    
    # 为测试数据提取特征
    print("\n[2.3] 为测试数据提取特征...")
    test_features = feature_engineer.extract_all_features(test_df, user_id_col)
    print(f"测试数据特征提取完成，共 {len(test_features.columns) - 1} 个特征，{len(test_features)} 条记录")
    
    # 3. 查找标签列（如果有）
    label_col = None
    # 优先查找指定的标签列名
    possible_label_names = ['所属泛家庭编码', 'family_c_id', '家庭圈', 'family', '标签', 'label', 
                           '家庭', 'family_circle', '家庭圈id', 'family_id', '家庭圈编号', 'family_circle_id']
    
    # 先精确匹配
    for col in train_df.columns:
        if str(col) == '所属泛家庭编码' or str(col) == 'family_c_id':
            label_col = col
            print(f"找到标签列: {label_col}")
            break
    
    # 如果没找到，再模糊匹配
    if label_col is None:
        for col in train_df.columns:
            col_lower = str(col).lower()
            if any(name in col_lower for name in possible_label_names):
                label_col = col
                print(f"找到标签列: {label_col}")
                break
    
    if label_col and label_col in train_df.columns:
        print(f"标签列: {label_col}")
        print(f"标签列唯一值数量: {train_df[label_col].nunique()}")
        print(f"标签列唯一值示例: {train_df[label_col].unique()[:10]}")
        print(f"标签列缺失值数量: {train_df[label_col].isna().sum()}")
    else:
        print("\n警告：未找到标签列，将使用无监督方法")
        print("训练数据列名:", train_df.columns.tolist()[:20])
    
    # 4. 模型训练和预测
    print("\n[步骤3] 构建家庭圈识别模型...")
    model = FamilyCircleModel()
    
    # 定义关系规则
    model.define_relationship_rules()
    
    # 如果有标签，使用监督学习训练模型
    if label_col and label_col in train_df.columns:
        print("使用带标签数据训练监督学习模型...")
        model.train_supervised_model(train_df, train_features, user_id_col, label_col)
    
    # 识别家庭圈
    train_result = model.identify_family_circles(
        train_df, user_id_col, features=train_features, original_df=train_df, label_col=label_col
    )
    
    # 识别关键人
    train_result = model.identify_key_persons(
        train_df, train_result, user_id_col
    )
    
    # 对验证数据进行预测
    print("\n[步骤4] 对验证数据进行预测...")
    valid_result = model.identify_family_circles(
        valid_df, user_id_col, features=valid_features, original_df=valid_df
    )
    valid_result = model.identify_key_persons(
        valid_df, valid_result, user_id_col
    )
    
    # 对测试数据进行预测
    print("\n[步骤5] 对测试数据进行预测...")
    test_result = model.identify_family_circles(
        test_df, user_id_col, features=test_features, original_df=test_df
    )
    test_result = model.identify_key_persons(
        test_df, test_result, user_id_col
    )
    
    # 6. 保存结果
    print("\n[步骤6] 保存结果...")
    output_dir = os.path.join(base_dir, 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    train_result.to_csv(os.path.join(output_dir, 'train_result.csv'), index=False, encoding='utf-8-sig')
    valid_result.to_csv(os.path.join(output_dir, 'valid_result.csv'), index=False, encoding='utf-8-sig')
    test_result.to_csv(os.path.join(output_dir, 'test_result.csv'), index=False, encoding='utf-8-sig')
    
    print(f"结果已保存到 {output_dir}")
    
    # 7. 模型评估（如果有标签）
    if label_col and label_col in train_df.columns:
        print("\n[步骤7] 模型评估...")
        # 合并标签
        train_with_label = pd.merge(
            train_result, 
            train_df[[user_id_col, label_col]], 
            on=user_id_col, 
            how='inner'
        )
        
        print(f"评估数据量: {len(train_with_label)} 条")
        print(f"真实标签唯一值数量: {train_with_label[label_col].nunique()}")
        print(f"预测标签唯一值数量: {train_with_label['family_circle_id'].nunique()}")
        
        # 使用训练时的编码器编码真实标签和预测标签
        if hasattr(model, 'label_encoder') and model.label_encoder is not None:
            try:
                # 使用训练时的编码器编码真实标签
                y_true = model.label_encoder.transform(train_with_label[label_col].values)
                # 预测结果已经是编码后的，直接使用
                y_pred = train_with_label['family_circle_id'].values
                
                print(f"使用训练时的编码器进行评估")
            except Exception as e:
                print(f"编码器编码失败: {e}")
                # 如果编码失败，使用简单映射
                if train_with_label[label_col].dtype == 'object':
                    unique_labels = sorted(train_with_label[label_col].unique())
                    label_map = {label: idx for idx, label in enumerate(unique_labels)}
                    y_true = train_with_label[label_col].map(label_map).values
                else:
                    y_true = train_with_label[label_col].values
                y_pred = train_with_label['family_circle_id'].values
        else:
            # 将标签转换为数值ID以便评估
            if train_with_label[label_col].dtype == 'object':
                unique_labels = sorted(train_with_label[label_col].unique())
                label_map = {label: idx for idx, label in enumerate(unique_labels)}
                y_true = train_with_label[label_col].map(label_map).values
            else:
                y_true = train_with_label[label_col].values
            y_pred = train_with_label['family_circle_id'].values
        
        # 检查标签范围
        print(f"真实标签范围: [{y_true.min()}, {y_true.max()}]")
        print(f"预测标签范围: [{y_pred.min()}, {y_pred.max()}]")
        
        # 评估模型
        metrics = model.evaluate_model(y_true, y_pred)
        
        # 将numpy类型转换为Python原生类型以便JSON序列化
        metrics_serializable = {
            'accuracy': float(metrics['accuracy']),
            'precision': float(metrics['precision']),
            'recall': float(metrics['recall']),
            'f1_score': float(metrics['f1_score'])
        }
        
        # 保存评估结果
        with open(os.path.join(output_dir, 'model_metrics.json'), 'w', encoding='utf-8') as f:
            json.dump(metrics_serializable, f, ensure_ascii=False, indent=2)
    
    # 8. 生成统计报告
    print("\n[步骤8] 生成统计报告...")
    stats = {
        '训练数据': {
            '总用户数': int(len(train_result)),
            '家庭圈数量': int(train_result['family_circle_id'].nunique()),
            '关键人数量': int(train_result['is_key_person'].sum())
        },
        '验证数据': {
            '总用户数': int(len(valid_result)),
            '家庭圈数量': int(valid_result['family_circle_id'].nunique()),
            '关键人数量': int(valid_result['is_key_person'].sum())
        },
        '测试数据': {
            '总用户数': int(len(test_result)),
            '家庭圈数量': int(test_result['family_circle_id'].nunique()),
            '关键人数量': int(test_result['is_key_person'].sum())
        }
    }
    
    with open(os.path.join(output_dir, 'statistics.json'), 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    
    print("\n统计报告:")
    for key, value in stats.items():
        print(f"\n{key}:")
        for k, v in value.items():
            print(f"  {k}: {v}")
    
    # 8. 生成报告文档
    print("\n[步骤9] 生成报告文档...")
    report_generator = ReportGenerator(output_dir)
    
    # 生成所有报告
    report_generator.generate_all_reports(
        feature_df=train_features,
        original_df=train_df,
        result_df=train_result,
        metrics=None  # 如果有标签可以计算metrics
    )
    
    print("\n" + "="*60)
    print("处理完成！")
    print("="*60)
    
    return train_result, valid_result, test_result, model

if __name__ == '__main__':
    train_result, valid_result, test_result, model = main()

