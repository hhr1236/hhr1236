#!/usr/bin/env python3
"""
Example: Using LLM responses to guide nautical chart modeling
示例：使用LLM回答指导海图建模

This example demonstrates how to:
1. Query the system about a specific water region
2. Extract nautical chart features from the response
3. Create a structured model for chart features
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.navigation_system import NavigationKnowledgeSystem


class NauticalChartModeler:
    """
    Extract nautical chart features from LLM responses.
    从LLM回答中提取海图要素。
    """
    
    # Define common nautical chart feature types
    FEATURE_TYPES = {
        "航道": "channel",
        "锚地": "anchorage",
        "禁航区": "prohibited_area",
        "警戒区": "caution_area",
        "浅水区": "shallow_water",
        "导航标志": "navigation_mark",
        "灯塔": "lighthouse",
        "分隔带": "separation_zone",
        "交通管制": "traffic_control",
        "潮汐站": "tide_station"
    }
    
    def __init__(self):
        """Initialize the modeler."""
        self.features = []
    
    def extract_features(self, text: str, region: str) -> list:
        """
        Extract nautical chart features from text.
        从文本中提取海图要素。
        
        Args:
            text: Input text (LLM response)
            region: Water region name
            
        Returns:
            List of extracted features
        """
        features = []
        
        for chinese_name, english_name in self.FEATURE_TYPES.items():
            if chinese_name in text:
                # Extract context around the feature mention
                sentences = text.split('。')
                relevant_sentences = [s for s in sentences if chinese_name in s]
                
                if relevant_sentences:
                    feature = {
                        "type": english_name,
                        "chinese_name": chinese_name,
                        "region": region,
                        "description": relevant_sentences[0][:200],
                        "priority": "high" if any(word in text for word in ["必须", "严格", "禁止", "强制"]) else "normal"
                    }
                    features.append(feature)
        
        return features
    
    def create_chart_model(self, region: str, features: list) -> dict:
        """
        Create a structured nautical chart model.
        创建结构化的海图模型。
        
        Args:
            region: Water region name
            features: List of features
            
        Returns:
            Nautical chart model dictionary
        """
        model = {
            "region": region,
            "feature_count": len(features),
            "features_by_type": {},
            "high_priority_features": [],
            "features": features
        }
        
        # Group features by type
        for feature in features:
            feature_type = feature["type"]
            if feature_type not in model["features_by_type"]:
                model["features_by_type"][feature_type] = []
            model["features_by_type"][feature_type].append(feature)
            
            # Track high priority features
            if feature.get("priority") == "high":
                model["high_priority_features"].append(feature)
        
        return model
    
    def print_model(self, model: dict):
        """
        Print the nautical chart model in a readable format.
        以可读格式打印海图模型。
        
        Args:
            model: Nautical chart model
        """
        print("\n" + "=" * 70)
        print(f"海图建模结果 - {model['region']}")
        print(f"Nautical Chart Model - {model['region']}")
        print("=" * 70)
        
        print(f"\n总要素数量: {model['feature_count']}")
        print(f"高优先级要素: {len(model['high_priority_features'])}")
        
        print("\n按类型分类 (Features by Type):")
        print("-" * 70)
        
        for feature_type, features in model["features_by_type"].items():
            chinese_name = features[0]["chinese_name"]
            print(f"\n{chinese_name} ({feature_type}): {len(features)} 个")
            
            for i, feature in enumerate(features, 1):
                priority_mark = "⚠️" if feature.get("priority") == "high" else "•"
                print(f"  {priority_mark} {feature['description'][:100]}...")
        
        if model["high_priority_features"]:
            print("\n" + "-" * 70)
            print("高优先级要素 (High Priority Features):")
            print("-" * 70)
            for feature in model["high_priority_features"]:
                print(f"  ⚠️ [{feature['chinese_name']}] {feature['description'][:150]}...")
        
        print("\n" + "=" * 70)


def main():
    """Main demonstration function."""
    
    print("=" * 70)
    print("海图建模示例 (Nautical Chart Modeling Example)")
    print("=" * 70)
    
    # Initialize system
    print("\n[步骤 1] 初始化系统...")
    system = NavigationKnowledgeSystem(data_dir="../data")
    
    try:
        system.load_knowledge_base()
    except Exception as e:
        print(f"错误: 无法加载知识库。请先运行: python main.py --ingest data/navigation_rules")
        return
    
    # Initialize modeler
    modeler = NauticalChartModeler()
    
    # Example queries for different regions
    queries = [
        ("渤海湾", "渤海湾建立海图模型需要标注哪些要素和注意事项？"),
        ("长江口", "长江口海图应该重点标注哪些航行要素？"),
        ("珠江口", "珠江口海图建模需要关注哪些区域和要素？")
    ]
    
    print("\n[步骤 2] 查询各水域并提取海图要素...\n")
    
    all_models = []
    
    for region, query in queries:
        print(f"\n{'='*70}")
        print(f"查询水域: {region}")
        print(f"Query Region: {region}")
        print(f"{'='*70}")
        
        # Query the system
        result = system.query(query, top_k=2)
        
        print(f"\n查询问题: {query}")
        print(f"\n获取到 {len(result['source_documents'])} 个相关文档")
        
        # Extract features from answer
        features = modeler.extract_features(result['answer'], region)
        print(f"提取到 {len(features)} 个海图要素")
        
        # Create chart model
        chart_model = modeler.create_chart_model(region, features)
        all_models.append(chart_model)
        
        # Print model
        modeler.print_model(chart_model)
        
        # Show part of the answer
        print("\nLLM回答摘要:")
        print("-" * 70)
        answer_preview = result['answer'][:400] + "..." if len(result['answer']) > 400 else result['answer']
        print(answer_preview)
        
        if region != queries[-1][0]:
            input("\n按Enter继续... (Press Enter to continue...)")
    
    # Summary
    print("\n" + "=" * 70)
    print("总结 (Summary)")
    print("=" * 70)
    
    total_features = sum(model['feature_count'] for model in all_models)
    total_high_priority = sum(len(model['high_priority_features']) for model in all_models)
    
    print(f"\n处理了 {len(all_models)} 个水域")
    print(f"提取了 {total_features} 个海图要素")
    print(f"识别了 {total_high_priority} 个高优先级要素")
    
    print("\n各水域要素统计:")
    for model in all_models:
        print(f"  • {model['region']}: {model['feature_count']} 个要素")
        types = ", ".join(model['features_by_type'].keys())
        print(f"    类型: {types}")
    
    print("\n" + "=" * 70)
    print("建模完成！Modeling Complete!")
    print("=" * 70)
    
    print("\n💡 下一步 (Next Steps):")
    print("  1. 将这些要素导入GIS系统")
    print("  2. 在电子海图上标注关键位置")
    print("  3. 关注高优先级要素")
    print("  4. 根据实际航行需求调整模型")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
