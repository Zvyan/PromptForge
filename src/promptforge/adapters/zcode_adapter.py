"""
ZCode (智谱 GLM Agent 智能体平台) 适配器模块。
适配智谱清言智能体平台、GLM-4 / CodeGeeX Code Agent 规范。
包含人设配置、工作流、输出规范、工具定义（含网络检索与代码解释器）以及开放平台 API 报文支持。
"""
import json
from pathlib import Path
from typing import Any, Dict, List

from promptforge.models import PromptOutput, PromptSection, TemplateSections
from promptforge.adapters.base import BaseAdapter


class ZCodeAdapter(BaseAdapter):
    """
    ZCode (智谱 GLM Agent 平台) 适配器。
    面向智谱清言智能体平台、GLM-4 开放平台以及 CodeGeeX 编程智能体，
    生成符合 GLM 规范的人设设定、技能流、工具声明与 API 配置报文。
    """
    platform_name = 'zcode'
    max_tokens = 128000
    supports_system_prompt = True
    supports_tool_definitions = True
    output_format = 'markdown'

    def format_prompt(self, sections: TemplateSections, variables: Dict[str, Any]) -> List[PromptSection]:
        """
        格式化为 GLM 智能体提示词片段。
        """
        result = []
        if sections.system:
            result.append(PromptSection(role="system", content=sections.system))
        for msg in sections.messages:
            result.append(PromptSection(role=msg.role, content=msg.content))
        return result

    def export(self, prompt: PromptOutput) -> str:
        """
        导出为符合智谱清言智能体平台 (GLM Agent) 规范的人设与指令 Markdown 文本。
        可直接复制粘贴到智谱智能体配置后台的「提示词 / 人设设定」中。
        """
        display_name = prompt.metadata.get('display_name', prompt.template_name)
        category = prompt.category

        content = f"# 【GLM 智能体人设配置】{display_name}\n\n"
        content += f"> **智能体分类**: {category} | **推荐基座模型**: GLM-4-Plus / GLM-4 / CodeGeeX\n\n"

        for section in prompt.sections:
            if section.role == "system":
                content += f"## 🤖 角色定位与设定 (Role & System Instructions)\n\n{section.content}\n\n"
            elif section.role == "user":
                content += f"## 📋 任务指引与执行工作流 (Workflow & Guidelines)\n\n{section.content}\n\n"
            else:
                content += f"## 💬 {section.role.capitalize()}\n\n{section.content}\n\n"

        # GLM 平台原生与扩展工具声明
        content += "## 🛠️ 能力与工具插件配置 (Capabilities & Tools)\n\n"
        content += "- **代码解释器 (Code Interpreter)**: 自动启用（支持 Python/多语言沙箱执行与数据分析）\n"
        content += "- **网络检索 (Web Search)**: 智能启用（需要获取实时开发文档或最新库时调用）\n"

        if prompt.tools:
            content += "\n### 自定义函数/API 插件列表 (Function Calling):\n\n"
            for tool in prompt.tools:
                content += f"- **`{tool.name}`**: {tool.description}\n"
                if tool.parameters:
                    content += "  - 参数要求:\n"
                    for param in tool.parameters:
                        req = "必选" if param.required else "可选"
                        content += f"    * `{param.name}` ({param.type}, {req}): {param.description}\n"
            content += "\n"

        content += "## 🎯 交互约束 (Constraints)\n\n"
        content += "1. 严谨遵循上述角色定位，优先保证代码与指令的准确性、安全性和可维护性。\n"
        content += "2. 遇到不明确的需求，优先提出澄清问题，而非盲目推测。\n"
        content += "3. 代码块务必注明编程语言标识，并提供可直接执行的清晰示例。\n"

        return content.strip() + "\n"

    def export_to_file(self, prompt: PromptOutput, output_path: Path) -> None:
        """
        导出到文件。支持保存为 Markdown 配置文件 (.md) 或 GLM Agent JSON 配置。
        """
        if output_path.is_dir():
            target = output_path / f"glm_agent_{prompt.template_name}.md"
        else:
            target = output_path

        if target.suffix.lower() == '.json':
            target.write_text(self.to_zcode_config(prompt), encoding='utf-8')
        else:
            target.write_text(self.export(prompt), encoding='utf-8')

    def to_zcode_config(self, prompt: PromptOutput) -> str:
        """
        导出为智谱 GLM 开放平台标准 Agent API 报文格式（JSON Schema）。
        可以直接用于调用智谱清言 GLM-4 API 或导入智能体平台。
        """
        system_content = ""
        user_content = ""

        for section in prompt.sections:
            if section.role == "system":
                system_content += section.content + "\n\n"
            elif section.role == "user":
                user_content += section.content + "\n\n"

        messages = [
            {"role": "system", "content": system_content.strip()}
        ]
        if user_content:
            messages.append({"role": "user", "content": user_content.strip()})

        # 组织 GLM-4 工具格式
        tools: List[Dict[str, Any]] = [
            {
                "type": "code_interpreter"
            },
            {
                "type": "web_search",
                "web_search": {
                    "enable": True,
                    "search_result": True
                }
            }
        ]

        if prompt.tools:
            for tool in prompt.tools:
                tools.append({
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": {
                            "type": "object",
                            "properties": {
                                p.name: {
                                    "type": p.type,
                                    "description": p.description,
                                }
                                for p in tool.parameters
                            },
                            "required": [p.name for p in tool.parameters if p.required]
                        }
                    }
                })

        config: Dict[str, Any] = {
            "platform": "GLM Agent (智谱开放平台)",
            "model": "glm-4-plus",
            "temperature": 0.3,
            "max_tokens": 4096,
            "stream": False,
            "messages": messages,
            "tools": tools,
            "agent_metadata": {
                "name": prompt.template_name,
                "display_name": prompt.metadata.get("display_name", prompt.template_name),
                "category": prompt.category,
                "version": prompt.metadata.get("version", "1.0.0"),
            }
        }

        return json.dumps(config, ensure_ascii=False, indent=2)
