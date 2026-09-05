#!/usr/bin/env python3
"""
PromptForge 统一启动入口 (Launcher)。
支持交互式控制台导航菜单、一键 Web UI 启动（自动打开浏览器）以及原生命令行透传。
"""
import sys
import os
from pathlib import Path

# 针对 Windows 控制台编码防护
if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# 确保 src 目录在 Python 模块搜索路径中
SRC_DIR = Path(__file__).resolve().parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import typer
from rich import print as rprint
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()


def show_interactive_menu():
    """显示启动交互菜单"""
    banner = (
        "[bold cyan]PromptForge — 多平台 Agent 规范提示词引擎[/bold cyan]\n"
        "[dim]9 大场景分类 • 56 套工程级模板 • 8 大平台深度适配 • 丰富实战需求预设[/dim]"
    )
    console.print(Panel(banner, border_style="blue", expand=False))

    console.print("\n[bold]请选择需要运行的功能或模式：[/bold]")
    console.print("  [bold green][1][/bold green] 🌐 [bold]启动 Web 可视化工作台[/bold] [dim](推荐：自动打开浏览器、图形化表单与实时预览)[/dim]")
    console.print("  [bold green][2][/bold green] 💻 [bold]向导式生成提示词 (CLI Wizard)[/bold] [dim](交互式选分类、模板、实战预设与平台)[/dim]")
    console.print("  [bold green][3][/bold green] 📦 [bold]浏览分类与模板全集一览[/bold] [dim](查看 56 套模板及元数据)[/dim]")
    console.print("  [bold green][4][/bold green] 🤖 [bold]查看支持的 8 大平台矩阵[/bold] [dim](OpenAI/Claude/Gemini/Cursor/ZCode/dsh 等)[/dim]")
    console.print("  [bold green][5][/bold green] 💡 [bold]查询指定模板的实战需求预设 (Presets)[/bold]")
    console.print("  [bold green][6][/bold green] 🧪 [bold]运行全套自动化与完整性测试 (pytest)[/bold]")
    console.print("  [bold red][0][/bold red] 🚪 [dim]退出程序[/dim]\n")

    choice = Prompt.ask("请输入选项数字", choices=["1", "2", "3", "4", "5", "6", "0"], default="1")

    if choice == "1":
        start_web_server()
    elif choice == "2":
        run_interactive_wizard()
    elif choice == "3":
        run_cli_command(["list"])
    elif choice == "4":
        run_cli_command(["platforms"])
    elif choice == "5":
        query_presets_flow()
    elif choice == "6":
        run_tests()
    elif choice == "0":
        console.print("[yellow]感谢使用 PromptForge，再见！[/yellow]")
        sys.exit(0)


def start_web_server(port: int = 8000, host: str = "127.0.0.1", open_browser: bool = True):
    """启动 Web 服务"""
    from promptforge.web.app import run_server, find_available_port
    actual_port = find_available_port(host=host, start_port=port)
    console.print(f"\n[bold green]🚀 正在启动 PromptForge Web 工作台...[/bold green]")
    if actual_port != port:
        console.print(f"[yellow]⚠️ 默认端口 {port} 已被占用，已自动平滑切换至空闲端口！[/yellow]")
    console.print(f"本地访问地址: [bold cyan]http://{host}:{actual_port}[/bold cyan]")
    if open_browser:
        console.print("[dim]已自动为您在默认浏览器中打开页面...[/dim]")
    console.print("[dim]按 Ctrl + C 可安全停止服务。[/dim]\n")
    try:
        run_server(host=host, port=port, open_browser=open_browser)
    except KeyboardInterrupt:
        console.print("\n[yellow]Web 服务已安全关闭。[/yellow]")


