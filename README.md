# PromptForge — 多平台 Agent 规范提示词生成框架

<p align="center">
  <a href="README_EN.md">English</a> | <b>中文</b>
</p>

PromptForge 是一个专为各类 AI Agent 平台量身打造的结构化提示词生成与管理框架，提供分类清晰、可复用、动态类型校验的模板系统，并支持通过 CLI、Web UI 与 OpenAI Codex 终端直接调用。

---

## 🌟 主要特性

- **九大场景分类**：内置 `coding`（编程开发）、`analysis`（数据与架构分析）、`writing`（工程写作与设计）、`tool_use`（工具调用与智能体）、`conversation`（交互式推理）、`system`（系统规则）、`productivity`（日常与办公）、`academic`（学术与科研）、`presentation`（演示与汇报）共 **56 套工程级专业模板**。
- **九大平台深度适配**：针对 OpenAI/Codex、Claude、Gemini、Cursor、Windsurf、通用 Markdown、**ZCode (智谱清言 GLM 智能体平台 / CodeGeeX)**、**DeepSeek Harness (dsh / Cordis 微内核架构)** 以及 **Kimi (Moonshot AI / 月之暗面)** 提供量身定制的格式化与能力配置。
- **双模态操作界面**：
  - **CLI 命令行**：交互式引导输入、一键生成、规则导出、Token 校验与合规性检查。
  - **Web 可视化界面**：基于 FastAPI + 响应式前端，支持分类检索、动态表单、实时 Token 统计、一键复制与文件下载。
- **中英双语输出**：原生支持中文 (`--lang zh`) 与英文 (`--lang en`) 提示词一键切换。
- **优先级继承机制**：支持在 `custom_templates/` 目录自定义模板，同名配置自动无缝覆盖内置模板。
- **Codex CLI 深度协同**：通过内置 `AGENTS.md` 指令规范，在 Codex 终端内通过自然语言即可完成规则配置。

---

## 🤖 平台支持矩阵

| 平台标识 | 适配对象 | 导出格式 | 核心能力支持 |
| :--- | :--- | :--- | :--- |
| `openai` | OpenAI API / Codex CLI | JSON / `AGENTS.md` | Messages 消息流、Function Calling 严格 JSON Schema、Codex 项目指令 |
| `claude` | Anthropic Claude API | JSON / Custom Instructions | 独立的顶层 `system` 字段、Tool Use `input_schema`、Claude Projects 规范 |
| `gemini` | Google Gemini API | JSON | `systemInstruction` 结构、`contents`（用户/模型轮次）、`functionDeclarations` |
| `cursor` | Cursor IDE 智能体 | Markdown (`.cursorrules`) | 平铺角色设定、编码准则与约束，适配 Composer 与 Agent 索引 |
| `windsurf` | Windsurf 编辑器 | Markdown (`.windsurfrules`) | 适配 Codeium Cascade 记忆引擎 |
| `zcode` | **智谱 GLM 智能体平台** / CodeGeeX | Markdown / JSON | 智谱清言智能体人设提示词、GLM-4 API 请求体、原生代码解释器与网页检索插件 |
| `kimi` (`moonshot`) | **Kimi (Moonshot AI / 月之暗面)** | Markdown / JSON | 128k~200k 超长上下文优化、Prompt Caching（前缀缓存友好的静态锚点设计）、Moonshot API 报文兼容、联网检索与长文档解析 |
| `deepseek_harness` (`dsh`) | **DeepSeek Harness 智能体框架** | YAML / Markdown | 基于 Cordis 微内核架构的智能体预设 (Preset)、V3/R1 人设规则、文件/终端沙箱插件配置 |
| `markdown` | 通用对话环境 | Markdown | 模块化结构，适合复制到任何 Web 对话界面 |

---

## 📦 安装与快速开始

### 1. 本地安装
```bash
git clone <repository-url> promptforge
cd promptforge
pip install -e .
```

### 2. CLI 命令行使用

```bash
# 1. 浏览所有分类及模板
promptforge list
promptforge list -c coding

# 2. 查看支持的 8 大平台特性与 Token 上限
promptforge platforms

# 3. 查看某模板内置的实战需求预设 (Presets)
promptforge presets -c coding -t code_review
promptforge presets -c presentation -t pitch_deck

# 4. 一键选用预设场景生成提示词（免手动输入长文本）
promptforge generate -c coding -t code_review --preset 1 -p zcode
promptforge generate -c presentation -t pitch_deck --preset agent_infra_seed -p deepseek_harness

# 5. 自定义参数覆盖预设中的部分变量
promptforge generate -c coding -t code_review --preset 1 -v language=Go

# 6. 导出为智谱 GLM Agent 开放平台 JSON 配置文件
promptforge export -c coding -t code_review --preset 1 -p zcode -o glm_agent_config.json

# 7. 交互式模式（支持友好的预设选择菜单引导）
promptforge generate -c coding -t bug_fix -p claude -i

# 8. 校验提示词文件的合规性与 Token 消耗
promptforge validate glm_agent_config.json -p zcode
```

