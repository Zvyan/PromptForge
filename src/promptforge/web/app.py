"""
PromptForge Web 应用程序。
基于 FastAPI 和 Jinja2 提供可视化模板浏览、交互生成与实时校验。
"""
from pathlib import Path
from typing import Any, Dict, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from promptforge.adapters import ADAPTER_REGISTRY
from promptforge.core.category import CategoryManager, CATEGORIES
from promptforge.core.engine import TemplateEngine, EngineError
from promptforge.core.resolver import VariableResolver, ResolverError
from promptforge.core.validator import PromptValidator

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"


class GenerateRequest(BaseModel):
    category: str
    template: str
    platform: str = "openai"
    variables: Dict[str, Any] = {}
    lang: str = "zh"


def create_app() -> FastAPI:
    """FastAPI 应用工厂函数"""
    app = FastAPI(
        title="PromptForge",
        description="多平台 Agent 提示词生成与管理系统",
        version="0.1.0",
    )

    # 挂载静态文件目录
    STATIC_DIR.mkdir(parents=True, exist_ok=True)
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    # 配置 HTML 模板目录
    templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
    engine = TemplateEngine()
    resolver = VariableResolver()
    validator = PromptValidator()

    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request):
        """首页：展示六大分类与概况"""
        categories = engine.category_manager.list_categories()
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "categories": categories,
                "platforms": list(ADAPTER_REGISTRY.keys()),
            },
        )

    @app.get("/templates/{category}", response_class=HTMLResponse)
    async def list_category_templates(request: Request, category: str):
        """分类页：展示某分类下的所有模板"""
        cat_info = engine.category_manager.get_category(category)
        if not cat_info:
            raise HTTPException(status_code=404, detail=f"未找到分类: {category}")
        
        tmpl_list = engine.category_manager.list_templates(category)
        return templates.TemplateResponse(
            request=request,
            name="category.html",
            context={
                "category": cat_info,
                "templates": tmpl_list,
                "all_categories": engine.category_manager.list_categories(),
            },
        )

    @app.get("/template/{category}/{name}", response_class=HTMLResponse)
    async def template_detail(request: Request, category: str, name: str):
        """模板详情页：动态输入变量、选择平台并生成提示词"""
        try:
            tmpl = engine.load_template(category, name)
        except EngineError:
            raise HTTPException(status_code=404, detail=f"未找到模板: {category}/{name}")

        cat_info = engine.category_manager.get_category(category)
        return templates.TemplateResponse(
            request=request,
            name="template_detail.html",
            context={
                "template": tmpl,
                "category": cat_info,
                "platforms": list(ADAPTER_REGISTRY.keys()),
                "all_categories": engine.category_manager.list_categories(),
            },
        )

    # ------------------ REST API ------------------

    @app.get("/api/categories")
    async def api_categories():
        """获取所有分类信息"""
        return engine.category_manager.list_categories()

    @app.get("/api/platforms")
    async def api_platforms():
        """获取所有支持平台信息"""
        result = {}
        for name, cls_ in ADAPTER_REGISTRY.items():
            adapter = cls_()
            result[name] = adapter.get_platform_info()
        return result

    @app.get("/api/templates/{category}")
    async def api_templates(category: str):
        """获取指定分类下的模板列表"""
        return engine.category_manager.list_templates(category)

    @app.get("/api/template/{category}/{name}")
    async def api_template_detail(category: str, name: str):
        """获取单个模板结构定义"""
        try:
            tmpl = engine.load_template(category, name)
            return tmpl.model_dump()
        except EngineError as e:
            raise HTTPException(status_code=404, detail=str(e))

    @app.post("/api/generate")
    async def api_generate(req: GenerateRequest):
        """根据输入渲染提示词并返回各平台格式化结果与校验数据"""
        if req.platform not in ADAPTER_REGISTRY:
            raise HTTPException(status_code=400, detail=f"不支持的平台: {req.platform}")

        try:
            tmpl = engine.load_template(req.category, req.template)
            resolved_vars = resolver.resolve(tmpl, req.variables)
            prompt_output = engine.render(
                tmpl, resolved_vars, platform=req.platform, lang=req.lang
            )
        except (EngineError, ResolverError) as e:
            raise HTTPException(status_code=400, detail=str(e))

        adapter = ADAPTER_REGISTRY[req.platform]()
        formatted = adapter.export(prompt_output)
        val_result = validator.validate(prompt_output, platform=req.platform)

        return {
            "template_name": prompt_output.template_name,
            "category": prompt_output.category,
            "platform": prompt_output.platform,
            "token_estimate": prompt_output.token_estimate,
            "raw_text": prompt_output.raw_text,
            "formatted_content": formatted,
            "output_format": adapter.output_format,
            "validation": val_result.model_dump(),
        }

    return app


def find_available_port(host: str = "127.0.0.1", start_port: int = 8000, max_attempts: int = 20) -> int:
    """自动检测可用端口，若被占用则平滑切换"""
    import socket
    for p in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((host, p))
                return p
            except OSError:
                continue
    return start_port


def run_server(host: str = "127.0.0.1", port: int = 8000, reload: bool = False, open_browser: bool = False):
    """启动 Web 服务（支持智能端口冲突自愈与平滑切换）"""
    import uvicorn
    import webbrowser
    import threading

    actual_port = find_available_port(host=host, start_port=port)
    if actual_port != port:
        print(f"\n⚠️ 提示: 默认端口 {port} 已被占用，已自动切换至空闲端口: http://{host}:{actual_port}\n")

    if open_browser:
        def _open():
            import time
            time.sleep(1.0)
            try:
                webbrowser.open(f"http://{host}:{actual_port}")
            except Exception:
                pass
        threading.Thread(target=_open, daemon=True).start()

    app = create_app()
    uvicorn.run(app, host=host, port=actual_port, reload=reload)


if __name__ == "__main__":
    run_server(open_browser=True)
