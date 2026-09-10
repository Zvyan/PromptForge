# PromptForge — Enterprise-Grade Prompt Engineering Framework for AI Agents

<p align="center">
  <b>English</b> | <a href="README.md">中文</a>
</p>

PromptForge is a structured prompt engineering and management framework tailored for modern AI Agent ecosystems. It provides a clean, reusable, strongly-typed template system supporting direct invocation via CLI, modern Web UI, and OpenAI Codex terminal.

---

## 🌟 Key Features

- **9 Domain Categories & 56 Enterprise-Grade Templates**:
  - `coding` (9 templates): Code review, bug fix, refactor, new feature, test generation, SQL optimization, Docker/DevOps, Git workflow, algorithm design.
  - `analysis` (6 templates): Data insights, code complexity, security audit, root cause analysis (RCA), performance profiling, dependency audit.
  - `writing` (6 templates): Technical documentation, OpenAPI contracts, project README, PRD, architecture decision records (ADR), technical specifications (RFC).
  - `tool_use` (6 templates): Function calling contracts, MCP Server plugins, 3rd-party API integration, multi-agent orchestration, browser automation, database MCP interfaces.
  - `conversation` (5 templates): Multi-turn context steering, mock interview, Plan-first mode, rubber-duck debugging, structured debates.
  - `system` (4 templates): Agent persona definitions, zero-trust guardrails, strict safety rules, strongly-typed structured output enforcers.
  - `productivity` (8 templates): Meeting minutes distillation, weekly sync reports, social media copywriting, Feynman explanations, travel itineraries, business email polishing, video scripts, customer complaints.
  - `academic` (6 templates): Literature reviews, thesis proposals, academic paper polishing, experiment ablation design, coursework helpers, defense mock drills.
  - `presentation` (6 templates): Presentation narrative outlines, slide content & layouts, Marp slide generator, pitch decks, academic defense decks, speech rehearsals & Q&A.
- **118 Ready-to-Use Presets (100% Template Coverage)**:
  - Covers both heavy-duty architectural workflows and beginner-friendly everyday scenarios (e.g., student paper outlines, sick leave emails, Python file batch renamer, common IndexError troubleshooting).
  - Web UI 1-click auto-filling and CLI `--preset <id/index>` instant injection.
- **Deep Adaptation for 9 Platforms**:
  - Native formatters and configurations for OpenAI/Codex, Claude, Gemini, Cursor, Windsurf, generic Markdown, **ZCode (Zhipu GLM Agent Platform / CodeGeeX)**, **DeepSeek Harness (dsh / Cordis microkernel)**, and **Kimi (Moonshot AI)**.
- **Dual Interaction Modalities**:
  - **CLI**: Interactive wizard, parameter validation, batch export, token estimation, and compliance checks.
  - **Web UI**: Built on FastAPI + responsive frontend, featuring Vercel/Linear dark/light themes, category filters, quick-select chips, real-time token counter, 1-click clipboard copy, and file downloads.
- **Bilingual Output Support**: Native support for Chinese (`--lang zh`) and English (`--lang en`) prompt generation.
- **Priority Inheritance**: Custom templates in `custom_templates/` automatically override built-in templates seamlessly.
- **Codex CLI Deep Collaboration**: Follows the built-in `AGENTS.md` specification for natural language agent instruction configuration.

---

## 🤖 Platform Support Matrix

| Platform ID | Target Platform | Export Format | Core Capabilities |
| :--- | :--- | :--- | :--- |
| `openai` | OpenAI API / Codex CLI | JSON / `AGENTS.md` | Messages format, strict Function Calling JSON Schema, Codex project rules |
| `claude` | Anthropic Claude API | JSON / Custom Instructions | Dedicated top-level `system` field, Tool Use `input_schema`, Claude Projects rules |
| `gemini` | Google Gemini API | JSON | `systemInstruction` structure, multi-turn `contents`, `functionDeclarations` |
| `cursor` | Cursor IDE Agent | Markdown (`.cursorrules`) | Flattened role persona, coding rules, Composer/Agent index optimization |
| `windsurf` | Windsurf Editor | Markdown (`.windsurfrules`) | Tailored for Codeium Cascade memory engine |
| `zcode` | **Zhipu GLM Agent Platform** / CodeGeeX | Markdown / JSON | GLM Agent persona prompts, GLM-4 API payloads, code interpreter & web search plugins |
| `kimi` (`moonshot`) | **Kimi (Moonshot AI)** | Markdown / JSON | 128k~200k long-context optimization, Prompt Caching static anchor structuring, Moonshot API payload compatibility, web search & document QA |
| `deepseek_harness` (`dsh`) | **DeepSeek Harness Agent Framework** | YAML / Markdown | Cordis microkernel presets, V3/R1 persona rules, sandbox plugin configurations |
| `markdown` | Generic Chat Environments | Markdown | Modular sections, clean formatting for any web chat UI |

---

## 📦 Installation & Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/Zvyan/PromptForge.git
cd PromptForge