### 3. 多种便捷启动方式 (Web UI & 启动器)

PromptForge 提供了针对不同操作习惯的专属启动程序：

#### 方式一：Windows 一键双击启动 (最推荐)
直接在项目根目录下双击运行：
* **`start_web.bat`**：一键拉起 Web 可视化工作台并自动唤起默认浏览器打开 `http://127.0.0.1:8000`。
* **`run.bat`**：一键进入控制台全交互式仪表盘向导。
*(Linux / macOS 用户可执行 `./start_web.sh`)*

#### 方式二：统一多功能启动器
在项目根目录下运行：
```bash
# 无参数启动：弹出控制台交互式导航仪表盘（支持 Web启动、向导生成、测试执行等）
python run.py

# 直接一键启动 Web 工作台并打开浏览器
python run.py web

# 指定端口启动
python run.py web --port 8888
```

#### 方式三：全局命令行启动
若已完成本地 pip 安装，可在系统任意终端直接运行：
```bash
# 自动打开浏览器启动 Web 界面
promptforge-ui

# 或通过主 CLI 命令启动
promptforge web --port 8000
```

---

## 📁 模板编写规范

模板位于 `templates/<category>/<template_name>.yaml`，标准格式如下：

```yaml
meta:
  name: "code_review"
  display_name: "代码审查"
  category: "coding"
  description: "全方位代码审查模板"
  tags: ["code-review", "quality"]
  version: "1.0.0"
  platforms: ["openai", "claude", "gemini", "cursor", "zcode"]

variables:
  language:
    type: string
    required: true
    description: "编程语言"
  strictness:
    type: enum
    required: true
    default: "standard"
    options: ["lenient", "standard", "strict"]
    description: "严格程度"
  code_content:
    type: string
    required: true
    description: "需要审查的代码"

sections:
  system:
    role: "你是一个资深的 {{ language }} 专家级工程师。"
    instructions: "对提供的代码进行深入审查，尺度为 {{ strictness }}。"
    output_format: "1. 总体评价\n2. 问题列表\n3. 优化建议"
    constraints: "- 建议必须具体可执行\n- 给出优化代码对比"
  user: |
    请审查以下 {{ language }} 代码：
    ```{{ language }}
    {{ code_content }}
    ```

# 可选：英文版本支持
sections_en:
  system:
    role: "You are a senior {{ language }} staff engineer."
    instructions: "Conduct a thorough code review."
  user: "Please review the following {{ language }} code:\n```{{ language }}\n{{ code_content }}\n```"
```

---

## 📊 效能验证与基准测试（普通对话 vs PromptForge）

我们基于行业标准 `tiktoken`（`cl100k_base`）在真实场景下进行了量化对比测试（运行 `python benchmark_comparison.py`）：

| 场景与对比维度 | 普通自由对话 (Naive Chat) | PromptForge 结构化工程 | 核心价值 / 差异 |
| :--- | :--- | :--- | :--- |
| **编程开发（批量重命名脚本）** | 3 轮拉扯，消耗 1,589 Tokens | **1 轮交付，消耗 757 Tokens** | 📉 **节省 52.4% Token**，消除历史重传 |
| **交付成果可用性** | 散装不可机读文本 | **标准 `.cursorrules` / `.zcoderules`** | **直接驱动 IDE 智能体自动编码** |
| **日常办公（周例会纪要提炼）** | 多轮流水账追问，无统一结构 | **1 轮交付标准行动项表格与风险点** | 自动生成 OpenAI 规范 JSON API 体 |
| **本地参数校验与安全防注入** | 发送到云端报错（1~3秒，花钱） | **本地 0.487 ms 拦截，0 Token 开销** | 拦截类型错误、枚举失配与提示词注入 |

---

## 🧪 自动化测试

运行完整测试套件：
```bash
pytest tests/ -v
```
覆盖 8 大平台适配器、核心模板引擎、变量与预设解析、安全校验、CLI 命令行与 Web API，共计 **38 个单元测试用例全部通过（100% Passed）**，并对全部 56 套模板及 118 组预设实施格式与元数据完整性校验。

