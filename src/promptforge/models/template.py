"""
提示词模板数据模型定义。
"""

from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import yaml
from pydantic import BaseModel, Field, field_validator


class VariableType(str, Enum):
    """变量类型枚举"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    LIST = "list"
    ENUM = "enum"


class VariableDefinition(BaseModel):
    """模板变量定义模型"""
    type: VariableType = Field(description="变量的类型")
    required: bool = Field(default=True, description="是否为必填变量")
    default: Optional[Any] = Field(default=None, description="变量的默认值")
    description: str = Field(description="变量的描述，用于帮助信息")
    examples: Optional[List[Any]] = Field(default=None, description="变量的示例值列表")
    options: Optional[List[str]] = Field(default=None, description="枚举变量的可用选项，当type为enum时必填")

    @field_validator("options")
    @classmethod
    def validate_options(cls, v: Optional[List[str]], info: Any) -> Optional[List[str]]:
        if info.data.get("type") == VariableType.ENUM and not v:
            raise ValueError("当类型为 'enum' 时，'options' 字段必填。")
        return v


class TemplateMeta(BaseModel):
    """模板元数据模型"""
    name: str = Field(description="模板名称，需唯一")
    display_name: str = Field(description="用于显示的模板名称")
    category: str = Field(description="模板所属分类")
    description: str = Field(description="模板的详细描述")
    tags: List[str] = Field(default_factory=list, description="模板标签列表")
    version: str = Field(description="模板版本号，如 '1.0.0'")
    platforms: List[str] = Field(description="支持的平台列表，如 ['openai', 'anthropic']")
    author: Optional[str] = Field(default=None, description="模板作者")
    presets_count: int = Field(default=0, description="预设场景数量")
    preset_titles: List[str] = Field(default_factory=list, description="预设场景标题列表")


class SystemSection(BaseModel):
    """系统提示词部分模型"""
    role: str = Field(description="角色设定，定义Agent的角色")
    instructions: str = Field(description="指令部分，定义核心任务和要求")
    output_format: Optional[str] = Field(default=None, description="输出格式要求")
    constraints: Optional[Union[str, List[str]]] = Field(default=None, description="各种约束条件和限制")
    examples: Optional[List[Dict[str, str]]] = Field(default=None, description="对话示例，few-shot examples")


class TemplateSections(BaseModel):
    """模板内容结构模型"""
    system: SystemSection = Field(description="系统提示词部分定义")
    user: str = Field(description="用户提示词模板字符串")


class PresetScenario(BaseModel):
    """预设场景模型，供用户一键选用常见需求与变量组合"""
    id: str = Field(description="预设唯一标识，如'concurrency_audit'")
    title: str = Field(description="预设标题，如'电商高并发库存扣减'")
    description: Optional[str] = Field(default=None, description="预设场景简述")
    variables: Dict[str, Any] = Field(default_factory=dict, description="预设变量字典")


class Template(BaseModel):
    """提示词模板模型"""
    meta: TemplateMeta = Field(description="模板的元数据")
    variables: Dict[str, VariableDefinition] = Field(default_factory=dict, description="模板所需的变量定义")
    presets: List[PresetScenario] = Field(default_factory=list, description="常用预设需求与场景列表")
    sections: TemplateSections = Field(description="模板的内容分块")
    sections_en: Optional[TemplateSections] = Field(default=None, description="英文版本模板内容分块")

    @classmethod
    def from_yaml(cls, path: Path) -> "Template":
        """从YAML文件加载并实例化模板对象。"""
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return cls.model_validate(data)

    def to_yaml(self) -> str:
        """将模板对象序列化为YAML格式字符串。"""
        data = self.model_dump(exclude_unset=True)
        return yaml.dump(data, allow_unicode=True, sort_keys=False)
