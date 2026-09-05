"""
生成的提示词与相关数据模型定义。
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class PromptRole(str, Enum):
    """提示词角色枚举"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class PromptSection(BaseModel):
    """提示词内容块模型"""
    role: PromptRole = Field(description="消息的角色")
    content: str = Field(description="消息的内容")


class ToolParameter(BaseModel):
    """工具参数定义模型"""
    name: str = Field(description="参数名称")
    type: str = Field(description="参数类型，如 'string', 'integer'")
    description: str = Field(description="参数的用途描述")
    required: bool = Field(default=False, description="是否必填参数")
    enum: Optional[List[str]] = Field(default=None, description="参数的枚举值选项")


class ToolDefinition(BaseModel):
    """工具（函数）定义模型"""
    name: str = Field(description="工具的名称")
    description: str = Field(description="工具的功能描述")
    parameters: List[ToolParameter] = Field(default_factory=list, description="工具的参数列表")


class PromptOutput(BaseModel):
    """生成的最终提示词输出模型"""
    template_name: str = Field(description="使用的模板名称")
    category: str = Field(description="模板分类")
    platform: str = Field(description="目标平台名称")
    sections: List[PromptSection] = Field(description="格式化后的各角色提示词列表")
    tool_definitions: Optional[List[ToolDefinition]] = Field(default=None, description="使用的工具定义列表")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="相关的其他元数据")
    token_estimate: int = Field(description="预估使用的Token数量")
    raw_text: str = Field(description="完整拼合的提示词纯文本")

    @property
    def tools(self) -> Optional[List[ToolDefinition]]:
        """获取工具定义列表（兼容别名）"""
        return self.tool_definitions


class ValidationResult(BaseModel):
    """提示词校验结果模型"""
    is_valid: bool = Field(description="提示词是否通过验证")
    errors: List[str] = Field(default_factory=list, description="校验失败的错误信息列表")
    warnings: List[str] = Field(default_factory=list, description="需要注意的警告信息列表")
    suggestions: List[str] = Field(default_factory=list, description="改进提示词的建议列表")
    token_count: int = Field(default=0, description="总计消耗的Token数量")
    platform_compatibility: Dict[str, bool] = Field(default_factory=dict, description="各个平台的支持状态")
