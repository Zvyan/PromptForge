from pathlib import Path
from typing import Any, Dict, List

from promptforge.models import PromptOutput, PromptSection, TemplateSections
from promptforge.adapters.base import BaseAdapter


class CursorAdapter(BaseAdapter):
    """
    Cursor 编辑器平台适配器。
    将所有提示词片段合并为单个 Markdown 文档。
    """
    platform_name = 'cursor'
    max_tokens = 32000
    supports_system_prompt = True
    supports_tool_definitions = False
    output_format = 'markdown'

    def format_prompt(self, sections: TemplateSections, variables: Dict[str, Any]) -> List[PromptSection]:
        """
        格式化提示词片段。
        """
        result = []
        if sections.system:
            result.append(PromptSection(role="system", content=sections.system))
        for msg in sections.messages:
            result.append(PromptSection(role=msg.role, content=msg.content))
        return result

    def export(self, prompt: PromptOutput) -> str:
        """
        导出为适用于 Cursor 的 Markdown 文本。
        """
        content = ""
        for section in prompt.sections:
            content += f"{section.content}\n\n"
        return content.strip() + "\n"

    def export_to_file(self, prompt: PromptOutput, output_path: Path) -> None:
        """
        导出到 .cursorrules 文件。
        """
        if output_path.is_dir():
            output_path = output_path / '.cursorrules'
        output_path.write_text(self.export(prompt), encoding='utf-8')


class WindsurfAdapter(CursorAdapter):
    """
    Windsurf 编辑器平台适配器。
    类似于 Cursor，用于生成 .windsurfrules 文件。
    """
    platform_name = 'windsurf'
    
    def export_to_file(self, prompt: PromptOutput, output_path: Path) -> None:
        """
        导出到 .windsurfrules 文件。
        """
        if output_path.is_dir():
            output_path = output_path / '.windsurfrules'
        output_path.write_text(self.export(prompt), encoding='utf-8')
