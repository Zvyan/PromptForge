"""
测试 PromptForge CLI 命令行交互。
"""
from pathlib import Path
from typer.testing import CliRunner
from promptforge.cli import app

runner = CliRunner()


def test_cli_list():
    """测试 promptforge list 列出分类汇总"""
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "PromptForge 模板分类一览" in result.output or "coding" in result.output


def test_cli_list_category():
    """测试 promptforge list -c coding 列出分类详情"""
    result = runner.invoke(app, ["list", "-c", "coding"])
    assert result.exit_code == 0
    assert "code_review" in result.output
    assert "bug_fix" in result.output


def test_cli_platforms():
    """测试 promptforge platforms 显示支持平台"""
    result = runner.invoke(app, ["platforms"])
    assert result.exit_code == 0
    assert "openai" in result.output
    assert "zcode" in result.output
    assert "claude" in result.output


def test_cli_generate():
    """测试 promptforge generate 指定参数生成提示词"""
    result = runner.invoke(
        app,
        [
            "generate",
            "-c", "coding",
            "-t", "code_review",
            "-p", "zcode",
            "-v", "language=Python",
            "-v", "strictness=standard",
            "-v", "code_content=x = 1",
        ],
    )
    assert result.exit_code == 0
    assert "GLM 智能体人设配置" in result.output or "Python" in result.output


def test_cli_export(tmp_path):
    """测试 promptforge export 导出文件"""
    out_file = tmp_path / ".zcoderules"
    result = runner.invoke(
        app,
        [
            "export",
            "-c", "coding",
            "-t", "code_review",
            "-p", "zcode",
            "-v", "language=Go",
            "-v", "strictness=strict",
            "-v", "code_content=package main",
            "-o", str(out_file),
        ],
    )
    assert result.exit_code == 0
    assert out_file.exists()
    assert "Go" in out_file.read_text(encoding="utf-8")


def test_cli_validate(tmp_path):
    """测试 promptforge validate 校验文件"""
    test_file = tmp_path / "prompt.txt"
    test_file.write_text("你是一个资深架构师，请协助编写测试用例。", encoding="utf-8")

    result = runner.invoke(app, ["validate", str(test_file), "-p", "openai"])
    assert result.exit_code == 0
    assert "提示词校验报告" in result.output or "验证通过" in result.output


def test_cli_presets():
    """测试 promptforge presets 列出内置场景预设"""
    result = runner.invoke(app, ["presets", "-c", "coding", "-t", "code_review"])
    assert result.exit_code == 0
    assert "内置需求预设" in result.output
    assert "concurrency_inventory" in result.output


def test_cli_generate_with_preset():
    """测试 promptforge generate --preset 一键选用预设生成"""
    result = runner.invoke(
        app,
        [
            "generate",
            "-c", "coding",
            "-t", "code_review",
            "-p", "zcode",
            "--preset", "1",
        ],
    )
    assert result.exit_code == 0
    assert "已加载预设场景" in result.output
    assert "scores" in result.output or "deduct_stock" in result.output

