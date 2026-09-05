from pathlib import Path
from typing import Any, Dict, List

from promptforge.models import PromptOutput, PromptSection, TemplateSections
from promptforge.adapters.base import BaseAdapter


class MarkdownAdapter(BaseAdapter):
    """
    通用的 Markdown 格式适配器。
    将内容输出为结构化的 Markdown 文件。
    """
    platform_name = 'markdown'
    max_tokens = None
    supports_system_prompt = True
    supports_tool_definitions = True
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
        导出为带有明确标题的 Markdown 内容。
        """
        content = ""
        for section in prompt.sections:
            if section.role == "system":
                content += f"## System Prompt\n\n{section.content}\n\n"
            elif section.role == "user":
                content += f"## User Prompt\n\n{section.content}\n\n"
            elif section.role == "assistant":
                content += f"## Assistant\n\n{section.content}\n\n"
            elif section.role == "tool":
                content += f"## Tool\n\n{section.content}\n\n"
            else:
                content += f"## {section.role.capitalize()}\n\n{section.content}\n\n"
                
        if prompt.tools:
            content += "## Tools\n\n"
            for tool in prompt.tools:
                content += f"### {tool.name}\n\n"
                content += f"**Description**: {tool.description}\n\n"
                if tool.parameters:
                    content += "**Parameters**:\n"
                    for param in tool.parameters:
                        required_mark = " (Required)" if param.required else ""
                        content += f"- `{param.name}` ({param.type}){required_mark}: {param.description}\n"
                content += "\n"
                
        return content.strip() + "\n"

    def export_to_file(self, prompt: PromptOutput, output_path: Path) -> None:
        """
        导出到 Markdown 文件。
        """
        output_path.write_text(self.export(prompt), encoding='utf-8')
