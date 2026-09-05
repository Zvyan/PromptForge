/**
 * PromptForge Web UI JavaScript
 * 处理交互逻辑、实时异步生成、剪贴板复制、文件导出与主题切换
 */

document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initUiLang();
    initTabs();
    initPresets();
    initQuickChips();
    initGenerateForm();
    initCopyAndDownload();
    checkUrlPreset();
});

// 国际化双语字典 (i18n)
const I18N_DICT = {
    zh: {
        cli_guide: 'CLI 指南',
        cat_overview: '概览',
        cat_coding: '💻 编程开发',
        cat_analysis: '📊 数据分析',
        cat_writing: '📝 写作',
        cat_tool_use: '🛠️ 工具调用',
        cat_conversation: '💬 对话控制',
        cat_system: '⚙️ 系统指令',
        cat_productivity: '✨ 办公效率',
        cat_academic: '🎓 学术科研',
        cat_presentation: '📽️ 演示汇报',
        params_config: '⚙️ 提示词参数与配置',
        presets_title: '实战需求预设 (1-Click Presets)',
        presets_hint: '点击卡片一键自动装配全部参数与代码',
        target_platform: '目标平台 (Platform)',
        output_language: '输出语言 (Language)',
        dynamic_vars: '动态模板变量输入',
        btn_generate: '✨ 立即生成规范提示词',
        tab_formatted: '平台格式化输出',
        tab_raw: '纯文本 (Raw)',
        tab_json: 'JSON 报文',
        btn_copy: '📋 复制',
        btn_download: '💾 导出文件',
        lang_toggle_label: 'English'
    },
    en: {
        cli_guide: 'CLI Guide',
        cat_overview: 'Overview',
        cat_coding: '💻 Coding',
        cat_analysis: '📊 Data Analysis',
        cat_writing: '📝 Technical Writing',
        cat_tool_use: '🛠️ Tool & Agent',
        cat_conversation: '💬 Conversation',
        cat_system: '⚙️ System Rules',
        cat_productivity: '✨ Productivity',
        cat_academic: '🎓 Academic & Research',
        cat_presentation: '📽️ Presentations',
        params_config: '⚙️ Parameters & Config',
        presets_title: '1-Click Ready Presets',
        presets_hint: 'Click any card to auto-populate all parameters and code',
        target_platform: 'Target Platform',
        output_language: 'Output Language',
        dynamic_vars: 'Template Variable Inputs',
        btn_generate: '✨ Generate Structured Prompt',
        tab_formatted: 'Platform Export',
        tab_raw: 'Raw Markdown',
        tab_json: 'JSON Payload',
        btn_copy: '📋 Copy',
        btn_download: '💾 Download Config',
        lang_toggle_label: '中文'
    }
};

function initUiLang() {
    const toggleBtn = document.getElementById('uiLangToggle');
    if (!toggleBtn) return;

    let currentLang = localStorage.getItem('pf_ui_lang') || 'zh';
    applyUiLang(currentLang);

    toggleBtn.addEventListener('click', () => {
        currentLang = currentLang === 'zh' ? 'en' : 'zh';
        localStorage.setItem('pf_ui_lang', currentLang);
        applyUiLang(currentLang);
        
        if (currentLang === 'en') {
            const enRadio = document.querySelector('input[name="lang"][value="en"]');
            if (enRadio) {
                enRadio.checked = true;
                enRadio.dispatchEvent(new Event('change'));
            }
        }
    });
}

function applyUiLang(lang) {
    const dict = I18N_DICT[lang] || I18N_DICT.zh;
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (dict[key]) {
            el.textContent = dict[key];
        }
    });

    const langText = document.getElementById('uiLangText');
    if (langText) {
        langText.textContent = dict.lang_toggle_label;
    }
}

