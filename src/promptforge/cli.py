"""
PromptForge 命令行工具 (CLI)。
提供多平台 Agent 提示词的生成、列举、校验、导出与 Web 界面启动功能。
"""
import sys
from pathlib import Path
from typing import List, Optional

# 针对 Windows 控制台默认 GBK 编码进行 UTF-8 适配，防止 Emoji 报 UnicodeEncodeError
if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import typer
from rich import print as rprint
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

from promptforge.adapters import ADAPTER_REGISTRY
from promptforge.core.category import CategoryManager, CATEGORIES
from promptforge.core.engine import TemplateEngine, EngineError
from promptforge.core.resolver import VariableResolver, ResolverError
from promptforge.core.validator import PromptValidator
from promptforge.models.prompt import PromptOutput, PromptSection

app = typer.Typer(
    name="promptforge",
    help="PromptForge - 多平台 Agent 规范提示词生成与管理工具",
    add_completion=False,
)
console = Console()


def _get_engine(custom_dir: Optional[Path] = None) -> TemplateEngine:
    """获取模板引擎实例"""
    cwd_custom = Path.cwd() / "custom_templates"
    custom_templates_dir = custom_dir or (cwd_custom if cwd_custom.is_dir() else None)
    return TemplateEngine(custom_templates_dir=custom_templates_dir)


def _parse_vars(var_list: Optional[List[str]]) -> dict:
    """解析 --var key=value 参数为字典"""
    vars_dict = {}
    if not var_list:
        return vars_dict
    for item in var_list:
        if "=" in item:
            k, v = item.split("=", 1)
            k = k.strip()
            v = v.strip()
            # 简易类型判断（详细类型校验交给 VariableResolver 依据模板定义处理）
            if v.lower() in ("true", "yes"):
                vars_dict[k] = True
            elif v.lower() in ("false", "no"):
                vars_dict[k] = False
            elif v.isdigit():
                vars_dict[k] = int(v)
            else:
                vars_dict[k] = v
        else:
            console.print(f"[yellow]警告: 忽略格式不正确的变量 '{item}'，请使用 key=value 格式[/yellow]")
    return vars_dict


@app.command("list")
def list_templates(
    category: Optional[str] = typer.Option(
        None, "--category", "-c", help=f"按分类筛选（{', '.join(CATEGORIES.keys())}）"
    ),
):
    """
    列出所有可用分类或特定分类下的提示词模板。
    """
    engine = _get_engine()
    cat_manager = engine.category_manager

    if category:
        cat_info = cat_manager.get_category(category)
        if not cat_info:
            console.print(f"[bold red]错误:[/bold red] 未知分类 '{category}'。可用分类: {', '.join(CATEGORIES.keys())}")
            raise typer.Exit(code=1)

        templates = cat_manager.list_templates(category)
        table = Table(title=f"{cat_info.icon} 分类: {cat_info.display_name} ({category})", show_header=True, header_style="bold cyan")
        table.add_column("模板名称", style="green", no_wrap=True)
        table.add_column("显示名称", style="white")
        table.add_column("描述", style="dim")
        table.add_column("支持平台", style="magenta")
        table.add_column("标签", style="yellow")

        if not templates:
            console.print(f"[yellow]分类 '{category}' 下暂无模板。[/yellow]")
            return

        for t in templates:
            table.add_row(
                t.name,
                t.display_name,
                t.description,
                ", ".join(t.platforms),
                ", ".join(t.tags),
            )
        console.print(table)
    else:
        # 显示所有分类汇总
        categories = cat_manager.list_categories()
        table = Table(title="📦 PromptForge 模板分类一览", show_header=True, header_style="bold blue")
        table.add_column("图标", justify="center", width=6)
        table.add_column("分类标识", style="cyan", no_wrap=True)
        table.add_column("分类名称", style="green")
        table.add_column("模板数量", justify="right", style="magenta")
        table.add_column("分类说明", style="dim")

        for cat in categories:
            table.add_row(
                cat.icon,
                cat.name,
                cat.display_name,
                str(cat.template_count),
                cat.description,
            )
        console.print(table)
        console.print("\n[dim]使用 [bold cyan]promptforge list --category <分类>[/bold cyan] 查看某分类下的所有详细模板。[/dim]")


