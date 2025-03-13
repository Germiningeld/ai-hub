from app.services.openai_service import OpenAIService
from app.services.anthropic_service import AnthropicService
from app.services.ai_service_factory import AIServiceFactory

# Создаем глобальный экземпляр фабрики сервисов
ai_service_factory = AIServiceFactory()