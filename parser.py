import logging
from typing import Dict, Any
import requests
from bs4 import BeautifulSoup, element
from requests.exceptions import RequestException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Parser:
    def __init__(self) -> None:
        self.context: Dict[str, Any] = {}

    def parse_website(self, url: str) -> str:
        """
        Parse website and extract visible text content from body.
        
        Args:
            url (str): Website URL to parse
            
        Returns:
            str: Extracted text content or empty string if error occurs
        """
        try:
            logger.info(f"Начинаем парсинг сайта: {url}")
            
            # Get HTML content
            response = requests.get(url, timeout=30, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
            response.raise_for_status()
            logger.info(f"Получен ответ от сервера: {response.status_code}")
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            logger.info("HTML успешно распарсен")
            
            # Remove unwanted elements
            for element_name in ['header', 'nav', 'footer', 'aside', 'script', 'style']:
                for element in soup.find_all(element_name):
                    element.decompose()
                    
            # Remove hidden elements
            for element in soup.find_all(style=lambda value: value and 'display:none' in value.replace(' ', '')):
                element.decompose()
            for element in soup.find_all(hidden=True):
                element.decompose()
                
            # Get body content
            body = soup.find('body')
            if not body:
                logger.warning(f"Тег body не найден в {url}")
                return ""
                
            # Извлекаем текст, включая тексты кнопок и альтернативные описания изображений
            text_content = []
            
            # Добавляем заголовок страницы
            title = soup.find('title')
            if title:
                text_content.append(f"Заголовок страницы: {title.text.strip()}")
            
            # Добавляем метаописание
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc and meta_desc.get('content'):
                text_content.append(f"Метаописание: {meta_desc['content']}")
            
            # Собираем весь видимый текст
            for tag in body.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'span', 'div', 'a', 'button']):
                if tag.string and tag.string.strip():
                    text_content.append(tag.string.strip())
                    
            # Добавляем альтернативные описания изображений
            for img in body.find_all('img'):
                alt = img.get('alt', '').strip()
                if alt:
                    text_content.append(f"Изображение: {alt}")
            
            content = '\n'.join(text_content)
            logger.info(f"Извлечено {len(content)} символов текста")
            return content
            
        except RequestException as e:
            logger.error(f"Error fetching URL {url}: {str(e)}")
            return ""
        except Exception as e:
            logger.error(f"Error parsing content from {url}: {str(e)}")
            return ""

    def parse_text(self, text: str) -> Dict[str, Any]:
        """
        Parse input text and extract relevant information
        
        Args:
            text (str): Input text to parse
            
        Returns:
            dict: Parsed information
        """
        # Add your parsing logic here
        parsed_data = {
            "raw_text": text,
            "processed": {}
        }
        return parsed_data

    def update_context(self, new_context: Dict[str, Any]) -> None:
        """
        Update the parsing context
        
        Args:
            new_context (dict): New context information to add
        """
        self.context.update(new_context)

    def clear_context(self) -> None:
        """Clear the current context"""
        self.context = {} 