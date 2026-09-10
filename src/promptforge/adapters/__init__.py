from typing import Dict, Type

from promptforge.adapters.base import BaseAdapter
from promptforge.adapters.openai_adapter import OpenAIAdapter
from promptforge.adapters.claude_adapter import ClaudeAdapter
from promptforge.adapters.gemini_adapter import GeminiAdapter
from promptforge.adapters.cursor_adapter import CursorAdapter, WindsurfAdapter
from promptforge.adapters.markdown_adapter import MarkdownAdapter
from promptforge.adapters.zcode_adapter import ZCodeAdapter
from promptforge.adapters.deepseek_harness_adapter import DeepSeekHarnessAdapter
from promptforge.adapters.kimi_adapter import KimiAdapter

# 导出所有的适配器类
__all__ = [
    'BaseAdapter',
    'OpenAIAdapter',
    'ClaudeAdapter',
    'GeminiAdapter',
    'CursorAdapter',
    'WindsurfAdapter',
    'MarkdownAdapter',
    'ZCodeAdapter',
    'DeepSeekHarnessAdapter',
    'KimiAdapter',
    'ADAPTER_REGISTRY'
]

# 注册所有支持的平台适配器
ADAPTER_REGISTRY: Dict[str, Type[BaseAdapter]] = {
    'openai': OpenAIAdapter,
    'claude': ClaudeAdapter,
    'gemini': GeminiAdapter,
    'cursor': CursorAdapter,
    'windsurf': WindsurfAdapter,
    'markdown': MarkdownAdapter,
    'zcode': ZCodeAdapter,
    'kimi': KimiAdapter,
    'moonshot': KimiAdapter,
    'deepseek_harness': DeepSeekHarnessAdapter,
    'dsh': DeepSeekHarnessAdapter,
    'deepseek': DeepSeekHarnessAdapter,
}