// 0. 预设场景一键填充
function initPresets() {
    const cards = document.querySelectorAll('.btn-preset-card, .btn-preset-chip');
    cards.forEach(card => {
        card.addEventListener('click', () => {
            cards.forEach(c => c.classList.remove('active'));
            card.classList.add('active');

            const presetDataStr = card.getAttribute('data-preset');
            const presetTitle = card.getAttribute('data-title') || '';
            if (!presetDataStr) return;

            try {
                const vars = JSON.parse(presetDataStr);
                Object.entries(vars).forEach(([key, val]) => {
                    const input = document.querySelector(`.generate-form [name="${key}"]`);
                    if (!input) return;

                    const type = input.getAttribute('data-type');
                    if (type === 'boolean') {
                        input.checked = Boolean(val);
                    } else if (type === 'list') {
                        input.value = Array.isArray(val) ? val.join(', ') : val;
                    } else {
                        input.value = val !== null && val !== undefined ? val : '';
                    }

                    // 触发 input/change 事件以同步快捷选项芯片状态
                    input.dispatchEvent(new Event('input', { bubbles: true }));
                    input.dispatchEvent(new Event('change', { bubbles: true }));

                    // 添加高亮反馈动效
                    input.classList.remove('field-highlight');
                    void input.offsetWidth; // 触发 reflow
                    input.classList.add('field-highlight');
                });

                // 展示装载成功提示
                const notice = document.getElementById('presetNotice');
                const noticeTitle = document.getElementById('presetNoticeTitle');
                if (notice && noticeTitle) {
                    noticeTitle.textContent = presetTitle;
                    notice.style.display = 'flex';
                }
            } catch (e) {
                console.error('解析预设参数失败:', e);
            }
        });
    });
}

// 0.1 变量快速选项芯片交互 (语言、框架、数据库与示例推荐)
function initQuickChips() {
    const quickChips = document.querySelectorAll('.btn-quick-chip');
    quickChips.forEach(chip => {
        chip.addEventListener('click', () => {
            const targetId = chip.getAttribute('data-target');
            const targetValue = chip.getAttribute('data-value');
            if (!targetId || targetValue === null) return;

            const targetInput = document.getElementById(targetId);
            if (!targetInput) return;

            // 设置目标输入控件值
            targetInput.value = targetValue;
            targetInput.dispatchEvent(new Event('input', { bubbles: true }));
            targetInput.dispatchEvent(new Event('change', { bubbles: true }));

            // 高亮当前芯片，取消同字段其他芯片的高亮
            const siblingChips = document.querySelectorAll(`.btn-quick-chip[data-target="${targetId}"]`);
            siblingChips.forEach(sc => sc.classList.remove('active'));
            chip.classList.add('active');

            // 给目标输入框添加脉冲动效
            targetInput.classList.remove('field-highlight');
            void targetInput.offsetWidth;
            targetInput.classList.add('field-highlight');
        });
    });

    // 监听输入控件的手动输入，实时同步选项芯片状态
    const formControls = document.querySelectorAll('.generate-form .form-control');
    formControls.forEach(ctrl => {
        ctrl.addEventListener('input', () => {
            const ctrlId = ctrl.id;
            if (!ctrlId) return;
            const currentVal = ctrl.value.trim();
            const relatedChips = document.querySelectorAll(`.btn-quick-chip[data-target="${ctrlId}"]`);
            relatedChips.forEach(chip => {
                if (chip.getAttribute('data-value').toLowerCase() === currentVal.toLowerCase()) {
                    chip.classList.add('active');
                } else {
                    chip.classList.remove('active');
                }
            });
        });
    });
}

