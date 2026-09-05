"""
测试 PromptForge Web UI API 路由。
"""
from fastapi.testclient import TestClient
from promptforge.web.app import create_app

client = TestClient(create_app())


def test_web_index():
    """测试 Web 首页加载"""
    response = client.get("/")
    assert response.status_code == 200
    assert "PromptForge" in response.text
    assert "编程开发" in response.text


def test_web_category_page():
    """测试分类模板列表页"""
    response = client.get("/templates/coding")
    assert response.status_code == 200
    assert "代码审查" in response.text


def test_web_template_detail_page():
    """测试模板详情页面"""
    response = client.get("/template/coding/code_review")
    assert response.status_code == 200
    assert "目标平台" in response.text
    assert "严格程度" in response.text


def test_api_categories():
    """测试 /api/categories 接口"""
    response = client.get("/api/categories")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 6
    names = [c["name"] for c in data]
    assert "coding" in names
    assert "analysis" in names


def test_api_platforms():
    """测试 /api/platforms 接口"""
    response = client.get("/api/platforms")
    assert response.status_code == 200
    data = response.json()
    assert "openai" in data
    assert "zcode" in data
    assert "claude" in data


def test_api_generate_success():
    """测试 /api/generate 接口渲染并返回格式化结果"""
    payload = {
        "category": "coding",
        "template": "code_review",
        "platform": "zcode",
        "variables": {
            "language": "Python",
            "focus_areas": ["readability"],
            "strictness": "standard",
            "code_content": "def hello(): print('world')",
        },
        "lang": "zh",
    }
    response = client.post("/api/generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["template_name"] == "code_review"
    assert data["platform"] == "zcode"
    assert data["token_estimate"] > 0
    assert "GLM 智能体人设配置" in data["formatted_content"]
    assert data["validation"]["is_valid"] is True
