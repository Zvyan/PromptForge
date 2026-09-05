import json
from pathlib import Path
from typing import Any, Dict, List

from promptforge.models import PromptOutput, PromptSection, TemplateSections
from promptforge.adapters.base import BaseAdapter


class ClaudeAdapter(BaseAdapter):
    """
    Claude 平台适配器。
    支持系统提示词（作为顶层参数）和工具定义。输出格式为 JSON。
    """
    platform_name = 'claude'
    max_tokens = 200000
    supports_system_prompt = True
    supports_tool_definitions = True
    output_format = 'json'

    def format_prompt(self, sections: TemplateSections, variables: Dict[str, Any]) -> List[PromptSection]:
        """
        格式化为 Claude 提示词片段。
        """
        result = []
        if sections.system:
            result.append(PromptSection(role="system", content=sections.system))
        for msg in sections.messages:
            result.append(PromptSection(role=msg.role, content=msg.content))
        return result

    def export(self, prompt: PromptOutput) -> str:
        """
        导出为 Claude API 兼容的 JSON 格式字符串。系统提示词作为顶层字段。
        """
        output: Dict[str, Any] = {"messages": []}
        
        for section in prompt.sections:
            if section.role == "system":
                # 合并多个系统提示词（如果存在）
                if "system" in output:
                    output["system"] += "\n" + section.content
                else:
                    output["system"] = section.content
            else:
                output["messages"].append({
                    "role": section.role,
                    "content": section.content
                })
                
        if prompt.tools:
            output["tools"] = []
            for tool in prompt.tools:
                tool_dict = {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            p.name: {"type": p.type, "description": p.description}
                            for p in tool.parameters
                        },
                        "required": [p.name for p in tool.parameters if p.required]
                    }
                }
                output["tools"].append(tool_dict)
                
        return json.dumps(output, ensure_ascii=False, indent=2)

    def export_to_file(self, prompt: PromptOutput, output_path: Path) -> None:
        """
        将 Claude 格式的 JSON 导出到文件。
        """
        output_path.write_text(self.export(prompt), encoding='utf-8')
        
    def to_claude_project_instructions(self, prompt: PromptOutput) -> str:
        """
        生成 Claude 项目的自定义指令（Custom Instructions）。
        """
        content = ""
        for section in prompt.sections:
            if section.role == "system":
                content += section.content + "\n\n"
        
        content += "## Additional Instructions\n\n"
        for section in prompt.sections:
            if section.role != "system":
                content += f"### {section.role.capitalize()}\n\n{section.content}\n\n"
                
        return content.strip()
