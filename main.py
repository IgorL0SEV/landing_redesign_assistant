"""
Landing Page Analysis Web Interface
"""
from typing import Union, Dict, Any
import logging
from flask import Flask, render_template, request
from parser import Parser
from openai_module import OpenAIModule, UI_PROMPT, UX_PROMPT

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


from markupsafe import Markup
import markdown as md

app = Flask(__name__)
parser = Parser()
openai_module = OpenAIModule()

@app.route("/", methods=["GET", "POST"])
def index() -> str:
    """Handle both GET and POST requests for the main page."""
    result: Dict[str, Any] = {}
    error: str = ""

    if request.method == "POST":
        error = ""  # Сброс ошибки при новом запросе
        try:
            url = request.form.get("url", "").strip()
            mode = request.form.get("mode", "UI")
            logger.info(f"Получен POST запрос. URL: {url}, Режим: {mode}")

            if not url:
                error = "URL обязателен для заполнения"
                logger.warning("Попытка отправки формы без URL")
            else:
                # Get website content
                logger.info(f"Начинаем парсинг сайта: {url}")
                content = parser.parse_website(url)
                
                if not content:
                    error = "Не удалось получить содержимое сайта"
                    logger.error(f"Не удалось получить содержимое с {url}")
                else:
                    logger.info(f"Успешно получен контент, длина: {len(content)} символов")
                    # Process based on mode
                    if mode in ["UI", "Оба (UI + UX)"]:
                        logger.info("Начинаем UI анализ")
                        ui_analysis = openai_module.query_llm(UI_PROMPT, content)
                        result["ui"] = ui_analysis
                        logger.info("UI анализ завершен")

                    if mode in ["UX", "Оба (UI + UX)"]:
                        logger.info("Начинаем UX анализ")
                        ux_analysis = openai_module.query_llm(UX_PROMPT, content)
                        result["ux"] = ux_analysis
                        logger.info("UX анализ завершен")

        except Exception as e:
            error = f"Произошла ошибка при анализе: {str(e)}"




    def to_structured_html(text: str, mode: str = "ux") -> str:
        if mode == "ui":
            return Markup(md.markdown(text))
        import re
        lines = [l.rstrip() for l in text.split('\n')]
        html = []
        i = 0
        n = len(lines)
        section_titles = {'Плюсы:', 'Минусы:', 'Рекомендации:'}
        while i < n:
            line_stripped = lines[i].strip()
            if line_stripped in section_titles and lines[i] == line_stripped:
                html.append(f"<div class='rec-section-title' style='font-size:1.18em;font-weight:bold;margin-top:1em;margin-bottom:0.5em'>{line_stripped}</div>")
                i += 1
                continue
            m = re.match(r'^\*\*(.+)\*\*\s*:\s*(.*)', lines[i])
            if m:
                title = m.group(1).strip()
                desc = m.group(2).strip()
                block_lines = [desc] if desc else []
                j = i + 1
                while j < n and not re.match(r'^\*\*(.+)\*\*\s*:\s*', lines[j]) and not re.match(r'^(\d+)\.\s*', lines[j]) and lines[j].strip() not in section_titles:
                    if lines[j].strip():
                        block_lines.append(lines[j].strip())
                    j += 1
                if block_lines:
                    html.append(f'<div><b>{title}:</b> {'<br/>'.join(block_lines)}</div>')
                else:
                    html.append(f'<div><b>{title}:</b></div>')
                i = j
                continue
            m = re.match(r'^(\d+)\.\s*(.*)', lines[i])
            if m:
                current_title = m.group(2).strip()
                current_block = []
                j = i + 1
                while j < n and not re.match(r'^(\d+)\.\s*', lines[j]) and not re.match(r'^\*\*(.+)\*\*\s*:\s*', lines[j]) and lines[j].strip() not in section_titles:
                    if lines[j].strip():
                        current_block.append(lines[j].strip())
                    j += 1
                html.append(f'<div class="rec-block"><div class="rec-title">{current_title}</div><div class="rec-desc">{"<br/>".join(current_block)}</div></div>')
                i = j
                continue
            md_block = []
            while i < n and not re.match(r'^\*\*(.+)\*\*\s*:\s*', lines[i]) and not re.match(r'^(\d+)\.\s*', lines[i]) and lines[i].strip() not in section_titles:
                md_block.append(lines[i])
                i += 1
            if md_block:
                html.append(str(Markup(md.markdown('\n'.join(md_block)))))
        return ''.join(html)

    if result.get("ui"):
        result["ui_html"] = Markup(to_structured_html(result["ui"], mode="ui"))
    if result.get("ux"):
        result["ux_html"] = Markup(to_structured_html(result["ux"], mode="ux"))

    return render_template(
        "index.html",
        error=error,
        result=result,
        url=request.form.get("url", ""),
        mode=request.form.get("mode", "UI")
    )

if __name__ == "__main__":
    app.run(debug=True) 