// 0.2 检查 URL 是否携带预设参数 (如 ?preset=xxx) 并自动装配
function checkUrlPreset() {
    const urlParams = new URLSearchParams(window.location.search);
    const presetParam = urlParams.get('preset');
    if (!presetParam) return;

    const cards = Array.from(document.querySelectorAll('.btn-preset-card, .btn-preset-chip'));
    if (!cards.length) return;

    let targetCard = null;
    // 按数字索引匹配 (1-based)
    const numIdx = parseInt(presetParam, 10);
    if (!isNaN(numIdx) && numIdx >= 1 && numIdx <= cards.length) {
        targetCard = cards[numIdx - 1];
    } else {
        // 按 ID 或标题匹配
        targetCard = cards.find(c => {
            const pid = c.getAttribute('data-preset-id') || '';
            const title = c.getAttribute('data-title') || '';
            return pid.toLowerCase() === presetParam.toLowerCase() || title.includes(presetParam);
        });
    }

    if (targetCard) {
        targetCard.click();
    }
}

// 1. 主题切换
function initTheme() {
    const btnTheme = document.getElementById('themeToggle');
    if (!btnTheme) return;

    const savedTheme = localStorage.getItem('pf_theme') || 'dark';
    setTheme(savedTheme);

    btnTheme.addEventListener('click', () => {
        const currentTheme = document.body.classList.contains('theme-light') ? 'light' : 'dark';
        const nextTheme = currentTheme === 'dark' ? 'light' : 'dark';
        setTheme(nextTheme);
    });
}

function setTheme(theme) {
    if (theme === 'light') {
        document.body.classList.remove('theme-dark');
        document.body.classList.add('theme-light');
        const icon = document.querySelector('.theme-icon');
        const text = document.querySelector('.theme-text');
        if (icon) icon.textContent = '☀️';
        if (text) text.textContent = '浅色模式';
    } else {
        document.body.classList.remove('theme-light');
        document.body.classList.add('theme-dark');
        const icon = document.querySelector('.theme-icon');
        const text = document.querySelector('.theme-text');
        if (icon) icon.textContent = '🌙';
        if (text) text.textContent = '深色模式';
    }
    localStorage.setItem('pf_theme', theme);
}

// 2. 预览标签页切换
function initTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            tabBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const targetTab = btn.getAttribute('data-tab');
            document.querySelectorAll('.tab-pane').forEach(pane => {
                pane.classList.remove('active');
            });

            if (targetTab === 'formatted') {
                document.getElementById('tabFormatted')?.classList.add('active');
            } else if (targetTab === 'raw') {
                document.getElementById('tabRaw')?.classList.add('active');
            } else if (targetTab === 'json') {
                document.getElementById('tabJson')?.classList.add('active');
            }
        });
    });
}

// 3. 动态表单提交与生成请求
let currentGenerationResult = null;

function initGenerateForm() {
    const form = document.getElementById('generateForm');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        await generatePrompt();
    });

    // 平台切换时若已有生成结果，自动重新生成对应平台格式
    const platformRadios = document.querySelectorAll('input[name="platform"]');
    platformRadios.forEach(radio => {
        radio.addEventListener('change', () => {
            const platName = radio.value;
            const currentPlatEl = document.getElementById('currentPlatform');
            if (currentPlatEl) currentPlatEl.textContent = platName.toUpperCase();
            if (currentGenerationResult) {
                generatePrompt();
            }
        });
    });

    // 语言切换
    const langRadios = document.querySelectorAll('input[name="lang"]');
    langRadios.forEach(radio => {
        radio.addEventListener('change', () => {
            if (currentGenerationResult) {
                generatePrompt();
            }
        });
    });
}

