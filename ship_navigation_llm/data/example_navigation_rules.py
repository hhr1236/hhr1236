"""
Example navigation rules for demonstration purposes.
示例航行规则 - 用于演示。
"""

# Example navigation rules for different water regions
EXAMPLE_NAVIGATION_RULES = {
    "渤海湾": """
渤海湾通航规则

一、基本规定
1. 所有进出渤海湾的船舶必须遵守《中华人民共和国海上交通安全法》
2. 船舶应保持正规的瞭望，使用安全的航速
3. 能见度不良时应采取谨慎措施

二、航行注意事项
1. 主航道宽度：主要航道宽度不少于200米，水深10-15米
2. 分道通航制：实行分道通航，顺航道右侧航行
3. 禁航区域：军事管制区、养殖区禁止通航
4. 锚地：指定锚地包括老铁山锚地、大连锚地等

三、特殊要求
1. 危险品船舶需提前申报
2. 大型船舶需申请引航
3. 夜间航行需开启导航灯
4. 恶劣天气时听从海事部门指挥

四、海图要素重点
- 航道边界标识
- 锚地范围
- 禁航区标注
- 浅水区警示
- 导航标志位置
""",
    
    "长江口": """
长江口通航规则

一、水域特点
1. 长江口为咸淡水交汇处，潮汐影响显著
2. 水道复杂，分为南北槽
3. 泥沙沉积快，航道常需维护

二、通航规定
1. 严格遵守VTS（船舶交通管理系统）指挥
2. 必须使用VHF频道保持通讯联系
3. 超过一万吨船舶需强制引航
4. 禁止在航道内抛锚

三、航行注意事项
1. 南北槽航道：北槽水深较深，适合大型船舶
2. 潮汐影响：涨潮时流速可达3-4节，需计算潮时
3. 能见度：雾天频繁，需加强雷达瞭望
4. 避让规则：上行船让下行船，支流让干流

四、关键区域
- 长江口深水航道
- 浏河口警戒区
- 横沙东滩（浅水区）
- 吴淞口交汇区

五、海图建模要素
- 航道中心线及边界
- 潮位观测站
- 导助航设施
- 危险沉船标记
- 锚地和禁锚区
""",
    
    "珠江口": """
珠江口通航规则

一、概况
珠江口是华南地区最重要的出海口，船舶流量大，水域情况复杂。

二、通航要求
1. 所有船舶需遵守《珠江口水域船舶定线制》
2. 进港船舶需提前24小时报告
3. 危险品船舶严格管制
4. 夜间进港需有引航员

三、主要航道
1. 虎门水道：主航道，水深8-15米
2. 蕉门水道：次要航道，适合中小型船舶
3. 洪奇沥水道：内河航道

四、特别注意
1. 台风季节（5-11月）需特别关注天气
2. 渔船作业密集区域需谨慎航行
3. 客货滚装码头区域限速
4. 避免在锚地外围随意抛锚

五、禁航与限制
- 军事禁区：伶仃岛周边
- 保护区：中华白海豚保护区（限速）
- 施工区域：需提前公告

六、海图标注要点
- 主要航道及支航道
- 锚地区域
- 禁航区和限制区
- 警戒区和交通分隔带
- 助航标志和灯塔
- 浅滩和暗礁
"""
}


def create_example_text_files(output_dir: str = "data/navigation_rules"):
    """
    Create example text files for navigation rules.
    创建导航规则的示例文本文件。
    
    Args:
        output_dir: Output directory for text files
    """
    import os
    from pathlib import Path
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    for region, rules in EXAMPLE_NAVIGATION_RULES.items():
        file_path = output_path / f"{region}.txt"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(rules)
        print(f"Created: {file_path}")
    
    print(f"\nTotal {len(EXAMPLE_NAVIGATION_RULES)} example files created in {output_dir}")


if __name__ == "__main__":
    create_example_text_files()