@app.command("generate")
def generate_prompt(
    category: str = typer.Option(..., "--category", "-c", help="模板分类名称，如 coding, writing"),
    template: str = typer.Option(..., "--template", "-t", help="模板名称，如 code_review, bug_fix"),
    platform: str = typer.Option("openai", "--platform", "-p", help=f"目标平台，可选: {', '.join(ADAPTER_REGISTRY.keys())}"),
    preset: Optional[str] = typer.Option(None, "--preset", help="选用预设需求场景（支持序号如 '1'、ID 或标题关键字）"),
    var: Optional[List[str]] = typer.Option(None, "--var", "-v", help="模板变量，格式 key=value，可多次使用"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="交互式引导填写变量"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="输出文件路径，若指定则保存至文件"),
    lang: str = typer.Option("zh", "--lang", "-l", help="语言选择: zh (中文) 或 en (英文)"),
):
    """
    根据指定模板与平台生成规范的 Agent 提示词（支持选用预设场景）。
    """
    engine = _get_engine()
    resolver = VariableResolver()
    validator = PromptValidator()

    # 1. 检查平台有效性
    if platform not in ADAPTER_REGISTRY:
        console.print(f"[bold red]错误:[/bold red] 不支持的平台 '{platform}'。可用平台: {', '.join(ADAPTER_REGISTRY.keys())}")
        raise typer.Exit(code=1)

    # 2. 加载模板
    try:
        tmpl = engine.load_template(category, template)
    except EngineError as e:
        console.print(f"[bold red]加载模板失败:[/bold red] {e}")
        raise typer.Exit(code=1)

    # 3. 处理预设需求场景
    user_vars = {}
    if preset:
        matched_preset = resolver.find_preset(tmpl, preset)
        if not matched_preset:
            console.print(f"[bold red]错误:[/bold red] 模板 '{tmpl.meta.name}' 未找到预设 '{preset}'。")
            if tmpl.presets:
                console.print("[yellow]可用预设场景：[/yellow]")
                for idx, p in enumerate(tmpl.presets, 1):
                    console.print(f"  [{idx}] {p.id} ({p.title})")
            else:
                console.print("[yellow]该模板暂无内置预设场景。[/yellow]")
            raise typer.Exit(code=1)
        user_vars.update(matched_preset.variables)
        console.print(f"[bold green]✓ 已加载预设场景：[/bold green] [cyan]{matched_preset.title}[/cyan]")

    # 4. 解析与提示变量
    user_vars.update(_parse_vars(var))
    try:
        if interactive:
            console.print(f"[cyan]开始交互式填写模板 '{tmpl.meta.display_name}' 变量:[/cyan]")
            prompted_vars = resolver.prompt_for_variables(tmpl, prefilled=user_vars)
            user_vars.update(prompted_vars)
        final_vars = resolver.resolve(tmpl, user_vars)
    except ResolverError as e:
        console.print(f"[bold red]变量解析失败:[/bold red] {e}")
        console.print("[yellow]提示: 可以使用 -i / --interactive 进入交互式模式填写，或通过 --preset / -v 传入所需变量。[/yellow]")
        raise typer.Exit(code=1)

    # 5. 渲染提示词
    try:
        rendered = engine.render(tmpl, final_vars, platform=platform, lang=lang)
    except EngineError as e:
        console.print(f"[bold red]渲染失败:[/bold red] {e}")
        raise typer.Exit(code=1)

    # 6. 获取适配器格式化输出
    adapter = ADAPTER_REGISTRY[platform]()
    formatted_content = adapter.export(rendered)

    # 7. 验证
    val_result = validator.validate(rendered, platform=platform)

    # 8. 控制台展示
    lang_label = "中文" if lang == "zh" else "English"
    title = f"🚀 [{tmpl.meta.display_name}] -> 平台: {platform.upper()} (语言: {lang_label})"
    lexer = "json" if adapter.output_format == "json" else "markdown"
    console.print(Panel(Syntax(formatted_content, lexer, theme="monokai", word_wrap=True), title=title, border_style="green"))

    # 状态栏
    token_str = f"预估 Tokens: [bold cyan]{rendered.token_estimate}[/bold cyan]"
    if val_result.is_valid:
        status_str = "[bold green]✓ 校验通过[/bold green]"
    else:
        status_str = "[bold red]✗ 存在校验错误[/bold red]"
    console.print(f"{status_str} | {token_str}")

    for warn in val_result.warnings:
        console.print(f"[yellow]⚠️ 提示:[/yellow] {warn}")
    for err in val_result.errors:
        console.print(f"[red]❌ 错误:[/red] {err}")

    # 9. 保存文件
    if output:
        try:
            adapter.export_to_file(rendered, output)
            console.print(f"[bold green]✓ 文件已保存至:[/bold green] {output.resolve()}")
        except Exception as e:
            console.print(f"[bold red]保存文件失败:[/bold red] {e}")
            raise typer.Exit(code=1)


