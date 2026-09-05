"""
数据模型包的初始化文件。
"""

from .template import (
    VariableType,
    VariableDefinition,
    SystemSection,
    TemplateSections,
    TemplateMeta,
    Template,
)
from .prompt import (
    PromptRole,
    PromptSection,
    ToolParameter,
    ToolDefinition,
    PromptOutput,
    ValidationResult,
)

__all__ = [
    "VariableType",
    "VariableDefinition",
    "SystemSection",
    "TemplateSections",
    "TemplateMeta",
    "Template",
    "PromptRole",
    "PromptSection",
    "ToolParameter",
    "ToolDefinition",
    "PromptOutput",
    "ValidationResult",
]
