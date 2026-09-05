from typing import Dict, Any, List, Optional
from rich.prompt import Prompt, Confirm, IntPrompt, FloatPrompt
from promptforge.models.template import Template, VariableDefinition, VariableType, PresetScenario

class ResolverError(Exception):
    """变量解析错误基类"""
    pass

class VariableResolver:
    """变量解析器，处理模板变量与预设场景解析。"""

    def find_preset(self, template: Template, preset_query: str) -> Optional[PresetScenario]:
        """
        根据编号（从 1 开始）、ID 或标题名称查找模板中的预设场景。
        
        Args:
            template: 模板对象
            preset_query: 预设查询标识（如 "1", "concurrency_audit", "高并发"）
            
        Returns:
            匹配到的 PresetScenario，未找到则返回 None
        """
        if not template.presets:
            return None
        
        # 1. 尝试解析为数字编号 (1-based index)
        if str(preset_query).isdigit():
            idx = int(preset_query) - 1
            if 0 <= idx < len(template.presets):
                return template.presets[idx]
        
        # 2. 匹配 ID（忽略大小写）
        for p in template.presets:
            if p.id.lower() == str(preset_query).lower():
                return p
                
        # 3. 匹配标题（包含或相等）
        for p in template.presets:
            if str(preset_query).lower() in p.title.lower():
                return p
                
        return None

    def resolve(self, template: Template, user_vars: Dict[str, Any]) -> Dict[str, Any]:
        """
        合并用户变量与模板默认值，验证类型，并在缺少必需变量时抛出异常。
        
        Args:
            template: 模板对象
            user_vars: 用户提供的变量
            
        Returns:
            合并并验证后的变量字典
            
        Raises:
            ResolverError: 当缺少必需变量或类型/值无效时
        """
        result = {}
        if not template.variables:
            return result
            
        for name, var_def in template.variables.items():
            if name in user_vars:
                value = user_vars[name]
                result[name] = self._validate_and_coerce(name, value, var_def)
            elif var_def.default is not None:
                result[name] = var_def.default
            elif var_def.required:
                raise ResolverError(f"缺少必需变量: {name} ({var_def.description})")
        
        return result
        
    def prompt_for_variables(
        self, template: Template, prefilled: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        交互式提示用户输入缺失的变量，支持选择内置预设场景。
        
        Args:
            template: 模板对象
            prefilled: 可选，已预先填充的变量字典
            
        Returns:
            用户输入的变量字典
        """
        result = {}
        if not template.variables:
            return result

        prefilled_vars = dict(prefilled or {})

        # 如果模板包含预设场景且未预填变量，交互提示用户是否选用预设
        if template.presets and not prefilled_vars:
            from rich import print as rprint
            rprint("\n[bold cyan]💡 该模板提供以下预设需求场景：[/bold cyan]")
            rprint("  [dim][0] ✍️ 手动填写全部参数（不使用预设）[/dim]")
            for idx, p in enumerate(template.presets, 1):
                desc_part = f" - [dim]{p.description}[/dim]" if p.description else ""
                rprint(f"  [green][{idx}][/green] ⚡ [bold]{p.title}[/bold]{desc_part}")
            
            choice = Prompt.ask("\n请选择预设场景编号（或按 Enter 自定义）", default="0")
            if choice != "0":
                preset = self.find_preset(template, choice)
                if preset:
                    rprint(f"[bold green]✓ 已选用预设：{preset.title}[/bold green]\n")
                    prefilled_vars.update(preset.variables)

        for name, var_def in template.variables.items():
            default_val = prefilled_vars.get(name, var_def.default)
            prompt_text = f"{var_def.description or name}"
            if var_def.options:
                prompt_text += f" {var_def.options}"
                
            if var_def.type == VariableType.BOOLEAN:
                result[name] = Confirm.ask(prompt_text, default=bool(default_val) if default_val is not None else False)
            elif var_def.type == VariableType.INTEGER:
                result[name] = IntPrompt.ask(prompt_text, default=int(default_val) if default_val is not None else 0)
            elif var_def.type == VariableType.FLOAT:
                result[name] = FloatPrompt.ask(prompt_text, default=float(default_val) if default_val is not None else 0.0)
            elif var_def.options:
                result[name] = Prompt.ask(prompt_text, choices=var_def.options, default=str(default_val) if default_val else None)
            else:
                result[name] = Prompt.ask(prompt_text, default=str(default_val) if default_val is not None else None)
                
            result[name] = self._validate_and_coerce(name, result[name], var_def)
            
        return result
        
    def _validate_and_coerce(self, name: str, value: Any, var_def: VariableDefinition) -> Any:
        """
        验证变量并执行类型转换。
        """
        if value is None:
            if var_def.required:
                raise ResolverError(f"变量 {name} 不能为空")
            return None
            
        try:
            if var_def.type == VariableType.STRING:
                value = str(value)
            elif var_def.type == VariableType.INTEGER:
                value = int(value)
            elif var_def.type == VariableType.FLOAT:
                value = float(value)
            elif var_def.type == VariableType.BOOLEAN:
                if isinstance(value, str):
                    value = value.lower() in ('true', 'yes', '1', 'y')
                else:
                    value = bool(value)
            elif var_def.type == VariableType.LIST:
                if isinstance(value, str):
                    value = [item.strip() for item in value.split(',')]
                elif not isinstance(value, list):
                    value = list(value)
        except (ValueError, TypeError):
            raise ResolverError(f"变量 {name} 类型转换失败: 无法转换为 {var_def.type.value}")
            
        if var_def.options and value not in var_def.options:
            raise ResolverError(f"变量 {name} 的值 {value} 不在允许的选项中: {var_def.options}")
            
        return value
