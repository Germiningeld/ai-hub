from app.services.openai_service import OpenAIService
from app.services.anthropic_service import AnthropicService
from app.services.ai_service_factory import AIServiceFactory
from app.services.cost_service import CostService

# Создаем глобальный экземпляр фабрики сервисов
ai_service_factory = AIServiceFactory()