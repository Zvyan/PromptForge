"""
提示词验证器模块，用于检查令牌限制、语法和安全性。
"""
import re
import tiktoken
from typing import Optional, List
from promptforge.models.prompt import PromptOutput, ValidationResult

class PromptValidator:
    """验证生成的提示词输出。"""
    
    TOKEN_LIMITS = {
        "openai": 128000,
        "claude": 200000,
        "gemini": 1000000,
        "cursor": 32000,
        "windsurf": 32000,
        "zcode": 128000,
        "deepseek_harness": 128000,
        "deepseek": 128000,
        "dsh": 128000,
    }
    
    def validate(self, prompt: PromptOutput, platform: Optional[str] = None) -> ValidationResult:
        """
        验证提示词的各个方面：空章节、未解析变量、注入风险、令牌限制等。
        
        Args:
            prompt: 生成的提示词输出
            platform: 目标平台（覆盖prompt自带的平台）
            
        Returns:
            验证结果对象
        """
        platform = platform or prompt.platform
        is_valid = True
        errors = []
        warnings = []
        
        total_tokens = 0
        has_system = False
        has_user = False
        
        for section in prompt.sections:
            content = section.content.strip()
            
            # 检查空章节
            if not content:
                errors.append(f"章节 {section.role} 内容为空")
                is_valid = False
                continue
                
            if section.role == "system":
                has_system = True
            elif section.role == "user":
                has_user = True
                
            # 检查未解析的 Jinja2 变量
            if re.search(r'\{\{.*?\}\}', content):
                errors.append(f"章节 {section.role} 包含未解析的变量")
                is_valid = False
                
            # 检查潜在的提示词注入风险
            injection_patterns = [
                r'(?i)ignore previous instructions',
                r'(?i)disregard previous instructions',
                r'(?i)system prompt',
                r'(?i)you are now'
            ]
            for pattern in injection_patterns:
                if re.search(pattern, content):
                    warnings.append(f"章节 {section.role} 可能包含提示词注入模式")
                    
            total_tokens += self.estimate_tokens(content)
            
        # 令牌限制检查
        limit = self.TOKEN_LIMITS.get(platform, 8000)
        if total_tokens > limit:
            errors.append(f"提示词超出 {platform} 的令牌限制: {total_tokens} > {limit}")
            is_valid = False
        elif total_tokens > limit * 0.8:
            warnings.append(f"提示词接近 {platform} 的令牌限制: {total_tokens} / {limit}")
            
        # 平台特定要求检查
        if platform == "claude" and not has_user:
            warnings.append(f"Claude 平台通常需要 user 角色")
            
        result = ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            suggestions=[],
            token_count=total_tokens,
        )
        
        # 如果可以改进，添加建议
        if warnings or total_tokens > limit * 0.8:
            result.suggestions = ["考虑精简提示词以减少令牌使用量"]
            if warnings:
                result.suggestions.append("审查警告中提到的潜在注入风险")
                
        return result

    def estimate_tokens(self, text: str) -> int:
        """
        使用 tiktoken (cl100k_base encoding) 估算文本的令牌数量。
        
        Args:
            text: 输入文本
            
        Returns:
            令牌数量估算值
        """
        try:
            encoding = tiktoken.get_encoding("cl100k_base")
            return len(encoding.encode(text, disallowed_special=()))
        except Exception:
            # 回退到简单的字符级估算
            return len(text) // 4