# (Optional) Create and activate virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies in editable development mode
pip install -e .
```

### 2. Multiple Launch Options

#### Option A: Windows 1-Click Launchers (Recommended)
Double-click in project root:
* **`start_web.bat`**: Launches the Web workspace and automatically opens `http://127.0.0.1:8000` in your default browser (with port conflict resolution).
* **`run.bat`**: Opens the interactive Rich console dashboard.
*(Linux / macOS users can run `chmod +x start_web.sh && ./start_web.sh`)*

#### Option B: Unified Interactive Launcher
```bash
# Interactive dashboard (Web launcher, CLI wizard, test runner)
python run.py

# Launch Web UI directly and open browser
python run.py web

# Launch with custom port
python run.py web --port 8888
```

#### Option C: Global Command Line
Once installed via pip:
```bash
# Launch Web UI directly
promptforge-ui

# Or via main CLI
promptforge web --port 8000
```

---

## 💻 CLI Usage Guide

```bash
# 1. List all categories and templates
promptforge list
promptforge list -c coding

# 2. View platform specifications and token limits
promptforge platforms

# 3. View built-in presets for a template
promptforge presets -c coding -t code_review
promptforge presets -c presentation -t pitch_deck

# 4. Generate prompts with 1-click preset (skip tedious variable typing)
promptforge generate -c coding -t code_review --preset 1 -p zcode
promptforge generate -c presentation -t pitch_deck --preset agent_infra_seed -p deepseek_harness

# 5. Override specific preset variables on the fly
promptforge generate -c coding -t code_review --preset 1 -v language=Go

# 6. Export directly to platform configuration files
promptforge export -c coding -t new_feature --preset batch_rename_files_script -p cursor -o .cursorrules
promptforge export -c coding -t code_review --preset 1 -p zcode -o glm_agent_config.json
promptforge export -c coding -t code_review --preset 1 -p deepseek_harness -o dsh_agent.yaml

# 7. Interactive mode (guided step-by-step menu)
promptforge generate -c coding -t bug_fix -p claude -i

# 8. Validate prompt files and estimate tokens
promptforge validate glm_agent_config.json -p zcode
```

---

## 📁 Template Specification

Templates are stored in `templates/<category>/<template_name>.yaml`. Standard schema:

```yaml
meta:
  name: "code_review"
  display_name: "Code Review"
  category: "coding"
  description: "Comprehensive code review template"
  tags: ["code-review", "quality"]
  version: "1.0.0"
  platforms: ["openai", "claude", "gemini", "cursor", "zcode"]

variables:
  language:
    type: string
    required: true
    description: "Programming language"
  strictness:
    type: enum
    required: true
    default: "standard"
    options: ["lenient", "standard", "strict"]
    description: "Review strictness"
  code_content:
    type: string
    required: true
    description: "Code snippet to review"

presets:
  - id: "python_api_review"
    title: "Python FastAPI Endpoint Review"
    description: "Review async endpoint for memory leaks and error handling"
    variables:
      language: "Python"
      strictness: "strict"
      code_content: "@app.get('/users')..."

sections:
  system:
    role: "You are a senior {{ language }} staff engineer."
    instructions: "Perform an in-depth code review with {{ strictness }} standards."
    output_format: "1. Executive Summary\n2. Issue List\n3. Actionable Recommendations"
    constraints: "- Specific and actionable\n- Provide before/after code snippets"
  user: |
    Please review the following {{ language }} code:
    ```{{ language }}
    {{ code_content }}
    ```

# Optional: English section overrides
sections_en:
  system:
    role: "You are a senior {{ language }} staff engineer."
    instructions: "Conduct a thorough code review."
  user: "Please review the following {{ language }} code:\n```{{ language }}\n{{ code_content }}\n```"
```

---

## 📊 Empirical Verification & Benchmarks (Naive Chat vs PromptForge)

Measured using standard `tiktoken` (`cl100k_base`) under real-world interaction patterns (`python benchmark_comparison.py`):

| Evaluation Dimension | Naive Freeform Chat | PromptForge Structured Engineering | Value & Core Difference |
| :--- | :--- | :--- | :--- |
| **Coding (Batch Rename Tool)** | 3 conversational turns, 1,589 Tokens | **1 turn precision delivery, 757 Tokens** | 📉 **52.4% Token Reduction**, eliminates history re-transmission |
| **Artifact Usability** | Conversational Markdown chatter | **Standard `.cursorrules` / `.zcoderules`** | **Directly drives IDE coding agents** |
| **Productivity (Meeting Minutes)** | Vague summaries requiring follow-ups | **1 turn action table + risk matrix** | Structured OpenAI JSON API payload |
| **Local Validation & Security** | Sent to cloud API (1-3s delay, incurred costs) | **Local 0.487 ms check, 0 Token cost** | Intercepts invalid enums & prompt injections |

---

## 🧪 Automated Testing

Run the full pytest suite:
```bash
pytest tests/ -v
```
All **38 unit tests pass cleanly (100% Passed)**, verifying all 8 platform adapters, core template engine, variable and preset resolution, prompt validation, CLI commands, FastAPI Web endpoints, and template integrity across all 56 templates and 118 presets.

---

## 📄 License

This project is licensed under the MIT License.
