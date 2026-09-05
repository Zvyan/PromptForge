import json
from pathlib import Path
from typing import Any, Dict, List

from promptforge.models import PromptOutput, PromptSection, TemplateSections
from promptforge.adapters.base import BaseAdapter


class OpenAIAdapter(BaseAdapter):
    """
    OpenAI 平台适配器。
    支持系统提示词、工具定义，输出为 JSON 格式。
    """
    platform_name = 'openai'
    max_tokens = 128000
    supports_system_prompt = True
    supports_tool_definitions = True
    output_format = 'json'

    def format_prompt(self, sections: TemplateSections, variables: Dict[str, Any]) -> List[PromptSection]:
        """
        格式化为 OpenAI 提示词片段。
        """
        # Placeholder implementation for formatting sections with variables
        result = []
        if sections.system:
            result.append(PromptSection(role="system", content=sections.system))
        for msg in sections.messages:
            result.append(PromptSection(role=msg.role, content=msg.content))
        return result

    def export(self, prompt: PromptOutput) -> str:
        """
        导出为 OpenAI API 兼容的 JSON 格式字符串。
        """
        output: Dict[str, Any] = {"messages": []}
        
        for section in prompt.sections:
            output["messages"].append({
                "role": section.role,
                "content": section.content
            })
            
        if prompt.tools:
            output["tools"] = []
            for tool in prompt.tools:
                tool_dict = {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": {
                            "type": "object",
                            "properties": {
                                p.name: {"type": p.type, "description": p.description}
                                for p in tool.parameters
                            },
                            "required": [p.name for p in tool.parameters if p.required]
                        }
                    }
                }
                output["tools"].append(tool_dict)
                
        return json.dumps(output, ensure_ascii=False, indent=2)

    def export_to_file(self, prompt: PromptOutput, output_path: Path) -> None:
        """
        将 OpenAI 格式的 JSON 导出到文件。
        """
        output_path.write_text(self.export(prompt), encoding='utf-8')
        
    def to_codex_agents_md(self, prompt: PromptOutput) -> str:
        """
        生成 AGENTS.md 格式的内容。
        """
        content = "# 智能体配置 (AGENTS.md)\n\n"
        for section in prompt.sections:
            content += f"## {section.role.capitalize()}\n\n{section.content}\n\n"
        
        if prompt.tools:
            content += "## Tools\n\n"
            for tool in prompt.tools:
                content += f"- **{tool.name}**: {tool.description}\n"
                
        return content
