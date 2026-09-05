import json
from pathlib import Path
from typing import Any, Dict, List

from promptforge.models import PromptOutput, PromptSection, TemplateSections
from promptforge.adapters.base import BaseAdapter


class GeminiAdapter(BaseAdapter):
    """
    Gemini 平台适配器。
    支持系统指令和函数声明。输出格式为 JSON。
    """
    platform_name = 'gemini'
    max_tokens = 1000000
    supports_system_prompt = True
    supports_tool_definitions = True
    output_format = 'json'

    def format_prompt(self, sections: TemplateSections, variables: Dict[str, Any]) -> List[PromptSection]:
        """
        格式化为 Gemini 提示词片段。
        """
        result = []
        if sections.system:
            result.append(PromptSection(role="system", content=sections.system))
        for msg in sections.messages:
            result.append(PromptSection(role=msg.role, content=msg.content))
        return result

    def export(self, prompt: PromptOutput) -> str:
        """
        导出为 Gemini API 兼容的 JSON 格式字符串。
        """
        output: Dict[str, Any] = {"contents": []}
        
        for section in prompt.sections:
            if section.role == "system":
                if "systemInstruction" not in output:
                    output["systemInstruction"] = {"parts": [{"text": section.content}]}
                else:
                    output["systemInstruction"]["parts"][0]["text"] += "\n" + section.content
            else:
                # Gemini roles are typically "user" or "model"
                role_mapped = "model" if section.role == "assistant" else section.role
                output["contents"].append({
                    "role": role_mapped,
                    "parts": [{"text": section.content}]
                })
                
        if prompt.tools:
            function_declarations = []
            for tool in prompt.tools:
                tool_dict = {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": {
                        "type": "OBJECT",
                        "properties": {
                            p.name: {"type": p.type.upper(), "description": p.description}
                            for p in tool.parameters
                        },
                        "required": [p.name for p in tool.parameters if p.required]
                    }
                }
                function_declarations.append(tool_dict)
            output["tools"] = [{"functionDeclarations": function_declarations}]
                
        return json.dumps(output, ensure_ascii=False, indent=2)

    def export_to_file(self, prompt: PromptOutput, output_path: Path) -> None:
        """
        将 Gemini 格式的 JSON 导出到文件。
        """
        output_path.write_text(self.export(prompt), encoding='utf-8')
