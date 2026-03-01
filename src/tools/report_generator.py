import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(os.path.expanduser(__file__)))))

"""
报告生成模块
生成特征工程报告、模型评估报告和结果说明文档
"""
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime
from typing import Dict, List

class ReportGenerator:
    def __init__(self, output_dir: str = None):
        """
        初始化报告生成器
        
        Args:
            output_dir: 输出目录
        """
        if output_dir is None:
            output_dir = os.path.join(base_dir, 'src', 'output')
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
    def generate_feature_engineering_report(self, feature_df: pd.DataFrame, 
                                           original_df: pd.DataFrame) -> str:
        """
        生成特征工程报告
        
        Args:
            feature_df: 特征数据框
            original_df: 原始数据框
            
        Returns:
            报告文件路径
        """
        report_lines = []
        report_lines.append("="*80)
        report_lines.append("特征工程报告")
        report_lines.append("="*80)
        report_lines.append(f"\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # 1. 数据概览
        report_lines.append("1. 数据概览")
        report_lines.append("-"*80)
        report_lines.append(f"原始数据维度: {original_df.shape[0]} 行 × {original_df.shape[1]} 列")
        report_lines.append(f"特征数据维度: {feature_df.shape[0]} 行 × {feature_df.shape[1]} 列")
        report_lines.append(f"生成特征数量: {feature_df.shape[1] - 1} 个（不含用户ID列）\n")
        
        # 2. 特征分类
        report_lines.append("2. 特征分类")
        report_lines.append("-"*80)
        
        feature_categories = {
            '地址关联性特征': [col for col in feature_df.columns if '地址' in str(col) or 'address' in str(col).lower()],
            '缴费账户关联性特征': [col for col in feature_df.columns if '账户' in str(col) or 'account' in str(col).lower() or '缴费' in str(col) or 'payment' in str(col).lower()],
            '终端共享特征': [col for col in feature_df.columns if '设备' in str(col) or 'device' in str(col).lower() or '终端' in str(col) or 'terminal' in str(col).lower() or '共享' in str(col) or 'share' in str(col).lower()],
            '通信行为特征': [col for col in feature_df.columns if '通话' in str(col) or 'call' in str(col).lower() or '联系人' in str(col) or 'contact' in str(col).lower() or '通信' in str(col) or 'communication' in str(col).lower()],
            '基础信息特征': [col for col in feature_df.columns if '性别' in str(col) or 'gender' in str(col).lower() or '年龄' in str(col) or 'age' in str(col).lower()]
        }
        
        for category, features in feature_categories.items():
            if features:
                report_lines.append(f"\n{category}:")
                for feat in features:
                    if feat in feature_df.columns:
                        stats = feature_df[feat].describe()
                        report_lines.append(f"  - {feat}")
                        report_lines.append(f"    均值: {stats['mean']:.4f}, 标准差: {stats['std']:.4f}, 范围: [{stats['min']:.4f}, {stats['max']:.4f}]")
        
        # 3. 特征重要性分析（如果有）
        report_lines.append("\n3. 特征统计信息")
        report_lines.append("-"*80)
        report_lines.append("\n所有特征的基本统计:")
        numeric_features = feature_df.select_dtypes(include=[np.number]).columns.tolist()
        if '用户ID' in numeric_features:
            numeric_features.remove('用户ID')
        
        stats_df = feature_df[numeric_features].describe().T
        report_lines.append(stats_df.to_string())
        
        # 4. 缺失值处理
        report_lines.append("\n\n4. 缺失值处理")
        report_lines.append("-"*80)
        missing_counts = feature_df.isnull().sum()
        missing_features = missing_counts[missing_counts > 0]
        if len(missing_features) > 0:
            report_lines.append("存在缺失值的特征:")
            for feat, count in missing_features.items():
                report_lines.append(f"  - {feat}: {count} 个缺失值 ({count/len(feature_df)*100:.2f}%)")
        else:
            report_lines.append("所有特征均无缺失值")
        
        # 保存报告
        report_content = "\n".join(report_lines)
        report_path = os.path.join(self.output_dir, '特征工程报告.txt')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"特征工程报告已保存到: {report_path}")
        return report_path
    
    def generate_model_evaluation_report(self, y_true: np.ndarray = None, 
                                        y_pred: np.ndarray = None,
                                        metrics: Dict = None,
                                        result_df: pd.DataFrame = None) -> str:
        """
        生成模型评估报告
        
        Args:
            y_true: 真实标签
            y_pred: 预测标签
            metrics: 评估指标字典
            result_df: 结果数据框
            
        Returns:
            报告文件路径
        """
        report_lines = []
        report_lines.append("="*80)
        report_lines.append("模型评估报告")
        report_lines.append("="*80)
        report_lines.append(f"\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # 1. 模型概述
        report_lines.append("1. 模型概述")
        report_lines.append("-"*80)
        report_lines.append("模型类型: DBSCAN聚类 + 规则判定")
        report_lines.append("算法特点:")
        report_lines.append("  - 基于密度的聚类算法，适合发现家庭圈")
        report_lines.append("  - 结合多维度特征进行用户聚类")
        report_lines.append("  - 使用规则判定进行关系验证\n")
        
        # 2. 关系判定规则
        report_lines.append("2. 关系判定规则")
        report_lines.append("-"*80)
        rules = {
            '地址关联性': {'阈值': 0.8, '权重': 0.3, '说明': '地址相似度达到80%以上'},
            '缴费账户关联性': {'阈值': 1.0, '权重': 0.4, '说明': '完全相同的缴费账户'},
            '终端共享特征': {'阈值': 1, '权重': 0.2, '说明': '至少共享1个设备'},
            '通信行为特征': {'阈值': 0.5, '权重': 0.1, '说明': '通信频率相似度达到50%以上'}
        }
        
        for rule_name, rule_info in rules.items():
            report_lines.append(f"\n{rule_name}:")
            report_lines.append(f"  阈值: {rule_info['阈值']}")
            report_lines.append(f"  权重: {rule_info['权重']}")
            report_lines.append(f"  说明: {rule_info['说明']}")
        
        report_lines.append(f"\n综合判定阈值: 0.5（加权得分达到50%以上判定为家庭成员）\n")
        
        # 3. 评估指标
        if metrics:
            report_lines.append("3. 模型评估指标")
            report_lines.append("-"*80)
            report_lines.append(f"准确率 (Accuracy): {metrics.get('accuracy', 0):.4f}")
            report_lines.append(f"精确率 (Precision): {metrics.get('precision', 0):.4f}")
            report_lines.append(f"召回率 (Recall): {metrics.get('recall', 0):.4f}")
            report_lines.append(f"F1值 (F1-Score): {metrics.get('f1_score', 0):.4f}")
            
            # 判断是否达到目标
            accuracy = metrics.get('accuracy', 0)
            if accuracy >= 0.85:
                report_lines.append(f"\n✓ 核心关系识别准确率 {accuracy:.2%} ≥ 85%，达到赛题要求")
            else:
                report_lines.append(f"\n⚠ 核心关系识别准确率 {accuracy:.2%} < 85%，需要进一步优化")
        
        # 4. 结果统计
        if result_df is not None:
            report_lines.append("\n\n4. 识别结果统计")
            report_lines.append("-"*80)
            total_users = len(result_df)
            total_circles = result_df['family_circle_id'].nunique()
            key_persons = result_df['is_key_person'].sum()
            
            report_lines.append(f"总用户数: {total_users}")
            report_lines.append(f"识别家庭圈数量: {total_circles}")
            report_lines.append(f"关键人数量: {key_persons}")
            report_lines.append(f"平均每个家庭圈用户数: {total_users/total_circles:.2f}" if total_circles > 0 else "平均每个家庭圈用户数: N/A")
            
            # 家庭圈大小分布
            circle_sizes = result_df.groupby('family_circle_id').size()
            report_lines.append(f"\n家庭圈大小分布:")
            report_lines.append(f"  最小: {circle_sizes.min()} 人")
            report_lines.append(f"  最大: {circle_sizes.max()} 人")
            report_lines.append(f"  平均: {circle_sizes.mean():.2f} 人")
            report_lines.append(f"  中位数: {circle_sizes.median():.2f} 人")
        
        # 5. 模型优势与局限性
        report_lines.append("\n\n5. 模型优势与局限性")
        report_lines.append("-"*80)
        report_lines.append("优势:")
        report_lines.append("  - 多维度特征融合，综合考虑地址、账户、设备、通信等信息")
        report_lines.append("  - 无监督学习方法，无需大量标注数据")
        report_lines.append("  - 规则与模型结合，可解释性强")
        report_lines.append("  - 能够自动识别家庭圈边界和关键人")
        report_lines.append("\n局限性:")
        report_lines.append("  - 对数据质量要求较高")
        report_lines.append("  - 参数需要根据实际数据调整")
        report_lines.append("  - 对于稀疏数据可能识别效果有限")
        
        # 保存报告
        report_content = "\n".join(report_lines)
        report_path = os.path.join(self.output_dir, '模型评估报告.txt')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"模型评估报告已保存到: {report_path}")
        return report_path
    
    def generate_result_explanation(self, result_df: pd.DataFrame) -> str:
        """
        生成结果说明文档
        
        Args:
            result_df: 结果数据框
            
        Returns:
            报告文件路径
        """
        report_lines = []
        report_lines.append("="*80)
        report_lines.append("家庭圈用户群体划分结果说明")
        report_lines.append("="*80)
        report_lines.append(f"\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # 1. 结果概述
        report_lines.append("1. 结果概述")
        report_lines.append("-"*80)
        total_users = len(result_df)
        total_circles = result_df['family_circle_id'].nunique()
        key_persons = result_df['is_key_person'].sum()
        
        report_lines.append(f"本次识别共处理 {total_users} 个用户，识别出 {total_circles} 个家庭圈，")
        report_lines.append(f"其中包含 {key_persons} 个家庭关键人。\n")
        
        # 2. 家庭圈划分标准
        report_lines.append("2. 家庭圈划分标准")
        report_lines.append("-"*80)
        report_lines.append("家庭圈的划分基于以下标准:")
        report_lines.append("  (1) 地址关联性: 用户具有相同或相似的地址信息")
        report_lines.append("  (2) 缴费账户关联性: 用户共享相同的缴费账户")
        report_lines.append("  (3) 终端共享特征: 用户共享设备或终端")
        report_lines.append("  (4) 通信行为特征: 用户之间存在频繁的通信联系")
        report_lines.append("\n当用户在上述多个维度存在关联时，判定为同一家庭圈成员。\n")
        
        # 3. 关键人识别标准
        report_lines.append("3. 关键人识别标准")
        report_lines.append("-"*80)
        report_lines.append("家庭关键人的识别基于以下特征:")
        report_lines.append("  (1) 账户主特征: 拥有更多账户或账户共享关系")
        report_lines.append("  (2) 缴费特征: 作为主要缴费人")
        report_lines.append("  (3) 通信中心度: 通信频率高，联系人多")
        report_lines.append("  (4) 地址稳定性: 地址信息稳定")
        report_lines.append("\n每个家庭圈中得分最高的用户被识别为关键人。\n")
        
        # 4. 结果文件说明
        report_lines.append("4. 结果文件说明")
        report_lines.append("-"*80)
        report_lines.append("结果文件包含以下字段:")
        report_lines.append("  - 用户ID: 用户的唯一标识")
        report_lines.append("  - 家庭圈ID: 用户所属的家庭圈编号")
        report_lines.append("  - 是否关键人: 1表示是关键人，0表示不是关键人")
        report_lines.append("\n同一家庭圈ID的用户属于同一个家庭圈。\n")
        
        # 5. 家庭圈示例
        report_lines.append("5. 家庭圈示例")
        report_lines.append("-"*80)
        # 选择几个较大的家庭圈作为示例
        circle_sizes = result_df.groupby('family_circle_id').size().sort_values(ascending=False)
        top_circles = circle_sizes.head(5)
        
        user_id_col = '用户ID' if '用户ID' in result_df.columns else result_df.columns[0]
        
        for circle_id, size in top_circles.items():
            circle_members = result_df[result_df['family_circle_id'] == circle_id]
            key_person = circle_members[circle_members['is_key_person'] == 1]
            key_person_id = key_person[user_id_col].iloc[0] if len(key_person) > 0 else None
            
            report_lines.append(f"\n家庭圈 #{circle_id} (共 {size} 人):")
            members = circle_members[user_id_col].tolist()
            report_lines.append(f"  成员: {', '.join(map(str, members))}")
            if key_person_id:
                report_lines.append(f"  关键人: {key_person_id} 👑")
        
        # 6. 使用建议
        report_lines.append("\n\n6. 使用建议")
        report_lines.append("-"*80)
        report_lines.append("  (1) 结果可用于家庭维度的精细化运营")
        report_lines.append("  (2) 关键人信息可用于家庭业务推广")
        report_lines.append("  (3) 可根据业务需求进一步优化模型参数")
        report_lines.append("  (4) 建议结合业务规则对结果进行验证和调整")
        
        # 保存报告
        report_content = "\n".join(report_lines)
        report_path = os.path.join(self.output_dir, '结果说明文档.txt')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"结果说明文档已保存到: {report_path}")
        return report_path
    
    def generate_all_reports(self, feature_df: pd.DataFrame, original_df: pd.DataFrame,
                           result_df: pd.DataFrame, metrics: Dict = None):
        """
        生成所有报告
        
        Args:
            feature_df: 特征数据框
            original_df: 原始数据框
            result_df: 结果数据框
            metrics: 评估指标
        """
        print("\n开始生成报告...")
        
        # 生成特征工程报告
        self.generate_feature_engineering_report(feature_df, original_df)
        
        # 生成模型评估报告
        self.generate_model_evaluation_report(metrics=metrics, result_df=result_df)
        
        # 生成结果说明文档
        self.generate_result_explanation(result_df)
        
        print("\n所有报告生成完成！")