def run_interactive_wizard():
    """交互式向导生成流程"""
    from promptforge.core.category import CATEGORIES
    from promptforge.core.engine import TemplateEngine
    from promptforge.adapters import ADAPTER_REGISTRY
    from promptforge.cli import app as cli_app

    engine = TemplateEngine()

    # 1. 选择分类
    cat_keys = list(CATEGORIES.keys())
    console.print("\n[bold cyan]步骤 1/4: 选择模板分类[/bold cyan]")
    for idx, (k, v) in enumerate(CATEGORIES.items(), 1):
        console.print(f"  [{idx}] {v.icon} [bold]{k}[/bold] ({v.display_name})")
    
    cat_idx = Prompt.ask("请选择分类序号", choices=[str(i) for i in range(1, len(cat_keys) + 1)], default="1")
    category = cat_keys[int(cat_idx) - 1]

    # 2. 选择模板
    tmpls = engine.category_manager.list_templates(category)
    if not tmpls:
        console.print(f"[red]分类 {category} 下未找到模板。[/red]")
        return

    console.print(f"\n[bold cyan]步骤 2/4: 选择分类 [{category}] 下的模板[/bold cyan]")
    for idx, t in enumerate(tmpls, 1):
        console.print(f"  [{idx}] [bold]{t.name}[/bold] ({t.display_name}) - [dim]{t.description}[/dim]")
    
    t_idx = Prompt.ask("请选择模板序号", choices=[str(i) for i in range(1, len(tmpls) + 1)], default="1")
    template_name = tmpls[int(t_idx) - 1].name

    # 3. 选择目标平台
    plat_keys = list(ADAPTER_REGISTRY.keys())
    console.print(f"\n[bold cyan]步骤 3/4: 选择目标输出平台[/bold cyan]")
    for idx, p in enumerate(plat_keys, 1):
        console.print(f"  [{idx}] [bold]{p}[/bold]")
    
    p_idx = Prompt.ask("请选择平台序号", choices=[str(i) for i in range(1, len(plat_keys) + 1)], default="1")
    platform = plat_keys[int(p_idx) - 1]

    # 4. 启动 CLI 交互式生成
    console.print(f"\n[bold green]✓ 进入变量填写与预设选择流程...[/bold green]")
    run_cli_command(["generate", "-c", category, "-t", template_name, "-p", platform, "-i"])


def query_presets_flow():
    """查询预设交互流程"""
    from promptforge.core.category import CATEGORIES
    from promptforge.core.engine import TemplateEngine

    engine = TemplateEngine()
    cat_keys = list(CATEGORIES.keys())
    console.print("\n[bold cyan]选择要查看预设的分类：[/bold cyan]")
    for idx, (k, v) in enumerate(CATEGORIES.items(), 1):
        console.print(f"  [{idx}] {v.icon} [bold]{k}[/bold] ({v.display_name})")
    
    cat_idx = Prompt.ask("分类序号", choices=[str(i) for i in range(1, len(cat_keys) + 1)], default="1")
    category = cat_keys[int(cat_idx) - 1]

    tmpls = engine.category_manager.list_templates(category)
    for idx, t in enumerate(tmpls, 1):
        console.print(f"  [{idx}] [bold]{t.name}[/bold] ({t.display_name})")
    t_idx = Prompt.ask("模板序号", choices=[str(i) for i in range(1, len(tmpls) + 1)], default="1")
    template_name = tmpls[int(t_idx) - 1].name

    run_cli_command(["presets", "-c", category, "-t", template_name])


def run_tests():
    """运行测试套件"""
    import subprocess
    console.print("\n[bold green]🧪 开始运行 pytest 测试套件...[/bold green]\n")
    try:
        res = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"], cwd=Path(__file__).parent)
        if res.returncode == 0:
            console.print("\n[bold green]✓ 全部测试通过！系统运行正常。[/bold green]")
        else:
            console.print(f"\n[bold red]存在失败的测试，退出代码: {res.returncode}[/bold red]")
    except Exception as e:
        console.print(f"[bold red]运行测试出错:[/bold red] {e}")


def run_cli_command(args: list):
    """透传参数调用 CLI 应用"""
    from promptforge.cli import app as cli_app
    try:
        cli_app(args)
    except SystemExit:
        pass


def main():
    """入口逻辑：如果有参数则直接作为 CLI 执行或处理子命令，无参数则打开交互式导航菜单"""
    if len(sys.argv) == 1:
        show_interactive_menu()
    else:
        cmd = sys.argv[1].lower()
        if cmd in ("web", "ui", "server"):
            port = 8000
            for i, arg in enumerate(sys.argv):
                if arg in ("--port", "-p") and i + 1 < len(sys.argv):
                    port = int(sys.argv[i + 1])
            start_web_server(port=port)
        elif cmd in ("test", "pytest"):
            run_tests()
        elif cmd in ("wizard", "guide"):
            run_interactive_wizard()
        else:
            # 透传参数调用 promptforge CLI
            run_cli_command(sys.argv[1:])


if __name__ == "__main__":
    main()
