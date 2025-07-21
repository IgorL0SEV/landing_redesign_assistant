import os
import logging
from typing import List, Dict, Any, Optional
import openai
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Prompts for different analysis types
UI_PROMPT: str = (
    "Ты опытный UI-дизайнер. Проанализируй структуру и текст лендинга. "
    "Дай 5 конкретных рекомендаций по улучшению структуры и визуальной подачи. "
    "Не выдумывай содержание, опирайся только на предоставленный текст."
)

UX_PROMPT: str = (
    "Ты эксперт по UX. Проанализируй сайт и предоставь анализ в следующем формате:\n\n"
    "Плюсы:\n"
    "- [перечисли положительные аспекты]\n\n"
    "Минусы:\n"
    "- [перечисли отрицательные аспекты]\n\n"
    "Рекомендации:\n"
    "- [предложи 5 конкретных улучшений]\n\n"
    "Опирайся только на предоставленный текст, не выдумывай содержание."
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class OpenAIModule:
    def __init__(self) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        openai.api_key = api_key
        self.model = os.getenv("MODEL_NAME", "gpt-4-turbo-preview")
        self.temperature = float(os.getenv("TEMPERATURE", 0.7))
        self.max_tokens = int(os.getenv("MAX_TOKENS", 4000))

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry_error_callback=lambda retry_state: logger.error(
            f"Attempt {retry_state.attempt_number} failed with exception: {retry_state.outcome.exception()}"
        )
    )
    def query_llm(self, prompt: str, content: str) -> str:
        """
        Query OpenAI LLM with system prompt and content.
        
        Args:
            prompt (str): System prompt/instructions for the model
            content (str): Main content/question for the model
            
        Returns:
            str: Model's response text
            
        Raises:
            Exception: If all retry attempts fail
        """
        try:
            logger.info(f"Отправляем запрос к LLM с промптом: {prompt[:100]}...")
            logger.info(f"Длина контента: {len(content)} символов")
            
            if not content or len(content.strip()) < 10:
                logger.error("Контент слишком короткий или пустой")
                return "Ошибка: не удалось получить достаточно содержимого с сайта для анализа"
            
            messages: List[Dict[str, str]] = [
                {"role": "system", "content": prompt},
                {"role": "user", "content": content}
            ]
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            return response.choices[0].message['content'] or ""
            
        except Exception as e:
            logger.error(f"Error in OpenAI API call: {str(e)}")
            raise

    def get_completion(self, messages: List[Dict[str, str]]) -> Optional[str]:
        """
        Get completion from OpenAI API
        
        Args:
            messages (list): List of message dictionaries
            
        Returns:
            str: Assistant's response or None if error occurs
        """
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            return response.choices[0].message['content']
        except Exception as e:
            logger.error(f"Error in OpenAI API call: {str(e)}")
            return None 