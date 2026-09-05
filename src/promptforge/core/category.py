"""
类别管理器模块，管理提示词模板的分类和发现。
"""
from dataclasses import dataclass
from typing import Dict, List, Optional
from pathlib import Path
import yaml
from promptforge.models.template import TemplateMeta

@dataclass
class CategoryInfo:
    """类别信息数据类"""
    name: str
    display_name: str
    description: str
    icon: str
    subcategories: List[str]
    template_count: int = 0

CATEGORIES = {
    "coding": CategoryInfo(
        name="coding",
        display_name="编程开发",
        description="代码生成、审查、重构、SQL优化与DevOps流水线",
        icon="💻",
        subcategories=["review", "bugfix", "refactor", "sql", "devops", "git", "algorithm"]
    ),
    "analysis": CategoryInfo(
        name="analysis",
        display_name="数据与架构分析",
        description="数据洞察、根因排查 (RCA)、性能剖析与安全审计",
        icon="📊",
        subcategories=["data", "rca", "performance", "security", "dependency"]
    ),
    "writing": CategoryInfo(
        name="writing",
        display_name="工程写作与设计",
        description="PRD需求、技术方案 (RFC)、架构决策 (ADR) 与接口文档",
        icon="📝",
        subcategories=["prd", "rfc", "adr", "api_doc", "docs", "readme"]
    ),
    "tool_use": CategoryInfo(
        name="tool_use",
        display_name="工具调用与智能体",
        description="MCP 服务设计、多智能体协同、浏览器自动化与接口集成",
        icon="🛠️",
        subcategories=["mcp", "subagent", "browser", "api", "function_call"]
    ),
    "conversation": CategoryInfo(
        name="conversation",
        display_name="交互式推理与流程",
        description="Plan规划先导模式、苏格拉底小黄鸭调试、技术方案辩论与模拟面试",
        icon="💬",
        subcategories=["plan_mode", "rubber_duck", "debate", "interview", "multi_turn"]
    ),
    "system": CategoryInfo(
        name="system",
        display_name="系统守则与规范",
        description="零信任防护守则、严格输出校验器、Agent角色设定与安全边界",
        icon="⚙️",
        subcategories=["guardrail", "json_enforcer", "persona", "safety"]
    ),
    "productivity": CategoryInfo(
        name="productivity",
        display_name="日常与办公",
        description="会议纪要提炼、职场周报总结、自媒体文案、大白话科普与出行规划",
        icon="✨",
        subcategories=["meeting", "weekly_report", "social_media", "explainer", "travel", "email"]
    ),
    "academic": CategoryInfo(
        name="academic",
        display_name="学术与科研",
        description="文献速读综述、开题报告立项、学术论文润色、实验消融设计与答辩模拟",
        icon="🎓",
        subcategories=["literature", "proposal", "paper_polish", "experiment", "coursework", "defense"]
    ),
    "presentation": CategoryInfo(
        name="presentation",
        display_name="演示与汇报",
        description="幻灯片大纲架构、逐页内容排版、Marp代码生成、商业路演Deck、学术答辩PPT与演讲逐字稿",
        icon="📽️",
        subcategories=["outline", "slide_layout", "marp", "pitch_deck", "academic_slides", "rehearsal"]
    )
}

class CategoryManager:
    """管理模板类别和文件扫描。"""
    
    def __init__(self, base_dir: Optional[Path] = None):
        """
        初始化类别管理器
        """
        if base_dir:
            if (base_dir / "templates").is_dir():
                self.templates_dir = base_dir / "templates"
            else:
                self.templates_dir = base_dir
        else:
            candidates = [
                Path(__file__).resolve().parent.parent.parent.parent / "templates",
                Path(__file__).resolve().parent.parent / "templates",
                Path.cwd() / "templates",
            ]
            self.templates_dir = next((p for p in candidates if p.is_dir()), candidates[0])

    def list_categories(self) -> List[CategoryInfo]:
        """
        列出所有可用的类别。
        
        Returns:
            类别信息列表
        """
        for category_name, category_info in CATEGORIES.items():
            category_info.template_count = len(self.list_templates(category_name))
        return list(CATEGORIES.values())

    def get_category(self, name: str) -> Optional[CategoryInfo]:
        """
        获取指定类别的信息。
        
        Args:
            name: 类别名称
            
        Returns:
            类别信息，如果不存在则返回 None
        """
        info = CATEGORIES.get(name)
        if info:
            info.template_count = len(self.list_templates(name))
        return info

    def list_templates(self, category: Optional[str] = None) -> List[TemplateMeta]:
        """
        扫描模板目录并返回模板元数据列表。
        
        Args:
            category: 可选，按类别过滤
            
        Returns:
            模板元数据列表
        """
        templates = []
        if not self.templates_dir.exists():
            return templates
            
        search_dirs = [self.templates_dir / category] if category else [d for d in self.templates_dir.iterdir() if d.is_dir()]
        
        for directory in search_dirs:
            if not directory.exists() or not directory.is_dir():
                continue
                
            for file_path in directory.glob("*.yaml"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = yaml.safe_load(f)
                        if 'meta' in data:
                            meta_dict = dict(data['meta'])
                            presets_data = data.get('presets', [])
                            if isinstance(presets_data, list):
                                meta_dict['presets_count'] = len(presets_data)
                                meta_dict['preset_titles'] = [
                                    p.get('title', '') for p in presets_data if isinstance(p, dict) and p.get('title')
                                ]
                            meta = TemplateMeta(**meta_dict)
                            templates.append(meta)
                except Exception:
                    pass
                    
        return templates

    def get_template_path(self, category: str, template_name: str) -> Path:
        """
        获取模板文件的路径。
        
        Args:
            category: 类别名称
            template_name: 模板名称
            
        Returns:
            模板文件的完整路径
        """
        return self.templates_dir / category / f"{template_name}.yaml"