@app.command("export")
def export_prompt(
    category: str = typer.Option(..., "--category", "-c", help="模板分类名称"),
    template: str = typer.Option(..., "--template", "-t", help="模板名称"),
    platform: str = typer.Option(..., "--platform", "-p", help="目标平台"),
    output: Path = typer.Option(..., "--output", "-o", help="输出目标文件路径"),
    preset: Optional[str] = typer.Option(None, "--preset", help="选用预设需求场景（支持序号或ID）"),
    var: Optional[List[str]] = typer.Option(None, "--var", "-v", help="模板变量 key=value"),
    lang: str = typer.Option("zh", "--lang", "-l", help="语言: zh / en"),
):
    """
    快速导出提示词为目标平台的专用文件（支持 --preset 快速注入）。
    """
    engine = _get_engine()
    resolver = VariableResolver()

    if platform not in ADAPTER_REGISTRY:
        console.print(f"[bold red]错误:[/bold red] 不支持的平台 '{platform}'")
        raise typer.Exit(code=1)

    try:
        tmpl = engine.load_template(category, template)
        user_vars = {}
        if preset:
            matched_preset = resolver.find_preset(tmpl, preset)
            if not matched_preset:
                console.print(f"[bold red]错误:[/bold red] 未找到预设 '{preset}'")
                raise typer.Exit(code=1)
            user_vars.update(matched_preset.variables)
        user_vars.update(_parse_vars(var))
        final_vars = resolver.resolve(tmpl, user_vars)
        rendered = engine.render(tmpl, final_vars, platform=platform, lang=lang)
        adapter = ADAPTER_REGISTRY[platform]()
        adapter.export_to_file(rendered, output)
        console.print(f"[bold green]✓ 导出成功:[/bold green] 已写入 {output.resolve()}")
    except Exception as e:
        console.print(f"[bold red]导出失败:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command("presets")
def list_presets(
    category: str = typer.Option(..., "--category", "-c", help="模板分类名称"),
    template: str = typer.Option(..., "--template", "-t", help="模板名称"),
):
    """
    列出指定模板内置的预设需求场景与示例参数。
    """
    engine = _get_engine()
    try:
        tmpl = engine.load_template(category, template)
    except EngineError as e:
        console.print(f"[bold red]加载模板失败:[/bold red] {e}")
        raise typer.Exit(code=1)

    if not tmpl.presets:
        console.print(f"[yellow]模板 '{category}/{template}' 暂无预设需求场景。[/yellow]")
        return

    table = Table(
        title=f"💡 模板 [{tmpl.meta.display_name}] 内置需求预设",
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("序号", justify="center", width=6)
    table.add_column("预设标识 (ID)", style="green", no_wrap=True)
    table.add_column("场景标题", style="white")
    table.add_column("场景说明", style="dim")
    table.add_column("预设变量", style="yellow")

    for idx, p in enumerate(tmpl.presets, 1):
        vars_summary = ", ".join(f"{k}={v}" for k, v in p.variables.items())
        if len(vars_summary) > 40:
            vars_summary = vars_summary[:37] + "..."
        table.add_row(str(idx), p.id, p.title, p.description or "", vars_summary)

    console.print(table)
    console.print(f"\n[dim]使用 [bold cyan]promptforge generate -c {category} -t {template} --preset <序号/ID>[/bold cyan] 即可一键直接调用。[/dim]")


@app.command("validate")
def validate_prompt(
    file: Path = typer.Argument(..., help="需要校验的提示词文件路径"),
    platform: str = typer.Option("openai", "--platform", "-p", help="目标平台"),
):
    """
    校验指定提示词文件的合规性、Token占用与潜在风险。
    """
    if not file.exists():
        console.print(f"[bold red]错误:[/bold red] 文件不存在: {file}")
        raise typer.Exit(code=1)

    content = file.read_text(encoding="utf-8")
    validator = PromptValidator()
    tokens = validator.estimate_tokens(content)

    dummy_prompt = PromptOutput(
        template_name=file.stem,
        category="custom",
        platform=platform,
        sections=[PromptSection(role="user", content=content)],
        token_estimate=tokens,
        raw_text=content,
    )

    result = validator.validate(dummy_prompt, platform=platform)

    console.print(Panel(f"文件: {file.name}\n平台: {platform}\n预估 Tokens: {tokens}", title="🔍 提示词校验报告", border_style="blue"))
    if result.is_valid:
        console.print("[bold green]✓ 提示词验证通过！未发现严重阻断性问题。[/bold green]")
    else:
        console.print("[bold red]✗ 提示词验证未通过，请检查以下错误：[/bold red]")
        for err in result.errors:
            console.print(f"  [red]• {err}[/red]")

    if result.warnings:
        console.print("\n[bold yellow]警告事项：[/bold yellow]")
        for warn in result.warnings:
            console.print(f"  [yellow]• {warn}[/yellow]")

    if result.suggestions:
        console.print("\n[bold cyan]优化建议：[/bold cyan]")
        for sug in result.suggestions:
            console.print(f"  [cyan]• {sug}[/cyan]")


@app.command("platforms")
def list_platforms():
    """
    列出所有支持的平台适配器与配置特性。
    """
    table = Table(title="🤖 支持的 Agent 平台一览", show_header=True, header_style="bold magenta")
    table.add_column("平台标识", style="cyan", no_wrap=True)
    table.add_column("输出格式", style="green")
    table.add_column("最大Token限制", justify="right", style="yellow")
    table.add_column("系统提示词", justify="center")
    table.add_column("工具/函数调用", justify="center")

    for name, adapter_cls in ADAPTER_REGISTRY.items():
        adapter = adapter_cls()
        max_t = f"{adapter.max_tokens:,}" if adapter.max_tokens else "无限制"
        sys_p = "✅" if adapter.supports_system_prompt else "❌"
        tools = "✅" if adapter.supports_tool_definitions else "❌"
        table.add_row(name, adapter.output_format.upper(), max_t, sys_p, tools)

    console.print(table)


@app.command("init")
def init_project():
    """
    在当前目录初始化 PromptForge 配置和自定义模板目录。
    """
    custom_dir = Path.cwd() / "custom_templates"
    custom_dir.mkdir(exist_ok=True)
    for cat in CATEGORIES.keys():
        (custom_dir / cat).mkdir(exist_ok=True)

    config_file = Path.cwd() / "promptforge.yaml"
    if not config_file.exists():
        sample_config = (
            "# PromptForge 项目配置文件\n"
            "default_platform: openai\n"
            "default_language: zh\n"
            "custom_templates_dir: ./custom_templates\n"
        )
        config_file.write_text(sample_config, encoding="utf-8")

    console.print("[bold green]✓ 初始化完成！[/bold green]")
    console.print(f"已创建自定义模板目录: [cyan]{custom_dir.resolve()}[/cyan]")
    console.print(f"已生成项目配置文件: [cyan]{config_file.resolve()}[/cyan]")


@app.command("web")
def run_web(
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="监听主机地址"),
    port: int = typer.Option(8000, "--port", "-p", help="监听端口"),
    reload: bool = typer.Option(False, "--reload", help="开发模式自动重载"),
    open_browser: bool = typer.Option(True, "--open-browser/--no-browser", "-b", help="启动后自动在默认浏览器中打开"),
):
    """
    启动 PromptForge 本地 Web 可视化交互界面（默认自动打开浏览器）。
    """
    try:
        from promptforge.web.app import run_server
    except ImportError:
        console.print("[bold red]错误:[/bold red] 缺少 Web 依赖。请运行: pip install fastapi uvicorn")
        raise typer.Exit(code=1)

    console.print(f"[bold green]🚀 正在启动 PromptForge Web 工作台...[/bold green]")
    console.print(f"访问地址: [bold cyan]http://{host}:{port}[/bold cyan]")
    if open_browser:
        console.print("[dim]已请求自动打开浏览器...[/dim]")
    run_server(host=host, port=port, reload=reload, open_browser=open_browser)


if __name__ == "__main__":
    app()
