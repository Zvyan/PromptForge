"""
测试所有平台适配器的导出格式与文件写入。
"""
import json
from pathlib import Path
from promptforge.adapters import (
    ADAPTER_REGISTRY,
    OpenAIAdapter,
    ClaudeAdapter,
    GeminiAdapter,
    CursorAdapter,
    WindsurfAdapter,
    ZCodeAdapter,
    MarkdownAdapter,
)


def test_adapter_registry():
    """测试所有平台已全部注册"""
    expected_platforms = ["openai", "claude", "gemini", "cursor", "windsurf", "zcode", "markdown"]
    for p in expected_platforms:
        assert p in ADAPTER_REGISTRY, f"平台 {p} 未注册在 ADAPTER_REGISTRY 中"


def test_openai_adapter_export(sample_prompt_output):
    """测试 OpenAI JSON 消息结构导出"""
    adapter = OpenAIAdapter()
    result = adapter.export(sample_prompt_output)
    data = json.loads(result)

    assert "messages" in data
    assert len(data["messages"]) == 2
    assert data["messages"][0]["role"] == "system"
    assert data["messages"][1]["role"] == "user"


def test_claude_adapter_export(sample_prompt_output):
    """测试 Claude 顶层系统参数输出"""
    adapter = ClaudeAdapter()
    result = adapter.export(sample_prompt_output)
    data = json.loads(result)

    assert "system" in data
    assert "messages" in data
    assert len(data["messages"]) == 1
    assert data["messages"][0]["role"] == "user"


def test_gemini_adapter_export(sample_prompt_output):
    """测试 Gemini 平台 systemInstruction 与 contents 格式"""
    adapter = GeminiAdapter()
    result = adapter.export(sample_prompt_output)
    data = json.loads(result)

    assert "systemInstruction" in data
    assert "contents" in data
    assert "parts" in data["systemInstruction"]


def test_cursor_and_windsurf_adapter(sample_prompt_output, tmp_path):
    """测试 Cursor 和 Windsurf 规则文件导出"""
    cursor_adapter = CursorAdapter()
    cursor_text = cursor_adapter.export(sample_prompt_output)
    assert "Python" in cursor_text

    cursor_file = tmp_path / ".cursorrules"
    cursor_adapter.export_to_file(sample_prompt_output, cursor_file)
    assert cursor_file.exists()

    windsurf_adapter = WindsurfAdapter()
    windsurf_file = tmp_path / ".windsurfrules"
    windsurf_adapter.export_to_file(sample_prompt_output, windsurf_file)
    assert windsurf_file.exists()


def test_zcode_adapter(sample_prompt_output, tmp_path):
    """测试 ZCode (智谱 GLM Agent) 适配器人设与配置导出"""
    adapter = ZCodeAdapter()
    text = adapter.export(sample_prompt_output)
    assert "GLM 智能体人设配置" in text
    assert "角色定位与设定" in text
    assert "代码解释器" in text

    # 测试文件写入
    target_file = tmp_path / "glm_agent_config.md"
    adapter.export_to_file(sample_prompt_output, target_file)
    assert target_file.exists()
    assert "GLM 智能体人设配置" in target_file.read_text(encoding="utf-8")

    # 测试 GLM Agent JSON 配置导出
    config_json = adapter.to_zcode_config(sample_prompt_output)
    config_data = json.loads(config_json)
    assert config_data["model"] == "glm-4-plus"
    assert "messages" in config_data
    assert "tools" in config_data
    assert any(t.get("type") == "code_interpreter" for t in config_data["tools"])


def test_markdown_adapter(sample_prompt_output):
    """测试通用 Markdown 导出"""
    adapter = MarkdownAdapter()
    text = adapter.export(sample_prompt_output)
    assert "## System Prompt" in text
    assert "## User Prompt" in text


def test_deepseek_harness_adapter(sample_prompt_output, tmp_path):
    """测试 DeepSeek Harness (dsh) 适配器 YAML 预设与文件导出"""
    from promptforge.adapters.deepseek_harness_adapter import DeepSeekHarnessAdapter
    import yaml

    adapter = DeepSeekHarnessAdapter()
    yaml_text = adapter.export(sample_prompt_output)
    assert "DeepSeek Harness (dsh)" in yaml_text
    
    # 验证导出的 YAML 结构合法性
    data = yaml.safe_load(yaml_text)
    assert data["version"] == "1.0"
    assert data["agent"]["name"] == "code_review"
    assert "persona" in data
    assert "runtime" in data
    assert any(p["name"] == "@dsh/plugin-model-deepseek" for p in data["runtime"]["plugins"])

    # 测试文件写入
    target_file = tmp_path / "dsh_agent.yaml"
    adapter.export_to_file(sample_prompt_output, target_file)
    assert target_file.exists()
    assert "DeepSeek Harness" in target_file.read_text(encoding="utf-8")

    # 测试 DeepSeek 专属 Markdown 提示词导出
    prompt_text = adapter.to_deepseek_prompt(sample_prompt_output)
    assert "DeepSeek Agent Specification" in prompt_text
    assert "System Instructions" in prompt_text
