from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional

from promptforge.models import PromptOutput, PromptSection, TemplateSections


class BaseAdapter(ABC):
    """
    提示词适配器的基础抽象类。
    定义了所有平台适配器必须实现的接口。
    """
    platform_name: str
    max_tokens: Optional[int]
    supports_system_prompt: bool
    supports_tool_definitions: bool
    output_format: str  # 'json', 'markdown', 'yaml'
    
    @abstractmethod
    def format_prompt(self, sections: TemplateSections, variables: Dict[str, Any]) -> List[PromptSection]:
        """
        根据提供的模板片段和变量，格式化为特定平台的提示词片段列表。

        Args:
            sections (TemplateSections): 提示词模板片段。
            variables (Dict[str, Any]): 渲染变量字典。

        Returns:
            List[PromptSection]: 格式化后的提示词片段列表。
        """
        pass
        
    @abstractmethod
    def export(self, prompt: PromptOutput) -> str:
        """
        将提示词输出对象导出为特定格式的字符串。

        Args:
            prompt (PromptOutput): 提示词输出对象。

        Returns:
            str: 导出格式的字符串。
        """
        pass
        
    @abstractmethod
    def export_to_file(self, prompt: PromptOutput, output_path: Path) -> None:
        """
        将提示词输出对象导出并保存到指定文件。

        Args:
            prompt (PromptOutput): 提示词输出对象。
            output_path (Path): 输出文件路径。
        """
        pass
        
    def get_platform_info(self) -> Dict[str, Any]:
        """
        获取当前平台适配器的基本信息。

        Returns:
            Dict[str, Any]: 包含平台名称、最大token数、功能支持等信息的字典。
        """
        return {
            "platform_name": self.platform_name,
            "max_tokens": self.max_tokens,
            "supports_system_prompt": self.supports_system_prompt,
            "supports_tool_definitions": self.supports_tool_definitions,
            "output_format": self.output_format,
        }
