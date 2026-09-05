"""
模板引擎模块，负责加载、渲染模板并适配不同平台。
"""
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List

import tiktoken
from jinja2 import Environment, StrictUndefined

from promptforge.models.template import Template, TemplateMeta, SystemSection
from promptforge.models.prompt import PromptOutput, PromptSection
from .category import CategoryManager


class EngineError(Exception):
    """模板引擎错误"""
    pass


class TemplateEngine:
    """核心模板引擎，处理模板加载、渲染和平台适配。"""

    def __init__(
        self,
        templates_dir: Optional[Path] = None,
        custom_templates_dir: Optional[Path] = None,
    ):
        """
        初始化模板引擎。

        Args:
            templates_dir: 内置模板目录，默认为项目根目录下的 templates/
            custom_templates_dir: 自定义模板目录，优先级高于内置模板
        """
        # 默认模板目录：项目根目录 / templates
        self.templates_dir = templates_dir or (
            Path(__file__).resolve().parent.parent.parent.parent / "templates"
        )
        self.custom_templates_dir = custom_templates_dir
        self.category_manager = CategoryManager(self.templates_dir.parent)
        self.jinja_env = Environment(undefined=StrictUndefined)

        # tiktoken 编码器（用于 token 估算）
        try:
            self._encoding = tiktoken.get_encoding("cl100k_base")
        except Exception:
            self._encoding = None

    # ------------------------------------------------------------------
    # 模板加载
    # ------------------------------------------------------------------

    def load_template(self, category: str, name: str) -> Template:
        """
        加载 YAML 模板，自定义模板优先于内置模板。

        Args:
            category: 类别名称
            name: 模板名称（不含扩展名）

        Returns:
            解析后的 Template 对象

        Raises:
            EngineError: 找不到模板或解析失败时
        """
        file_name = f"{name}.yaml"
        target_path = None

        # 优先查找自定义模板
        if self.custom_templates_dir:
            custom_path = self.custom_templates_dir / category / file_name
            if custom_path.exists():
                target_path = custom_path

        # 回退到内置模板
        if not target_path:
            builtin_path = self.templates_dir / category / file_name
            if builtin_path.exists():
                target_path = builtin_path

        if not target_path:
            raise EngineError(f"找不到模板: {category}/{name}")

        try:
            return Template.from_yaml(target_path)
        except Exception as e:
            raise EngineError(f"加载模板失败 {target_path}: {e}") from e

    # ------------------------------------------------------------------
    # 渲染
    # ------------------------------------------------------------------

    def render(
        self,
        template: Template,
        variables: Dict[str, Any],
        platform: str = "openai",
        lang: str = "zh",
    ) -> PromptOutput:
        """
        使用 Jinja2 渲染模板，并输出面向指定平台的 PromptOutput。

        Args:
            template: 模板对象
            variables: 渲染变量字典
            platform: 目标平台名称（openai / claude / gemini / cursor / zcode / …）
            lang: 语言选择 ('zh' 或 'en')

        Returns:
            渲染后的 PromptOutput
        """
        sections: List[PromptSection] = []

        active_sections = template.sections
        if lang == "en" and getattr(template, "sections_en", None):
            active_sections = template.sections_en

        # 自动填充模板定义的默认变量，防止直接调用 render 时未提供默认变量而抛出 UndefinedError
        merged_variables = {}
        if template.variables:
            for v_name, v_def in template.variables.items():
                if v_def.default is not None:
                    merged_variables[v_name] = v_def.default
        merged_variables.update(variables)

        # --- 渲染 system 部分 ---
        if active_sections and active_sections.system:
            system_text = self._render_system_section(
                active_sections.system, merged_variables
            )
            if lang == "en" and not getattr(template, "sections_en", None):
                system_text = "Please formulate the response in English.\n\n" + system_text
            sections.append(PromptSection(role="system", content=system_text))

        # --- 渲染 user 部分 ---
        if active_sections and active_sections.user:
            user_text = self._render_text(active_sections.user, merged_variables)
            sections.append(PromptSection(role="user", content=user_text))

        # 合并所有文本用于 raw_text 和 token 估算
        raw_text = "\n\n".join(s.content for s in sections)
        token_estimate = self.estimate_tokens(raw_text)

        return PromptOutput(
            template_name=template.meta.name,
            category=template.meta.category,
            platform=platform,
            sections=sections,
            tool_definitions=None,
            metadata={
                "display_name": template.meta.display_name,
                "version": template.meta.version,
                "tags": template.meta.tags,
                "lang": lang,
            },
            token_estimate=token_estimate,
            raw_text=raw_text,
        )

    def _render_system_section(
        self, system: SystemSection, variables: Dict[str, Any]
    ) -> str:
        """
        渲染 SystemSection 的各子字段并拼接为完整的系统提示词。
        """
        parts: List[str] = []

        if system.role:
            parts.append(self._render_text(system.role, variables).strip())

        if system.instructions:
            parts.append(self._render_text(system.instructions, variables).strip())

        if system.output_format:
            parts.append(
                "## 输出格式\n"
                + self._render_text(system.output_format, variables).strip()
            )

        if system.constraints:
            if isinstance(system.constraints, list):
                rendered = [self._render_text(c, variables).strip() for c in system.constraints]
                parts.append("## 约束条件\n" + "\n".join(f"- {c}" for c in rendered))
            else:
                parts.append(
                    "## 约束条件\n"
                    + self._render_text(system.constraints, variables).strip()
                )

        if system.examples:
            example_lines = ["## 示例"]
            for i, ex in enumerate(system.examples, 1):
                for k, v in ex.items():
                    example_lines.append(f"**{k}**: {v}")
                if i < len(system.examples):
                    example_lines.append("---")
            parts.append("\n".join(example_lines))

        return "\n\n".join(parts)

    def _render_text(self, content: str, variables: Dict[str, Any]) -> str:
        """
        渲染单个 Jinja2 模板字符串。

        Args:
            content: 模板字符串
            variables: 变量字典

        Returns:
            渲染后的字符串

        Raises:
            EngineError: 渲染失败
        """
        try:
            jinja_template = self.jinja_env.from_string(content)
            return jinja_template.render(**variables)
        except Exception as e:
            raise EngineError(f"渲染失败: {e}") from e

    # ------------------------------------------------------------------
    # 辅助方法
    # ------------------------------------------------------------------

    def list_templates(self, category: Optional[str] = None) -> List[TemplateMeta]:
        """
        列出可用模板。

        Args:
            category: 可选，按类别过滤

        Returns:
            模板元数据列表
        """
        return self.category_manager.list_templates(category)

    def get_adapter(self, platform: str):
        """
        获取指定平台的适配器实例。

        Args:
            platform: 平台名称

        Returns:
            适配器实例

        Raises:
            EngineError: 不支持的平台
        """
        from promptforge.adapters import ADAPTER_REGISTRY

        adapter_cls = ADAPTER_REGISTRY.get(platform)
        if adapter_cls is None:
            raise EngineError(
                f"不支持的平台: {platform}。可用平台: {list(ADAPTER_REGISTRY.keys())}"
            )
        return adapter_cls()

    def estimate_tokens(self, text: str) -> int:
        """
        使用 tiktoken (cl100k_base) 估算文本的 token 数量。

        Args:
            text: 输入文本

        Returns:
            token 数量估算值
        """
        if self._encoding:
            try:
                return len(self._encoding.encode(text, disallowed_special=()))
            except Exception:
                pass
        # 回退到字符级估算
        return len(text) // 4
