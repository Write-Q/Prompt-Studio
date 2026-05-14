from pathlib import Path
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "frontend" / "script.js"
STYLE = Path(__file__).resolve().parents[1] / "frontend" / "style.css"
INDEX = Path(__file__).resolve().parents[1] / "frontend" / "index.html"


def _section_between(source: str, start: str, end: str) -> str:
    return source.split(start, 1)[1].split(end, 1)[0]


class FrontendFallbackSeedTest(unittest.TestCase):
    def test_frontend_fallback_matches_builtin_seed_library(self):
        source = SCRIPT.read_text(encoding="utf-8")
        fallback_seed_section = _section_between(source, "fallbackTemplates.splice(", "const contextCardTypeLabels")

        for title in [
            "日程规划助手",
            "学习笔记整理",
            "资料总结与重点提取",
            "文章润色改写",
            "工作周报整理",
            "会议纪要整理",
            "沟通表达优化",
            "旅行攻略规划",
            "商品对比决策",
            "一周饮食计划",
        ]:
            self.assertIn(title, fallback_seed_section)

        self.assertIn("fallbackContextCards.splice(", fallback_seed_section)
        self.assertEqual(fallback_seed_section.count("seed_key:"), 40)

        for title in [
            "PromptStudio 日常使用方式",
            "计划需要留缓冲",
            "周报结构",
            "示例：模糊事项到日程安排",
            "计划执行前检查",
        ]:
            self.assertIn(title, fallback_seed_section)

        self.assertNotIn("source:", fallback_seed_section)
        self.assertNotIn("contextCardSource", source)
        self.assertNotIn("来源", source)
        self.assertNotIn("大白话", source)
        self.assertNotIn("Prompt 需求澄清与模板生成", source)
        self.assertNotIn("上下文预算原则", source)

    def test_frontend_cards_render_hover_explanations(self):
        source = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("function templateHoverText", source)
        self.assertIn("function contextCardHoverText", source)
        self.assertIn("function showHoverTooltip", source)
        self.assertIn("function moveHoverTooltip", source)
        self.assertIn("function hideHoverTooltip", source)
        self.assertIn('document.createElement("div")', source)
        self.assertIn('hover-tooltip', source)
        self.assertIn("document.body.appendChild(elements.hoverTooltip)", source)
        self.assertIn('document.addEventListener("pointerover"', source)
        self.assertIn('document.addEventListener("pointermove"', source)
        self.assertIn('document.addEventListener("pointerout"', source)
        self.assertIn('class="choice-card has-hover-tip"', source)
        self.assertNotIn('class="resource-card has-hover-tip', source)
        self.assertNotIn('data-tooltip="${escapeHtml(contextCardHoverText(item))}" tabindex="0">\n        <div class="resource-row"', source)
        self.assertIn('data-tooltip="${escapeHtml(contextCardHoverText(item))}"', source)

    def test_frontend_enhances_all_selects_with_custom_ui(self):
        source = SCRIPT.read_text(encoding="utf-8")

        for fragment in [
            "const customSelects = new Map();",
            "function enhanceSelect(select, options = {})",
            "function refreshCustomSelect(select)",
            "function closeCustomSelects()",
            "function selectOption(select, value)",
            'select.classList.add("native-select")',
            'select.dispatchEvent(new Event("change", { bubbles: true }))',
            "enhanceSelect(elements.quickTemplateSelect",
            "enhanceSelect(elements.contextCardType",
            "enhanceSelect(elements.llmModel",
            'document.addEventListener("click",',
            'document.addEventListener("keydown",',
            'event.target.closest(".custom-select-menu")',
            "refreshCustomSelect(elements.quickTemplateSelect)",
            "refreshCustomSelect(elements.contextCardType)",
        ]:
            self.assertIn(fragment, source)

        self.assertIn('target.closest(".custom-select")', source)
        self.assertIn('data-custom-select-id', source)
        self.assertIn('custom-select', source)
        self.assertNotIn("function templateSelectOptionTooltip", source)
        self.assertNotIn("tooltip: templateSelectOptionTooltip", source)
        self.assertNotIn('data-tooltip="${escapeHtml(tooltip)}"', source)
        self.assertNotIn('${tooltip ? " has-hover-tip" : ""}', source)
        self.assertNotIn('elements.quickTemplateSelect.classList.add("has-hover-tip")', source)

    def test_custom_select_styles_cover_light_and_dark_variants(self):
        style = STYLE.read_text(encoding="utf-8")

        for fragment in [
            ".native-select",
            ".custom-select",
            ".custom-select-trigger",
            ".custom-select-menu",
            ".custom-select.open .custom-select-menu",
            ".custom-select-option.selected",
            ".custom-select.dark .custom-select-trigger",
            ".custom-select.dark .custom-select-menu",
            ".custom-select.dark .custom-select-option.selected",
        ]:
            self.assertIn(fragment, style)

    def test_frontend_assets_are_cache_busted(self):
        index = INDEX.read_text(encoding="utf-8")

        self.assertIn('./style.css?v=workflow-note-refine', index)
        self.assertIn('./script.js?v=workflow-note-refine', index)

    def test_sidebar_status_and_variable_inputs_match_current_workflow(self):
        index = INDEX.read_text(encoding="utf-8")
        source = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("<strong>Rule-first · DeepSeek LLM</strong>", index)
        self.assertNotIn("<strong>Rule + DeepSeek</strong>", index)
        self.assertIn("模板、变量与上下文卡片先在规则层拼装成 Prompt", index)
        self.assertIn("DeepSeek LLM 优化或生成", index)
        self.assertIn('data-variable-name="${escapeHtml(name)}"', source)
        self.assertIn('placeholder=""', source)
        self.assertNotIn('placeholder="填写 ${escapeHtml(name)}"', source)

    def test_seed_variables_are_specific_without_extra_input_hints(self):
        source = SCRIPT.read_text(encoding="utf-8")
        style = STYLE.read_text(encoding="utf-8")
        fallback_seed_section = _section_between(source, "fallbackTemplates.splice(", "const contextCardTypeLabels")

        for variable in [
            "待安排事项",
            "学习材料",
            "资料内容",
            "同行人和特殊需求",
            "当前顾虑",
            "现有食材和烹饪条件",
        ]:
            self.assertIn(f"{{{variable}}}", fallback_seed_section)

        self.assertNotIn("{输入内容}", fallback_seed_section)
        self.assertNotIn("function variableInputHint", source)
        self.assertNotIn("function variablePlaceholder", source)
        self.assertNotIn("variable-hint", source)
        self.assertNotIn(".variable-hint", style)
        self.assertNotIn("这里对应", source)


if __name__ == "__main__":
    unittest.main()