async function generatePrompt() {
    const category = document.getElementById('categoryName')?.value;
    const template = document.getElementById('templateName')?.value;
    const platform = document.querySelector('input[name="platform"]:checked')?.value || 'openai';
    const lang = document.querySelector('input[name="lang"]:checked')?.value || 'zh';
    const btnSubmit = document.getElementById('btnSubmit');

    if (!category || !template) return;

    // 收集表单变量
    const variables = {};
    const inputs = document.querySelectorAll('.generate-form [data-type]');
    inputs.forEach(input => {
        const name = input.name;
        const type = input.getAttribute('data-type');
        if (!name) return;

        if (type === 'boolean') {
            variables[name] = input.checked;
        } else if (type === 'number') {
            variables[name] = input.value !== '' ? Number(input.value) : null;
        } else if (type === 'list') {
            variables[name] = input.value.split(',').map(s => s.trim()).filter(Boolean);
        } else {
            variables[name] = input.value;
        }
    });

    if (btnSubmit) {
        btnSubmit.disabled = true;
        btnSubmit.innerHTML = '<span>⏳ 正在生成...</span>';
    }

    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                category,
                template,
                platform,
                variables,
                lang,
            }),
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || '生成失败');
        }

        const data = await response.json();
        currentGenerationResult = data;
        renderOutput(data);
    } catch (err) {
        alert(`错误: ${err.message}`);
    } finally {
        if (btnSubmit) {
            btnSubmit.disabled = false;
            btnSubmit.innerHTML = '<span>✨ 立即生成提示词</span>';
        }
    }
}

function renderOutput(data) {
    const outputFormatted = document.getElementById('outputFormatted');
    const outputRaw = document.getElementById('outputRaw');
    const outputJson = document.getElementById('outputJson');
    const tokenCount = document.getElementById('tokenCount');
    const validationBadge = document.getElementById('validationBadge');
    const currentPlatform = document.getElementById('currentPlatform');
    const warningContainer = document.getElementById('warningContainer');
    const warningsList = document.getElementById('warningsList');

    if (outputFormatted) outputFormatted.textContent = data.formatted_content;
    if (outputRaw) outputRaw.textContent = data.raw_text;
    if (outputJson) outputJson.textContent = JSON.stringify(data, null, 2);
    if (tokenCount) tokenCount.textContent = data.token_estimate.toLocaleString();
    if (currentPlatform) currentPlatform.textContent = data.platform.toUpperCase();

    if (validationBadge) {
        if (data.validation.is_valid) {
            validationBadge.className = 'badge badge-success';
            validationBadge.textContent = '✓ 校验通过';
        } else {
            validationBadge.className = 'badge badge-error';
            validationBadge.textContent = '✗ 存在错误';
        }
    }

    if (warningContainer && warningsList) {
        const allNotes = [...(data.validation.errors || []), ...(data.validation.warnings || []), ...(data.validation.suggestions || [])];
        if (allNotes.length > 0) {
            warningsList.innerHTML = '';
            allNotes.forEach(item => {
                const li = document.createElement('li');
                li.textContent = item;
                warningsList.appendChild(li);
            });
            warningContainer.style.display = 'block';
        } else {
            warningContainer.style.display = 'none';
        }
    }
}

// 4. 复制与下载
function initCopyAndDownload() {
    const btnCopy = document.getElementById('btnCopy');
    const btnDownload = document.getElementById('btnDownload');

    if (btnCopy) {
        btnCopy.addEventListener('click', () => {
            const activePane = document.querySelector('.tab-pane.active code');
            if (!activePane || !activePane.textContent) {
                alert('暂无内容可复制');
                return;
            }
            navigator.clipboard.writeText(activePane.textContent).then(() => {
                const originalText = btnCopy.textContent;
                btnCopy.textContent = '✅ 已复制!';
                setTimeout(() => {
                    btnCopy.textContent = originalText;
                }, 2000);
            });
        });
    }

    if (btnDownload) {
        btnDownload.addEventListener('click', () => {
            if (!currentGenerationResult) {
                alert('请先生成提示词');
                return;
            }

            const platform = currentGenerationResult.platform;
            const content = currentGenerationResult.formatted_content;
            let filename = `prompt_${currentGenerationResult.template_name}_${platform}`;

            if (platform === 'cursor') filename = '.cursorrules';
            else if (platform === 'windsurf') filename = '.windsurfrules';
            else if (platform === 'zcode') filename = '.zcoderules';
            else if (currentGenerationResult.output_format === 'json') filename += '.json';
            else filename += '.md';

            const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        });
    }
}
