"""
Kimi (Moonshot AI / 月之暗面) 平台适配器模块。
适配 Kimi 开放平台 (api.moonshot.cn)、Kimi 智能助手及长上下文模型 (moonshot-v1-8k/32k/128k, kimi-latest)。
针对 Kimi 的超长上下文 (128k~200k) 与 Prompt Caching（前缀缓存）机制进行排版优化，
支持标准 Markdown 提示词导出与兼容 OpenAI 协议的 Moonshot API JSON 报文。
"""
import json
from pathlib import Path
from typing import Any, Dict, List

from promptforge.models import PromptOutput, PromptSection, TemplateSections
from promptforge.adapters.base import BaseAdapter


class KimiAdapter(BaseAdapter):
    """
    Kimi (Moonshot AI / 月之暗面) 适配器。
    支持超长上下文 (128k~200k Tokens)、Prompt Cache 缓存友好排版、
    系统提示词隔离、原生/自定义工具调用声明及标准 API JSON 请求体生成。
    """
    platform_name = 'kimi'
    max_tokens = 200000
    supports_system_prompt = True
    supports_tool_definitions = True
    output_format = 'markdown'

    def format_prompt(self, sections: TemplateSections, variables: Dict[str, Any]) -> List[PromptSection]:
        """
        格式化为 Kimi 提示词片段。
        """
        result = []
        if sections.system:
            result.append(PromptSection(role="system", content=sections.system))
        for msg in sections.messages:
            result.append(PromptSection(role=msg.role, content=msg.content))
        return result

    def export(self, prompt: PromptOutput) -> str:
        """
        导出为符合 Kimi / Moonshot AI 规范的人设与指令 Markdown 文本。
        静态角色设定置顶以最大化命中 Kimi 的 Prompt Caching 前缀缓存机制。
        """
        display_name = prompt.metadata.get('display_name', prompt.template_name)
        category = prompt.category

        content = f"# 【Kimi / Moonshot 智能体提示词】{display_name}\n\n"
        content += f"> **适配平台**: Kimi (Moonshot AI / 月之暗面) | **推荐基座模型**: `moonshot-v1-128k` / `kimi-latest`\n"
        content += f"> **上下文窗口**: 128k ~ 200k Tokens | **前缀缓存 (Prompt Cache)**: 已针对静态人设与规范做前置结构优化\n"
        content += f"> **任务分类**: {category}\n\n"

        for section in prompt.sections:
            if section.role == "system":
                content += "## 🌙 角色定位与核心准则 (System Persona & Principles)\n"
                content += "> 💡 *此区域为 Kimi 静态前缀缓存锚点 (Cache Anchor)，在长上下文交互中持续保留。*\n\n"
                content += f"{section.content}\n\n"
            elif section.role == "user":
                content += "## 📋 任务指引与执行工作流 (Workflow & Guidelines)\n\n"
                content += f"{section.content}\n\n"
            else:
                content += f"## 💬 {section.role.capitalize()}\n\n{section.content}\n\n"

        # Kimi 原生能力与扩展工具声明
        content += "## 🛠️ 能力与工具插件配置 (Capabilities & Tools)\n\n"
        content += "- **联网检索 (Web Search)**: 智能启用（自动获取最新网络资料、API 最新版本及官方事实）\n"
        content += "- **长文档/代码库解析 (Files & Long Context QA)**: 智能启用（支持深度解读超长文本、PDF、代码库）\n"

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

        content += "## 🎯 交互约束与质量规范 (Constraints)\n\n"
        content += "1. 严谨遵循上述角色定位，充分利用 Kimi 超长上下文深度推演能力，确保产出严谨、逻辑缜密。\n"
        content += "2. 对于复杂系统架构与工程代码，优先采用模块化、高可维护的设计，并注明关键边界条件。\n"
        content += "3. 代码块务必注明编程语言标识，并提供可直接执行的清晰示例。\n"

        return content.strip() + "\n"

    def export_to_file(self, prompt: PromptOutput, output_path: Path) -> None:
        """
        导出到文件。支持保存为 Markdown 配置文件 (.md) 或 Kimi API JSON 配置 (.json)。
        """
        if output_path.is_dir():
            target = output_path / f"kimi_agent_{prompt.template_name}.md"
        else:
            target = output_path

        if target.suffix.lower() == '.json':
            target.write_text(self.to_kimi_config(prompt), encoding='utf-8')
        else:
            target.write_text(self.export(prompt), encoding='utf-8')

    def to_kimi_config(self, prompt: PromptOutput, model: str = "moonshot-v1-128k") -> str:
        """
        导出为 Moonshot AI 开放平台标准 API 请求体（兼容 OpenAI 协议）。
        可以直接用于通过 curl 或 Python SDK 调用 https://api.moonshot.cn/v1/chat/completions。
        """
        system_content = ""
        user_content = ""

        for section in prompt.sections:
            if section.role == "system":
                system_content += section.content + "\n\n"
            elif section.role == "user":
                user_content += section.content + "\n\n"

        messages = []
        if system_content:
            messages.append({"role": "system", "content": system_content.strip()})
        if user_content:
            messages.append({"role": "user", "content": user_content.strip()})

        # 工具配置
        tools = []
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
            "platform": "Kimi (Moonshot AI 开放平台)",
            "api_endpoint": "https://api.moonshot.cn/v1/chat/completions",
            "model": model,
            "temperature": 0.3,
            "max_tokens": 4096,
            "messages": messages,
            "metadata": {
                "name": prompt.template_name,
                "display_name": prompt.metadata.get("display_name", prompt.template_name),
                "category": prompt.category,
                "version": prompt.metadata.get("version", "1.0.0"),
                "prompt_cache_optimized": True,
            }
        }

        if tools:
            config["tools"] = tools

        return json.dumps(config, ensure_ascii=False, indent=2)
