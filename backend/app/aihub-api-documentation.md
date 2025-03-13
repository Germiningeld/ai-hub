# AIHub API Documentation

AIHub предоставляет REST API для взаимодействия с различными моделями искусственного интеллекта через единый интерфейс. Это руководство содержит документацию по доступным эндпоинтам, схемам запросов и ответов.

## Основная информация

- **Базовый URL**: `/api`
- **Формат данных**: JSON
- **Аутентификация**: JWT Bearer токен

## Содержание

1. [Аутентификация](#аутентификация)
2. [Пользователи](#пользователи)
3. [API ключи](#api-ключи)
4. [Треды и сообщения](#треды-и-сообщения)
5. [Категории](#категории)
6. [Промпты](#промпты)
7. [Настройки моделей](#настройки-моделей)
8. [Статистика использования](#статистика-использования)
9. [Прямое взаимодействие с AI](#прямое-взаимодействие-с-ai)

## Аутентификация

### Вход в систему через форму OAuth2

**Запрос**:
```
POST /api/auth/token
```

**Параметры формы**:
- `username`: Email пользователя
- `password`: Пароль пользователя

**Ответ**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Вход в систему через JSON

**Запрос**:
```
POST /api/auth/login
```

**Тело запроса**:
```json
{
  "email": "user@example.com",
  "password": "strong_password"
}
```

**Ответ**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## Пользователи

### Создание нового пользователя

**Запрос**:
```
POST /api/users/
```

**Тело запроса**:
```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "strong_password"
}
```

**Ответ**:
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "is_active": true,
  "created_at": "2023-04-15T12:20:45.123456"
}
```

### Получение информации о текущем пользователе

**Запрос**:
```
GET /api/users/me
```

**Заголовки**:
- `Authorization`: `Bearer {token}`

**Ответ**:
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "is_active": true,
  "created_at": "2023-04-15T12:20:45.123456"
}
```

### Обновление информации о текущем пользователе

**Запрос**:
```
PUT /api/users/me
```

**Заголовки**:
- `Authorization`: `Bearer {token}`

**Тело запроса**:
```json
{
  "email": "newemail@example.com",
  "username": "new_username",
  "password": "new_password"
}
```

**Ответ**:
```json
{
  "id": 1,
  "email": "newemail@example.com",
  "username": "new_username",
  "is_active": true,
  "created_at": "2023-04-15T12:20:45.123456"
}
```

## API ключи

### Получение списка API ключей

**Запрос**:
```
GET /api/api-keys/
```

**Заголовки**:
- `Authorization`: `Bearer {token}`

**Ответ**:
```json
[
  {
    "id": 1,
    "user_id": 1,
    "provider": "openai",
    "api_key": "sk-ABC1234****9876XYZ",
    "name": "OpenAI Key",
    "is_active": true,
    "created_at": "2023-04-15T12:30:45.123456",
    "updated_at": "2023-04-15T12:30:45.123456"
  }
]
```

### Создание нового API ключа

**Запрос**:
```
POST /api/api-keys/
```

**Заголовки**:
- `Authorization`: `Bearer {token}`

**Тело запроса**:
```json
{
  "provider": "anthropic",
  "api_key": "sk-ant-api-key-123456789",
  "name": "Claude API Key",
  "is_active": true
}
```

**Ответ**:
```json
{
  "id": 2,
  "user_id": 1,
  "provider": "anthropic",
  "api_key": "sk-ant-api****789",
  "name": "Claude API Key",
  "is_active": true,
  "created_at": "2023-04-16T10:15:20.123456",
  "updated_at": "2023-04-16T10:15:20.123456"
}
```

### Обновление API ключа

**Запрос**:
```
PUT /api/api-keys/{key_id}
```

**Заголовки**:
- `Authorization`: `Bearer {token}`

**Тело запроса**:
```json
{
  "name": "Updated Key Name",
  "api_key": "sk-new-api-key-987654321",
  "is_active": false
}
```

**Ответ**:
```json
{
  "id": 2,
  "user_id": 1,
  "provider": "anthropic",
  "api_key": "sk-new-api****321",
  "name": "Updated Key Name",
  "is_active": false,
  "created_at": "2023-04-16T10:15:20.123456",
  "updated_at": "2023-04-16T11:30:15.987654"
}
```

### Удаление API ключа

**Запрос**:
```
DELETE /api/api-keys/{key_id}
```

**Заголовки**:
- `Authorization`: `Bearer {token}`

**Ответ**:
- Статус код: `204 No Content`

## Треды и сообщения

### Получение списка тредов

**Запрос**:
```
GET /api/threads/
```

**Заголовки**:
- `Authorization`: `Bearer {token}`

**Параметры запроса**:
- `skip` (необязательный): Пропустить указанное количество тредов (по умолчанию: 0)
- `limit` (необязательный): Максимальное количество возвращаемых тредов (по умолчанию: 100)
- `category_id` (необязательный): Фильтр по ID категории
- `is_archived` (необязательный): Фильтр по архивному статусу (true/false)
- `is_pinned` (необязательный): Фильтр по закрепленным тредам (true/false)
- `search` (необязательный): Текст для поиска в названиях тредов

**Ответ**:
```json
[
  {
    "id": 42,
    "user_id": 1,
    "title": "Обзор алгоритмов для обработки естественного языка",
    "provider": "openai",
    "model": "gpt-4o",
    "category_id": 9,
    "is_pinned": false,
    "is_archived": false,
    "created_at": "2024-02-10T09:15:32.123456",
    "updated_at": "2024-03-15T18:45:10.987654",
    "last_message_at": "2024-03-15T18:45:10.987654",
    "category": {
      "id": 9,
      "user_id": 1,
      "name": "NLP и обработка текста",
      "description": "Обсуждение технологий и алгоритмов обработки естественного языка",
      "color": "#008000",
      "created_at": "2024-01-20T14:22:36.741852",
      "updated_at": "2024-01-20T14:22:36.741852"
    },
    "message_count": 28
  }
]
```

### Создание нового треда

**Запрос**:
```
POST /api/threads/
```

**Заголовки**:
- `Authorization`: `Bearer {token}`

**Тело запроса**:
```json
{
  "title": "Анализ данных о продажах за 2023 год",
  "provider": "openai",
  "model": "gpt-4o",
  "category_id": 3,
  "is_pinned": false,
  "is_archived": false,
  "initial_message": "Я хочу проанализировать данные о продажах моего магазина за прошлый год. Как лучше визуализировать сезонные тренды?",
  "system_prompt": "Ты опытный аналитик данных, который помогает пользователю анализировать бизнес-показатели и строить информативные визуализации",
  "max_tokens": 2000,
  "temperature": 0.8
}
```

**Ответ**:
```json
{
  "id": 53,
  "user_id": 1,
  "title": "Анализ данных о продажах за 2023 год",
  "provider": "openai",
  "model": "gpt-4o",
  "category_id": 3,
  "is_pinned": false,
  "is_archived": false,
  "created_at": "2024-03-16T10:30:45.123456",
  "updated_at": "2024-03-16T10:30:45.123456",
  "last_message_at": "2024-03-16T10:30:45.123456",
  "message_count": 2,
  "category": {
    "id": 3,
    "user_id": 1,
    "name": "Аналитика данных",
    "description": "Запросы, связанные с анализом данных и бизнес-показателей",
    "color": "#0000FF",
    "created_at": "2024-01-15T09:10:20.123456",
    "updated_at": "2024-01-15T09:10:20.123456"
  },
  "messages": [
    {
      "id": 105,
      "thread_id": 53,
      "role": "system",
      "content": "Ты опытный аналитик данных, который помогает пользователю анализировать бизнес-показатели и строить информативные визуализации",
      "tokens": null,
      "model": null,
      "provider": null,
      "meta_data": {},
      "created_at": "2024-03-16T10:30:45.123456"
    },
    {
      "id": 106,
      "thread_id": 53,
      "role": "user",
      "content": "Я хочу проанализировать данные о продажах моего магазина за прошлый год. Как лучше визуализировать сезонные тренды?",
      "tokens": null,
      "model": null,
      "provider": null,
      "meta_data": {},
      "created_at": "2024-03-16T10:30:45.123456"
    }
  ]
}
```

### Создание треда с потоковой обработкой

**Запрос**:
```
POST /api/threads/stream
```

**Заголовки**:
- `Authorization`: `Bearer {token}`

**Тело запроса**:
```json
{
  "title": "Анализ сезонных трендов",
  "provider": "openai",
  "model": "gpt-4o",
  "category_id": 3,
  "is_pinned": false,
  "is_archived": false,
  "initial_message": "Как выявить и визуализировать сезонные тренды в данных о продажах?",
  "system_prompt": "Ты эксперт по анализу данных",
  "max_tokens": 2000,
  "temperature": 0.7
}
```

**Ответ**:
- Server-sent events (SSE) поток со следующими данными:
  - Информация о созданном треде
  - Текст ответа от AI (потоковая передача)
  - Сигнал завершения с ID сообщения ассистента

### Получение треда по ID

**Запрос**:
```
GET /api/threads/{thread_id}
```

**Заголовки**:
- `Authorization`: `Bearer {token}`

**Ответ**:
```json
{
  "id": 53,
  "user_id": 1,
  "title": "Анализ данных о продажах за 2023 год",
  "provider": "openai",
  "model": "gpt-4o",
  "category_id": 3,
  "is_pinned": false,
  "is_archived": false,
  "created_at": "2024-03-16T10:30:45.123456",
  "updated_at": "2024-03-16T10:35:20.987654",
  "last_message_at": "2024-03-16T10:35:20.987654",
  "message_count": 3,
  "category": {
    "id": 3,
    "user_id": 1,
    "name": "Аналитика данных",
    "description": "Запросы, связанные с анализом данных и бизнес-показателей",
    "color": "#0000FF",
    "created_at": "2024-01-15T09:10:20.123456",
    "updated_at": "2024-01-15T09:10:20.123456"
  },
  "messages": [
    {
      "id": 105,
      "thread_id": 53,
      "role": "system",
      "content": "Ты опытный аналитик данных, который помогает пользователю анализировать бизнес-показатели и строить информативные визуализации",
      "tokens": null,
      "model": null,
      "provider": null,
      "meta_data": {},
      "created_at": "2024-03-16T10:30:45.123456"
    },
    {
      "id": 106,
      "thread_id": 53,
      "role": "user",
      "content": "Я хочу проанализировать данные о продажах моего магазина за прошлый год. Как лучше визуализировать сезонные тренды?",
      "tokens": null,
      "model": null,
      "provider": null,
      "meta_data": {},
      "created_at": "2024-03-16T10:30:45.123456"
    },
    {
      "id": 107,
      "thread_id": 53,
      "role": "assistant",
      "content": "Для визуализации сезонных трендов в продажах за год рекомендую следующие подходы:\n\n1. **Линейный график продаж по месяцам/неделям** - самый простой и наглядный способ увидеть сезонность\n\n2. **Тепловая карта продаж** по месяцам и дням недели - помогает выявить паттерны не только по сезонам, но и в рамках недель\n\n3. **Столбчатая диаграмма с накоплением** - показывает вклад различных категорий товаров в общие продажи в течение сезонов\n\n4. **Декомпозиция временного ряда** - разбивает ваши данные на тренд, сезонность и остаток, явно выделяя сезонный компонент\n\n5. **Годовой календарь с цветовым кодированием** - интуитивное представление продаж по дням года\n\nКакие данные у вас имеются для анализа? Есть ли конкретные аспекты сезонности, которые вас особенно интересуют?",
      "tokens": 262,
      "model": "gpt-4o",
      "provider": "openai",
      "meta_data": {
        "tokens": {
          "prompt_tokens": 45,
          "completion_tokens": 262,
          "total_tokens": 307
        },
        "cost": 0.00786,
        "with_context": true
      },
      "created_at": "2024-03-16T10:35:20.987654"
    }
  ]
}
```

### Обновление информации о треде

**Запрос**:
```
PUT /api/threads/{thread_id}
```

**Заголовки**:
- `Authorization`: `Bearer {token}`

**Тело запроса**:
```json
{
  "title": "Оптимизация SQL-запросов для высоконагруженного приложения",
  "category_id": 7,
  "is_pinned": true,
  "is_archived": false
}
```

**Ответ**:
```json
{
  "id": 53,
  "user_id": 1,
  "title": "Оптимизация SQL-запросов для высоконагруженного приложения",
  "provider": "openai",
  "model": "gpt-4o",
  "category_id": 7,
  "is_pinned": true,
  "is_archived": false,
  "created_at": "2024-03-16T10:30:45.123456",
  "updated_at": "2024-03-16T11:20:30.123456",
  "last_message_at": "2024-03-16T10:35:20.987654",
  "message_count": 3,
  "category": {
    "id": 7,
    "user_id": 1,
    "name": "Разработка баз данных",
    "description": "Оптимизация и проектирование баз данных",
    "color": "#800080",
    "created_at": "2024-01-18T14:25:30.123456",
    "updated_at": "2024-01-18T14:25:30.123456"
  },
  "messages": [...]
}
```

### Удаление треда

**Запрос**:
```
DELETE /api/threads/{thread_id}
```

**Заголовки**:
- `Authorization`: `Bearer {token}`

**Ответ**:
- Статус код: `204 No Content`

### Массовое удаление тредов

**Запрос**:
```
POST /api/threads/bulk-delete
```

**Заголовки**:
- `Authorization`: `Bearer {token}`

**Тело запроса**:
```json
{
  "thread_ids": [12, 45, 67, 89, 123]
}
```

**Ответ**:
- Статус код: `204 No Content`

### Массовое архивирование тредов

**Запрос**:
```
POST /api/threads/bulk-archive
```

**Заголовки**:
- `Authorization`: `Bearer {token}`

**Тело запроса**:
```json
{
  "thread_ids": [12, 45, 67, 89, 123]
}
```

**Ответ**:
```json
[
  {
    "id": 12,
    "user_id": 1,
    "title": "Название треда 1",
    "provider": "openai",
    "model": "gpt-4o",
    "category_id": 3,
    "is_pinned": false,
    "is_archived": true,
    "created_at": "2024-02-10T09:15:32.123456",
    "updated_at": "2024-03-16T11:30:45.123456",
    "last_message_at": "2024-03-15T18:45:10.987654",
    "message_count": 15,
    "category": { ... }
  },
  ...
]
```

### Добавление сообщения в тред

**Запрос**:
```
POST /api/threads/{thread_id}/messages
```

**Заголовки**:
- `Authorization`: `Bearer {token}`

**Тело запроса**:
```json
{
  "role": "user",
  "content": "Объясни, пожалуйста, как работает алгоритм кластеризации K-means простыми словами",
  "tokens": 16,
  "model": null,
  "provider": null,
  "metadata": {
    "browser": "Chrome",
    "os": "Windows 11",
    "source": "web"
  }
}
```

**Ответ**:
```json
{
  "id": 108,
  "thread_id": 53,
  "role": "user",
  "content": "Объясни, пожалуйста, как работает алгоритм кластеризации K-means простыми словами",
  "tokens": 16,
  "model": null,
  "provider": null,
  "meta_data": {
    "browser": "Chrome",
    "os": "Windows 11",
    "source": "web"
  },
  "created_at": "2024-03-16T11:45:20.123456"
}
```

### Отправка сообщения и получение ответа

**Запрос**:
```
POST /api/threads/{thread_id}/send
```

**Заголовки**:
- `Authorization`: `Bearer {token}`

**Параметры запроса**:
- `use_context` (необязательный): Использовать ли контекст для генерации ответа (по умолчанию: true)

**Тело запроса**:
```json
{
  "content": "Напиши план исследования по теме 'Влияние социальных сетей на психологическое здоровье подростков'",
  "system_prompt": "Ты опытный научный руководитель, специализирующийся на психологии и социологии",
  "max_tokens": 2000,
  "temperature": 0.5
}
```

**Ответ**:
```json
{
  "id": 110,
  "thread_id": 53,
  "role": "assistant",
  "content": "# План исследования: Влияние социальных сетей на психологическое здоровье подростков\n\n## 1. Введение\n...",
  "tokens": 1245,
  "model": "gpt-4o",
  "provider": "openai",
  "meta_data": {
    "tokens": {
      "prompt_tokens": 89,
      "completion_tokens": 1245,
      "total_tokens": 1334
    },
    "cost": 0.03251,
    "with_context": true
  },
  "created_at": "2024-03-16T11:48:35.123456"
}
```

### Отправка сообщения с потоковой обработкой

**Запрос**:
```
POST /api/threads/{thread_id}/stream
```

**Заголовки**:
- `Authorization`: `Bearer {token}`

**Параметры запроса**:
- `use_context` (необязательный): Использовать ли контекст для генерации ответа (по умолчанию: true)
- `timeout` (необязательный): Таймаут генерации в секундах (по умолчанию: 120)

**Тело запроса**:
```json
{
  "content": "Напиши детальный анализ преимуществ и недостатков различных NoSQL баз данных",
  "system_prompt": "Ты эксперт по системам управления базами данных",
  "max_tokens": 3000,
  "temperature": 0.3
}
```

**Ответ**:
- Server-sent events (SSE) поток со следующими данными:
  - Подтверждение соединения с ID сообщения пользователя
  - Текст ответа от AI (потоковая передача)
  - Сигнал завершения с ID сообщения ассистента

### Остановка потоковой генерации

**Запрос**:
```
POST /api/threads/{thread_id}/stream/stop
```

**Заголовки**:
- `Authorization`: `Bearer {token}`

**Параметры запроса**:
- `message_id` (необязательный): ID сообщения, если уже сохранено

**Ответ**:
```json
{
  "success": true,
  "message": "Генерация прервана"
}
```

## Категории

### Получение списка категорий

**Запрос**:
```
GET /api/categories/
```

**Заголовки**:
- `Authorization`: `Bearer {token}`

**Ответ**:
```json
[
  {
    "id": 3,
    "user_id": 1,
    "name": "Аналитика данных",
    "description": "Запросы, связанные с анализом данных и бизнес-показателей",
    "color": "#0000FF",
    "created_at": "2024-01-15T09:10:20.123456",
    "updated_at": "2024-01-15T09:10:20.123456"
  },
  {
    "id": 7,
    "user_id": 1,
    "name": "Разработка баз данных",
    "description": "Оптимизация и проектирование баз данных",
    "color": "#800080",
    "created_at": "2024-01-18T14:25:30.123456",
    "updated_at": "2024-01-18T14:25:30.123456"
  }
]
```

### Создание новой категории

**Запрос**:
```
POST /api/categories/
```

**Заголовки**:
- `Authorization`: `Bearer {token}`

**Тело запроса**:
```json
{
  "name": "Учебные проекты",
  "description": "Треды, связанные с учебными заданиями и проектами",
  "color": "#4B0082"
}
```

**Ответ**:
```json
{
  "id": 12,
  "user_id": 1,
  "name": "Учебные проекты",
  "description": "Треды, связанные с учебными заданиями и проектами",
  "color": "#4B0082",
  "created_at": "2024-03-16T12:15:30.123456",
  "updated_at": "2024-03-16T12:15:30.123456"
}
```

### Обновление категории

**Запрос**:
```
PUT /api/categories/{category_id}
```

**Заголовки**:
- `Authorization`: `Bearer {token}`

**Тело запроса**:
```json
{
  "name": "Проекты по машинному обучению",
  "description": "Треды, посвященные проектам и задачам по ML",
  "color": "#800080"
}
```

**Ответ**:
```json
{
  "id": 12,
  "user_id": 1,
  "name": "Проекты по машинному обучению",
  "description": "Треды, посвященные проектам и задачам по ML",
  "color": "#800080",
  "created_at": "2024-03-16T12:15:30.123456",
  "updated_at": "2024-03-16T12:20:15.987654"
}
```

### Удаление категории

**Запрос**:
```
DELETE /api/categories/{category_id}
```

**Заголовки**:
- `Authorization`: `Bearer {token}`

**Ответ**:
- Статус код: `204 No Content`

## Промпты

### Получение списка промптов

**Запрос**:
```
GET /api/prompts/
```

**Заголовки**:
- `Authorization`: `Bearer {token}`

**Параметры запроса**:
- `skip` (необязательный): Пропустить указанное количество промптов (по умолчанию: 0)
- `limit` (необязательный): Максимальное количество возвращаемых промптов (по умолчанию: 100)
- `category_id` (необязательный): Фильтр по ID категории
- `is_favorite` (необязательный): Фильтр по избранным промптам (true/false)
- `search` (необязательный): Текст для поиска в названиях и содержании промптов

**Ответ**:
```json
[
  {
    "id": 42,
    "user_id": 1,
    "title": "Генерация идей для статьи",
    "content": "Предложи 5 креативных идей для статьи на тему {тема}",
    "description": "Промпт для быстрой генерации идей для контент-плана",
    "category_id": 5,
    "is_favorite": false,
    "created_at": "2025-02-15T14:30:45",
    "updated_at": "2025-02-16T09:12:33",
    "category": {
      "id": 5,
      "name": "Контент-маркетинг",
      "color": "#FF5733"
    }
  }
]
```

### Получение промпта по ID

**Запрос**:
```
GET /api/prompts/{prompt_id}
```

**Заголовки**:
- `Authorization`: `Bearer {token}`

**Ответ**:
```json
{
  "id": 42,
  "user_id": 1,
  "title": "Генерация идей для статьи",
  "content": "Предложи 5 креативных идей для статьи на тему {тема}",
  "description": "Промпт для быстрой генерации идей для контент-плана",
  "category_id": 5,
  "is_favorite": false,
  "created_at": "2025-02-15T14:30:45",
  "updated_at": "2025-02-16T09:12:33",
  "category": {
    "id": 5,
    "name": "Контент-маркетинг",
    "description": "Промпты для создания контента",
    "color": "#FF5733"
  }
}
```

### Создание нового промпта

**Запрос**:
```
POST /api/prompts/
```

**Заголовки**:
- `Authorization`: `Bearer {token}`

**Тело запроса**:
```json
{
  "title": "План маркетингового исследования",
  "content": "Проанализируй целевую аудиторию продукта {название_продукта} и предложи стратегию продвижения в социальных сетях.",
  "description": "Промпт для создания маркетингового плана по продвижению продукта",
  "category_id": 3,
  "is_favorite": true
}
```

**Ответ**:
```json
{
  "id": 48,
  "user_id": 1,
  "title": "План маркетингового исследования",
  "content": "Проанализируй целевую аудиторию продукта {название_продукта} и предложи стратегию продвижения в социальных сетях.",
  "description": "Промпт для создания маркетингового плана по продвижению продукта",
  "category_id": 3,
  "is_favorite": true,
  "created_at": "2024-03-16T14:30:45.123456",
  "updated_at": "2024-03-16T14:30:45.123456",
  "category": {
    "id": 3,
    "name": "Аналитика данных",
    "color": "#0000FF"
  }
}
```

### Обновление промпта

**Запрос**:
```
PUT /api/prompts/{prompt_id}
```

**Заголовки**:
- `Authorization`: `Bearer {token}`

**Тело запроса**:
```json
{
  "title": "Улучшенный план исследования",
  "content": "Разработай детальный план исследования по теме {тема_исследования}, включающий методологию, ключевые вопросы и ожидаемые результаты.",
  "description": "Обновленная версия промпта для научных исследований",
  "category_id": 2,
  "is_favorite": true
}
```

**Ответ**:
```json
{
  "id": 48,
  "user_id": 1,
  "title": "Улучшенный план исследования",
  "content": "Разработай детальный план исследования по теме {тема_исследования}, включающий методологию, ключевые вопросы и ожидаемые результаты.",
  "description": "Обновленная версия промпта для научных исследований",
  "category_id": 2,
  "is_favorite": true,
  "created_at": "2024-03-16T14:30:45.123456",
  "updated_at": "2024-03-16T15:20:30.987654",
  "category": {
    "id": 2,
    "name": "Научные исследования",
    "color": "#008000"
  }
}
```

### Удаление промпта

**Запрос**:
```
DELETE /api/prompts/{prompt_id}
```

**Заголовки**:
- `Authorization`: `Bearer {token}`

**Ответ**:
- Статус код: `204 No Content`

## Настройки моделей

### Получение списка доступных моделей

**Запрос**:
```
GET /api/models/available
```

**Заголовки**:
- `Authorization`: `Bearer {token}`

**Ответ**:
```json
{
  "models": [
    {
      "provider": "openai",
      "id": "gpt-4",
      "name": "GPT-4",
      "description": "Передовая модель OpenAI с высокой способностью к рассуждению",
      "max_tokens": 8192,
      "pricing": {
        "input": 10.0,
        "output": 30.0
      },
      "capabilities": ["рассуждение", "креативное письмо", "программирование"]
    },
    {
      "provider": "anthropic",
      "id": "claude-3-opus",
      "name": "Claude 3 Opus",
      "description": "Самая мощная модель Claude, оптимизированная для сложных задач",
      "max_tokens": 200000,
      "pricing": {
        "input": 15.0,
        "output": 75.0
      },
      "capabilities": ["рассуждение", "креативное письмо", "программирование", "математика", "анализ данных"]
    }
  ]
}
```

### Получение настроек моделей пользователя

**Запрос**:
```
GET /api/models/preferences
```

**Заголовки**:
- `Authorization`: `Bearer {token}`

**Ответ**:
```json
[
  {
    "id": 15,
    "user_id": 1,
    "provider": "openai",
    "model": "gpt-4",
    "max_tokens": 1500,
    "temperature": 0.8,
    "system_prompt": "Ты аналитик данных, помогающий интерпретировать сложные наборы данных и строить прогнозы",
    "is_default": false,
    "created_at": "2025-02-10T12:30:45",
    "updated_at": "2025-02-15T18:22:33"
  },
  {
    "id": 16,
    "user_id": 1,
    "provider": "anthropic",
    "model": "claude-3-opus",
    "max_tokens": 4000,
    "temperature": 0.5,
    "system_prompt": "Ты эксперт по машинному обучению, специализирующийся на глубоком обучении и компьютерном зрении",
    "is_default": true,
    "created_at": "2025-02-12T09:15:20",
    "updated_at": "2025-02-15T18:23:10"
  }
]
```

### Получение настроек моделей по умолчанию

**Запрос**:
```
GET /api/models/preferences/default
```

**Заголовки**:
- `Authorization`: `Bearer {token}`

**Ответ**:
```json
{
  "openai": {
    "id": 17,
    "user_id": 1,
    "provider": "openai",
    "model": "gpt-3.5-turbo",
    "max_tokens": 1000,
    "temperature": 0.7,
    "system_prompt": null,
    "is_default": true,
    "created_at": "2025-02-10T12:30:45",
    "updated_at": "2025-02-15T18:22:33"
  },
  "anthropic": {
    "id": 16,
    "user_id": 1,
    "provider": "anthropic",
    "model": "claude-3-opus",
    "max_tokens": 4000,
    "temperature": 0.5,
    "system_prompt": "Ты эксперт по машинному обучению, специализирующийся на глубоком обучении и компьютерном зрении",
    "is_default": true,
    "created_at": "2025-02-12T09:15:20",
    "updated_at": "2025-02-15T18:23:10"
  }
}
```

### Создание настройки модели

**Запрос**:
```
POST /api/models/preferences
```

**Заголовки**:
- `Authorization`: `Bearer {token}`

**Тело запроса**:
```json
{
  "provider": "anthropic",
  "model": "claude-3-opus",
  "max_tokens": 2000,
  "temperature": 0.5,
  "system_prompt": "Ты профессиональный копирайтер, специализирующийся на создании рекламных текстов",
  "is_default": true
}
```

**Ответ**:
```json
{
  "id": 18,
  "user_id": 1,
  "provider": "anthropic",
  "model": "claude-3-opus",
  "max_tokens": 2000,
  "temperature": 0.5,
  "system_prompt": "Ты профессиональный копирайтер, специализирующийся на создании рекламных текстов",
  "is_default": true,
  "created_at": "2024-03-16T15:45:30.123456",
  "updated_at": "2024-03-16T15:45:30.123456"
}
```

### Обновление настройки модели

**Запрос**:
```
PUT /api/models/preferences/{preferences_id}
```

**Заголовки**:
- `Authorization`: `Bearer {token}`

**Тело запроса**:
```json
{
  "max_tokens": 4000,
  "temperature": 0.3,
  "system_prompt": "Ты опытный научный консультант с глубокими знаниями в области медицины и биологии",
  "is_default": true
}
```

**Ответ**:
```json
{
  "id": 18,
  "user_id": 1,
  "provider": "anthropic",
  "model": "claude-3-opus",
  "max_tokens": 4000,
  "temperature": 0.3,
  "system_prompt": "Ты опытный научный консультант с глубокими знаниями в области медицины и биологии",
  "is_default": true,
  "created_at": "2024-03-16T15:45:30.123456",
  "updated_at": "2024-03-16T16:10:15.987654"
}
```

### Удаление настройки модели

**Запрос**:
```
DELETE /api/models/preferences/{preferences_id}
```

**Заголовки**:
- `Authorization`: `Bearer {token}`

**Ответ**:
- Статус код: `204 No Content`

## Статистика использования

### Получение статистики использования

**Запрос**:
```
GET /api/statistics/usage
```

**Заголовки**:
- `Authorization`: `Bearer {token}`

**Параметры запроса**:
- `start_date` (необязательный): Начальная дата в формате YYYY-MM-DD
- `end_date` (необязательный): Конечная дата в формате YYYY-MM-DD

**Ответ**:
```json
{
  "start_date": "2024-02-16",
  "end_date": "2024-03-16",
  "total_requests": 235,
  "total_tokens": 126758,
  "total_cost": 3.85,
  "daily_usage": [
    {
      "date": "2024-02-16",
      "requests": 15,
      "tokens": 8432,
      "cost": 0.25
    },
    {
      "date": "2024-02-17",
      "requests": 8,
      "tokens": 4217,
      "cost": 0.13
    }
  ],
  "model_usage": [
    {
      "provider": "openai",
      "model": "gpt-4",
      "requests": 120,
      "tokens": 75432,
      "cost": 2.45
    },
    {
      "provider": "anthropic",
      "model": "claude-3-opus",
      "requests": 85,
      "tokens": 42158,
      "cost": 1.12
    }
  ],
  "provider_summary": [
    {
      "provider": "openai",
      "requests": 150,
      "tokens": 85432,
      "cost": 2.65,
      "models_count": 2
    },
    {
      "provider": "anthropic",
      "requests": 85,
      "tokens": 41326,
      "cost": 1.20,
      "models_count": 1
    }
  ]
}
```

### Получение общей сводки использования

**Запрос**:
```
GET /api/statistics/summary
```

**Заголовки**:
- `Authorization`: `Bearer {token}`

**Ответ**:
```json
{
  "current_month": {
    "start_date": "2024-03-01",
    "end_date": "2024-03-16",
    "requests": 95,
    "tokens": 51247,
    "cost": 1.87
  },
  "last_30_days": {
    "start_date": "2024-02-15",
    "end_date": "2024-03-16",
    "requests": 215,
    "tokens": 115342,
    "cost": 3.42
  },
  "all_time": {
    "requests": 512,
    "tokens": 287652,
    "cost": 8.63
  },
  "savings": {
    "vs_subscription": 18.13,
    "subscription_cost": 20.0
  }
}
```

## Прямое взаимодействие с AI

### Генерация ответа без сохранения в тред

**Запрос**:
```
POST /api/threads/completion
```

**Заголовки**:
- `Authorization`: `Bearer {token}`

**Тело запроса**:
```json
{
  "provider": "openai",
  "model": "gpt-4o",
  "prompt": "Напиши стихотворение о весне в Санкт-Петербурге",
  "max_tokens": 1500,
  "temperature": 0.8,
  "system_prompt": "Ты талантливый поэт, который пишет красивые стихи в классическом стиле"
}
```

**Ответ**:
```json
{
  "text": "Над Невой туман рассветный,\nТает снег в объятьях солнца.\nВ Петербурге незаметно\nВесна в права свои вступает...",
  "model": "gpt-4o",
  "provider": "openai",
  "tokens": {
    "prompt_tokens": 42,
    "completion_tokens": 220,
    "total_tokens": 262
  },
  "cost": 0.00786,
  "from_cache": false
}
```

### Подсчет токенов в тексте

**Запрос**:
```
POST /api/threads/token-count
```

**Заголовки**:
- `Authorization`: `Bearer {token}`

**Тело запроса**:
```json
{
  "provider": "openai",
  "model": "gpt-4o",
  "text": "Проанализируй текст Пушкина 'Евгений Онегин' и выдели основные темы произведения"
}
```

**Ответ**:
```json
{
  "token_count": 12,
  "estimated": false
}
```

## Коды ошибок

В случае ошибки сервис возвращает соответствующий HTTP-статус код и JSON-объект с подробной информацией об ошибке.

### Общие ошибки

- `400 Bad Request` - Некорректные параметры запроса
- `401 Unauthorized` - Отсутствует или недействительный токен аутентификации
- `403 Forbidden` - У пользователя нет доступа к запрашиваемому ресурсу
- `404 Not Found` - Запрашиваемый ресурс не найден
- `429 Too Many Requests` - Превышен лимит запросов к API
- `500 Internal Server Error` - Внутренняя ошибка сервера

### Формат ответа с ошибкой

```json
{
  "error": true,
  "error_message": "Текст ошибки",
  "error_type": "Тип ошибки (not_found, rate_limit, billing, etc.)"
}
```

### Специфичные ошибки при работе с AI

- `api_key_not_found` - API ключ для указанного провайдера не найден
- `rate_limit` - Достигнут лимит запросов к API провайдера
- `billing` - Проблемы с биллингом (например, исчерпан кредит на API)
- `api_error` - Общая ошибка при взаимодействии с API провайдера
- `invalid_context` - Некорректный контекст диалога

## Примеры использования

### Пример рабочего процесса

1. Пользователь авторизуется: `POST /api/auth/login`
2. Пользователь настраивает API ключи: `POST /api/api-keys/`
3. Пользователь создает категории для организации: `POST /api/categories/`
4. Пользователь создает треды: `POST /api/threads/`
5. Пользователь отправляет сообщения в тред: `POST /api/threads/{thread_id}/send`
6. Пользователь сохраняет полезные промпты: `POST /api/prompts/`
7. Пользователь настраивает предпочтения моделей: `POST /api/models/preferences`
8. Пользователь отслеживает статистику использования: `GET /api/statistics/summary`

**