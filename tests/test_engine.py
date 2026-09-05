"""
测试 TemplateEngine 模板加载、渲染与多语言支持。
"""
from pathlib import Path
import pytest
from promptforge.core.engine import TemplateEngine, EngineError
from promptforge.models.template import Template


def test_load_template_success(engine):
    """测试正常加载内置模板"""
    tmpl = engine.load_template("coding", "code_review")
    assert tmpl is not None
    assert tmpl.meta.name == "code_review"
    assert tmpl.meta.category == "coding"
    assert "language" in tmpl.variables
    assert "code_content" in tmpl.variables


def test_load_template_not_found(engine):
    """测试加载不存在的模板抛出 EngineError"""
    with pytest.raises(EngineError):
        engine.load_template("coding", "non_existent_template")


def test_render_template_chinese(engine, sample_template, sample_variables):
    """测试中文模板渲染"""
    output = engine.render(sample_template, sample_variables, platform="openai", lang="zh")
    assert output is not None
    assert output.platform == "openai"
    assert len(output.sections) >= 2
    assert output.token_estimate > 0

    # 检查变量是否被正确渲染替换
    system_sec = next(s for s in output.sections if s.role.value == "system")
    assert "Python" in system_sec.content
    assert "readability" in system_sec.content
    assert "def add(a, b)" in output.raw_text


def test_render_template_english(engine, sample_template, sample_variables):
    """测试英文版模板渲染 (sections_en)"""
    output = engine.render(sample_template, sample_variables, platform="openai", lang="en")
    assert output is not None
    assert output.metadata.get("lang") == "en"
    system_sec = next(s for s in output.sections if s.role.value == "system")
    # 英文版专属文本
    assert "senior Python staff engineer" in system_sec.content or "Please formulate" in system_sec.content


def test_list_templates(engine):
    """测试列举所有分类下的模板"""
    all_tmpls = engine.list_templates()
    assert len(all_tmpls) >= 56  # 9 大分类共 56 套模板

    coding_tmpls = engine.list_templates("coding")
    assert len(coding_tmpls) >= 9
    names = [t.name for t in coding_tmpls]
    assert "code_review" in names
    assert "bug_fix" in names

    presentation_tmpls = engine.list_templates("presentation")
    assert len(presentation_tmpls) == 6
    p_names = [t.name for t in presentation_tmpls]
    assert "ppt_outline" in p_names
    assert "marp_generator" in p_names
    assert "pitch_deck" in p_names


def test_load_and_render_presentation_template(engine):
    """测试演示类模板加载与渲染"""
    tmpl = engine.load_template("presentation", "ppt_outline")
    assert tmpl.meta.name == "ppt_outline"
    assert "topic" in tmpl.variables

    rendered = engine.render(
        tmpl,
        {"topic": "云原生微服务重构", "audience": "企业技术架构师"},
        platform="zcode"
    )
    assert "云原生微服务重构" in rendered.raw_text
    assert rendered.platform == "zcode"



def test_custom_templates_override(tmp_path, sample_variables):
    """测试用户自定义模板覆盖同名内置模板"""
    custom_dir = tmp_path / "custom"
    coding_dir = custom_dir / "coding"
    coding_dir.mkdir(parents=True)

    # 创建一个覆盖 code_review 的自定义模板
    custom_yaml = """
meta:
  name: "code_review"
  display_name: "自定义代码审查"
  category: "coding"
  description: "用户自定义的代码审查规则"
  tags: ["custom"]
  version: "2.0.0"
  platforms: ["openai"]

variables:
  language:
    type: string
    required: true
    description: "语言"
  code_content:
    type: string
    required: true
    description: "代码"

sections:
  system:
    role: "【自定义角色】{{ language }} 审查专家"
    instructions: "严格审查所有代码风格"
  user: "请检查：{{ code_content }}"
"""
    (coding_dir / "code_review.yaml").write_text(custom_yaml, encoding="utf-8")

    custom_engine = TemplateEngine(custom_templates_dir=custom_dir)
    loaded = custom_engine.load_template("coding", "code_review")
    assert loaded.meta.version == "2.0.0"
    assert loaded.meta.display_name == "自定义代码审查"

    rendered = custom_engine.render(loaded, {"language": "Rust", "code_content": "fn main() {}"})
    assert "【自定义角色】Rust 审查专家" in rendered.raw_text


def test_get_adapter(engine):
    """测试适配器获取与异常"""
    adapter = engine.get_adapter("zcode")
    assert adapter.platform_name == "zcode"

    with pytest.raises(EngineError):
        engine.get_adapter("unsupported_platform_xyz")


def test_all_templates_integrity(engine):
    """遍历检查所有 9 大分类下所有模板的完整性与格式合法性"""
    all_templates = engine.list_templates()
    assert len(all_templates) >= 56

    for meta in all_templates:
        tmpl = engine.load_template(meta.category, meta.name)
        assert tmpl.meta.name == meta.name
        assert tmpl.meta.category == meta.category
        assert tmpl.meta.display_name
        assert tmpl.meta.description
        assert tmpl.sections.system is not None or tmpl.sections.user is not None
        for v_name, v_def in tmpl.variables.items():
            assert v_def.type is not None
            assert v_def.description


def test_resolver_preset_lookup(engine):
    """测试变量解析器的预设场景匹配逻辑"""
    from promptforge.core.resolver import VariableResolver
    resolver = VariableResolver()
    tmpl = engine.load_template("presentation", "pitch_deck")
    assert len(tmpl.presets) >= 2

    # 按 1-based index 查找
    p1 = resolver.find_preset(tmpl, "1")
    assert p1 is not None
    assert p1.id == "agent_infra_seed"

    # 按 id 查找
    p_id = resolver.find_preset(tmpl, "agent_infra_seed")
    assert p_id is not None
    assert p_id.id == "agent_infra_seed"

    # 按标题关键词查找
    p_title = resolver.find_preset(tmpl, "物联网")
    assert p_title is not None
    assert p_title.id == "industrial_iot_series_a"


def test_all_presets_rendering_and_validation(engine):
    """测试全库所有模板的所有预设均能无损解析、严格匹配枚举并通过渲染校验"""
    all_templates = engine.list_templates()
    total_presets = 0

    for meta in all_templates:
        tmpl = engine.load_template(meta.category, meta.name)
        assert len(tmpl.presets) >= 1, f"Template {meta.category}/{meta.name} must have at least 1 preset"
        for preset in tmpl.presets:
            total_presets += 1
            # 校验预设变量中的 enum 选项有效性
            for var_name, var_val in preset.variables.items():
                if var_name in tmpl.variables:
                    v_def = tmpl.variables[var_name]
                    if v_def.type.value == "enum":
                        assert var_val in v_def.options, (
                            f"{meta.category}/{meta.name} preset '{preset.id}' var '{var_name}'="
                            f"'{var_val}' not in allowed options: {v_def.options}"
                        )
            # 确保实际渲染完全无报错
            output = engine.render(tmpl, preset.variables, platform="openai")
            assert output.raw_text
            assert output.token_estimate > 0

    assert total_presets >= 80



