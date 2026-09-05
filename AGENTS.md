# PromptForge - Codex 集成指南

## 什么是 PromptForge？

PromptForge 是一个跨平台的 Agent 提示词生成框架。它的目的是将复杂的、重复使用的提示词模板化，支持多平台（OpenAI、Anthropic 等）快速切换与渲染，并保证生成结果结构的正确性。通过将指令、上下文、工具和用户变量分层，能够极大地提升系统和 Agent 交互的灵活性。

## 命令行工具支持的指令

- `promptforge --help`: 显示帮助信息。
- `promptforge validate <template-path>`: 校验指定的 YAML 模板文件格式是否正确。
- `promptforge render <template-path> [options]`: 利用传入变量渲染并生成最终的 Prompt 文本或数据对象。
- `promptforge list [category]`: 列出当前可用的提示词模板。

## Codex 使用示例

假设你需要为 Codex 生成一个关于代码审查任务的 prompt，你可以利用 PromptForge 加载 `code_reviewer.yaml`：

```bash
# 验证代码审查模板
promptforge validate templates/code_reviewer.yaml

# 生成提供给 Codex 的 Prompt
promptforge render templates/code_reviewer.yaml \
    --var language="Python" \
    --var strict_mode=true \
    --platform openai
```

## 模板格式说明

PromptForge 的模板文件（YAML格式）要求包含三个基本部分：
1. `meta`：包含名称、版本及目标平台。
2. `variables`：定义所有必需或可选的变量，如类型、默认值及说明。
3. `sections`：由 `system`（系统设定，如角色、指令、限制等）和 `user`（最终拼接给用户的文本格式）组成，用于生成带有标记符号（如 Jinja2 或特定结构标记）的高级 Prompt 结构。
