"""
pytest 共享测试 fixtures。
"""
import sys
from pathlib import Path
import pytest

# 确保 src 目录在 sys.path 中
SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from promptforge.models.template import Template
from promptforge.models.prompt import PromptOutput, PromptSection, PromptRole
from promptforge.core.engine import TemplateEngine


@pytest.fixture
def project_root() -> Path:
    return Path(__file__).resolve().parent.parent


@pytest.fixture
def templates_dir(project_root) -> Path:
    return project_root / "templates"


@pytest.fixture
def engine(templates_dir) -> TemplateEngine:
    return TemplateEngine(templates_dir=templates_dir)


@pytest.fixture
def sample_variables() -> dict:
    return {
        "language": "Python",
        "focus_areas": ["readability", "security"],
        "strictness": "strict",
        "code_content": "def add(a, b):\n    return a + b\n",
    }


@pytest.fixture
def sample_template(engine) -> Template:
    return engine.load_template("coding", "code_review")


@pytest.fixture
def sample_prompt_output() -> PromptOutput:
    return PromptOutput(
        template_name="code_review",
        category="coding",
        platform="openai",
        sections=[
            PromptSection(role=PromptRole.SYSTEM, content="你是一位资深的 Python 架构师。"),
            PromptSection(role=PromptRole.USER, content="请审查以下代码:\ndef add(a, b): return a + b"),
        ],
        metadata={"display_name": "代码审查", "version": "1.0.0"},
        token_estimate=120,
        raw_text="你是一位资深的 Python 架构师。\n\n请审查以下代码:\ndef add(a, b): return a + b",
    )
