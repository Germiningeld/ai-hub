# Документация API для платформы AI чатов

## Содержание
- [Общая информация](#общая-информация)
- [Аутентификация](#аутентификация)
- [Обработка ошибок](#обработка-ошибок)
- [Эндпоинты API](#эндпоинты-api)
  - [Аутентификация](#эндпоинты-аутентификации)
  - [Пользователи](#пользователи)
  - [API ключи](#api-ключи)
  - [AI модели](#ai-модели)
  - [Треды (чаты)](#треды-чаты)
  - [Категории](#категории)
  - [Промпты](#промпты)
  - [Настройки моделей](#настройки-моделей)
  - [Статистика](#статистика)
- [Модели данных](#модели-данных)
- [Общие паттерны](#общие-паттерны)
- [Примеры на JavaScript](#примеры-на-javascript)
- [Решение проблем интеграции](#решение-проблем-интеграции)

## Общая информация

### Базовый URL
```
https://api.example.com/api
```

Для среды разработки: `http://localhost:8000/api`

### Принципы API
- RESTful архитектура
- JSON используется для тел запросов и ответов
- Аутентификация с помощью Bearer токена
- Единообразная обработка ошибок

### Поддерживаемые форматы данных
Все эндпоинты принимают и возвращают данные в формате JSON, если не указано иное. Загрузка файлов и специальные типы контента будут документированы для каждого эндпоинта по мере необходимости.

### Настройки CORS
API поддерживает Cross-Origin Resource Sharing (CORS) со следующими настройками:
- Разрешенные источники: настраиваются через `ALLOWED_ORIGINS` в настройках
- Учетные данные: разрешены
- Методы: все методы разрешены
- Заголовки: все заголовки разрешены

## Аутентификация

### Процесс аутентификации

1. Зарегистрируйте учетную запись пользователя (если еще не зарегистрированы)
2. Получите токен доступа, выполнив вход в систему
3. Включайте токен в заголовок авторизации для всех последующих запросов

### Получение токена

#### POST /auth/token

**Назначение:** Получение JWT токена для аутентификации через стандартную форму OAuth2.

**Тело запроса:**
```json
{
  "username": "user@example.com",  // Используется email в качестве username
  "password": "your_password"
}
```

**Пример ответа:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Коды ответов:**
- `200 OK`: Успешная аутентификация
- `401 Unauthorized`: Неверный email или пароль
- `400 Bad Request`: Пользователь неактивен

#### POST /auth/login

**Назначение:** Получение JWT токена для аутентификации через JSON.

**Тело запроса:**
```json
{
  "email": "user@example.com",
  "password": "your_password"
}
```

**Пример ответа:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Коды ответов:**
- `200 OK`: Успешная аутентификация
- `401 Unauthorized`: Неверный email или пароль
- `400 Bad Request`: Пользователь неактивен

### Использование токена

Для аутентифицированных запросов необходимо включать полученный токен в заголовок `Authorization` в формате:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Срок действия токена

Токен действителен в течение периода, указанного в настройках приложения (`ACCESS_TOKEN_EXPIRE_MINUTES`). Обычно это 30 дней.

## Обработка ошибок

### Стандартный формат ошибок

API возвращает ошибки в следующем формате:

```json
{
  "detail": "Сообщение об ошибке"
}
```

Для более сложных ошибок используется расширенный формат:

```json
{
  "error": true,
  "error_message": "Описание ошибки",
  "error_type": "тип_ошибки",
  "error_details": {} // Дополнительные детали ошибки
}
```

### Общие коды ошибок

- `400 Bad Request`: Неверный запрос, проверьте переданные параметры
- `401 Unauthorized`: Требуется аутентификация или учетные данные недействительны
- `403 Forbidden`: У пользователя нет прав для доступа к запрашиваемому ресурсу
- `404 Not Found`: Запрашиваемый ресурс не найден
- `405 Method Not Allowed`: Метод HTTP не разрешен для указанного эндпоинта
- `422 Unprocessable Entity`: Валидация не пройдена (проверьте тело запроса)
- `500 Internal Server Error`: Внутренняя ошибка сервера

## Эндпоинты API

### Эндпоинты аутентификации

#### POST /auth/token
Описано в разделе [Получение токена](#получение-токена).

#### POST /auth/login
Описано в разделе [Получение токена](#получение-токена).

### Пользователи

#### POST /users

**Назначение:** Создание нового пользователя.

**Требуется аутентификация:** Нет

**Тело запроса:**
```json
{
  "email": "user@example.com",
  "username": "username",
  "password": "strong_password"
}
```

**Пример ответа:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "is_active": true,
  "created_at": "2023-08-15T10:00:00"
}
```

**Коды ответов:**
- `201 Created`: Пользователь успешно создан
- `400 Bad Request`: Email уже зарегистрирован или имя пользователя уже занято

#### GET /users/me

**Назначение:** Получение информации о текущем пользователе.

**Требуется аутентификация:** Да

**Пример ответа:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "is_active": true,
  "created_at": "2023-08-15T10:00:00"
}
```

**Коды ответов:**
- `200 OK`: Успешный запрос
- `401 Unauthorized`: Требуется аутентификация

#### GET /model_preferences/preferences/default

**Назначение:** Возвращает настройки моделей по умолчанию для каждого провайдера.

**Требуется аутентификация:** Да

**Пример ответа:**
```json
{
  "1": {
    "id": 5,
    "user_id": 123,
    "provider_id": 1,
    "model_id": 3,
    "max_tokens": 2000,
    "temperature": 0.5,
    "system_prompt": "Ты опытный научный консультант с глубокими знаниями в области медицины и биологии",
    "is_default": true,
    "created_at": "2023-08-01T15:30:00",
    "updated_at": "2023-08-01T15:30:00"
  },
  "2": {
    "id": 12,
    "user_id": 123,
    "provider_id": 2,
    "model_id": 7,
    "max_tokens": 1000,
    "temperature": 0.7,
    "system_prompt": "Ты профессиональный копирайтер, специализирующийся на создании рекламных текстов",
    "is_default": true,
    "created_at": "2023-08-05T12:15:00",
    "updated_at": "2023-08-05T12:15:00"
  }
}
```

**Коды ответов:**
- `200 OK`: Успешный запрос
- `401 Unauthorized`: Требуется аутентификация

#### POST /model_preferences/preferences

**Назначение:** Создает новые настройки модели.

**Требуется аутентификация:** Да

**Тело запроса:**
```json
{
  "provider_id": 1,
  "model_id": 3,
  "max_tokens": 2000,
  "temperature": 0.5,
  "system_prompt": "Ты профессиональный копирайтер, специализирующийся на создании рекламных текстов",
  "is_default": true
}
```

**Пример ответа:**
```json
{
  "id": 25,
  "user_id": 123,
  "provider_id": 1,
  "model_id": 3,
  "max_tokens": 2000,
  "temperature": 0.5,
  "system_prompt": "Ты профессиональный копирайтер, специализирующийся на создании рекламных текстов",
  "is_default": true,
  "created_at": "2023-08-20T10:00:00",
  "updated_at": "2023-08-20T10:00:00"
}
```

**Коды ответов:**
- `201 Created`: Настройки успешно созданы
- `400 Bad Request`: Провайдер или модель не найдены, или настройки для этой модели уже существуют
- `401 Unauthorized`: Требуется аутентификация

#### PUT /model_preferences/preferences/{preferences_id}

**Назначение:** Обновляет настройки модели.

**Требуется аутентификация:** Да

**Параметры пути:**
- `preferences_id` - ID настроек модели

**Тело запроса:**
```json
{
  "provider_id": 1,
  "model_id": 3,
  "max_tokens": 4000,
  "temperature": 0.3,
  "system_prompt": "Ты опытный научный консультант с глубокими знаниями в области медицины и биологии",
  "is_default": true
}
```

**Пример ответа:**
```json
{
  "id": 25,
  "user_id": 123,
  "provider_id": 1,
  "model_id": 3,
  "max_tokens": 4000,
  "temperature": 0.3,
  "system_prompt": "Ты опытный научный консультант с глубокими знаниями в области медицины и биологии",
  "is_default": true,
  "created_at": "2023-08-20T10:00:00",
  "updated_at": "2023-08-20T10:15:00"
}
```

**Коды ответов:**
- `200 OK`: Успешное обновление
- `400 Bad Request`: Провайдер или модель не найдены
- `401 Unauthorized`: Требуется аутентификация
- `404 Not Found`: Настройки не найдены

#### DELETE /model_preferences/preferences/{preferences_id}

**Назначение:** Удаляет настройки модели.

**Требуется аутентификация:** Да

**Параметры пути:**
- `preferences_id` - ID настроек модели

**Коды ответов:**
- `204 No Content`: Успешное удаление
- `401 Unauthorized`: Требуется аутентификация
- `404 Not Found`: Настройки не найдены

### Статистика

#### GET /statistics/usage

**Назначение:** Возвращает статистику использования за указанный период.

**Требуется аутентификация:** Да

**Параметры запроса:**
- `start_date` (string, опционально): Начальная дата в формате YYYY-MM-DD
- `end_date` (string, опционально): Конечная дата в формате YYYY-MM-DD

**Пример ответа:**
```json
{
  "start_date": "2023-08-01",
  "end_date": "2023-08-31",
  "total_requests": 250,
  "total_tokens": 125000,
  "total_cost": 2.75,
  "daily_usage": [
    {
      "date": "2023-08-01",
      "requests": 10,
      "tokens": 5000,
      "cost": 0.1
    },
    // Другие дни
  ],
  "model_usage": [
    {
      "provider_id": 1,
      "provider_code": "openai",
      "model_id": 1,
      "model_code": "gpt-3.5-turbo",
      "requests": 200,
      "tokens": 100000,
      "cost": 2.0
    },
    // Другие модели
  ],
  "provider_summary": [
    {
      "provider_id": 1,
      "provider_code": "openai",
      "requests": 200,
      "tokens": 100000,
      "cost": 2.0,
      "models_count": 2
    },
    // Другие провайдеры
  ]
}
```

**Коды ответов:**
- `200 OK`: Успешный запрос
- `401 Unauthorized`: Требуется аутентификация

#### GET /statistics/summary

**Назначение:** Возвращает краткую сводку использования за последний месяц и всё время.

**Требуется аутентификация:** Да

**Пример ответа:**
```json
{
  "current_month": {
    "start_date": "2023-08-01",
    "end_date": "2023-08-31",
    "requests": 250,
    "tokens": 125000,
    "cost": 2.75
  },
  "last_30_days": {
    "start_date": "2023-08-02",
    "end_date": "2023-09-01",
    "requests": 245,
    "tokens": 122500,
    "cost": 2.65
  },
  "all_time": {
    "requests": 1250,
    "tokens": 625000,
    "cost": 15.50
  },
  "savings": {
    "vs_subscription": 17.25,
    "subscription_cost": 20.0
  }
}
```

**Коды ответов:**
- `200 OK`: Успешный запрос
- `401 Unauthorized`: Требуется аутентификация

## Модели данных

### Пользователь (User)

| Поле | Тип | Описание |
|------|-----|----------|
| id | int | Уникальный идентификатор пользователя |
| username | string | Имя пользователя (уникальное) |
| email | string | Email пользователя (уникальный) |
| password_hash | string | Хеш пароля (не возвращается в API) |
| first_name | string | Имя пользователя (опционально) |
| last_name | string | Фамилия пользователя (опционально) |
| is_active | boolean | Активен ли пользователь |
| is_admin | boolean | Является ли пользователь администратором |
| preferences | json | Предпочтения пользователя |
| created_at | datetime | Дата и время создания |
| updated_at | datetime | Дата и время последнего обновления |

### Провайдер (Provider)

| Поле | Тип | Описание |
|------|-----|----------|
| id | int | Уникальный идентификатор провайдера |
| code | string | Код провайдера (например, "openai", "anthropic") |
| name | string | Название провайдера |
| description | string | Описание провайдера |
| is_active | boolean | Активен ли провайдер |
| service_class | string | Имя класса сервиса для провайдера |
| config | json | Дополнительная конфигурация провайдера |
| created_at | datetime | Дата и время создания |
| updated_at | datetime | Дата и время последнего обновления |

### AI Модель (AIModel)

| Поле | Тип | Описание |
|------|-----|----------|
| id | int | Уникальный идентификатор модели |
| provider_id | int | ID провайдера |
| code | string | Код модели (например, "gpt-4", "claude-3-opus") |
| name | string | Название модели |
| description | string | Описание модели |
| is_active | boolean | Активна ли модель |
| max_context_length | int | Максимальная длина контекста в токенах |
| supports_streaming | boolean | Поддерживает ли потоковую генерацию |
| input_price | float | Стоимость за 1K входных токенов |
| output_price | float | Стоимость за 1K выходных токенов |
| config | json | Дополнительная конфигурация |
| created_at | datetime | Дата и время создания |
| updated_at | datetime | Дата и время последнего обновления |

### API Ключ (ApiKey)

| Поле | Тип | Описание |
|------|-----|----------|
| id | int | Уникальный идентификатор API ключа |
| user_id | int | ID пользователя |
| provider_id | int | ID провайдера |
| api_key | string | Значение API ключа (маскируется в ответах) |
| is_active | boolean | Активен ли ключ |
| name | string | Имя ключа (для удобства пользователя) |
| created_at | datetime | Дата и время создания |
| updated_at | datetime | Дата и время последнего обновления |

### Категория треда (ThreadCategory)

| Поле | Тип | Описание |
|------|-----|----------|
| id | int | Уникальный идентификатор категории |
| user_id | int | ID пользователя |
| name | string | Название категории |
| description | string | Описание категории |
| color | string | Цвет категории в HEX формате |
| created_at | datetime | Дата и время создания |
| updated_at | datetime | Дата и время последнего обновления |

### Тред (Thread)

| Поле | Тип | Описание |
|------|-----|----------|
| id | int | Уникальный идентификатор треда |
| user_id | int | ID пользователя |
| category_id | int | ID категории (опционально) |
| title | string | Название треда |
| is_pinned | boolean | Закреплен ли тред |
| is_archived | boolean | Архивирован ли тред |
| provider_id | int | ID провайдера |
| model_id | int | ID модели |
| provider_code | string | Код провайдера |
| model_code | string | Код модели |
| created_at | datetime | Дата и время создания |
| updated_at | datetime | Дата и время последнего обновления |
| last_message_at | datetime | Дата и время последнего сообщения |
| model_preference_id | int | ID предпочтения модели |
| max_tokens | int | Максимальное количество токенов для ответа |
| temperature | float | Температура (случайность) ответа |

### Сообщение (Message)

| Поле | Тип | Описание |
|------|-----|----------|
| id | int | Уникальный идентификатор сообщения |
| thread_id | int | ID треда |
| role | string | Роль отправителя (user, assistant, system) |
| content | string | Текст сообщения |
| tokens_input | int | Количество входных токенов |
| tokens_output | int | Количество выходных токенов |
| tokens_total | int | Общее количество токенов |
| provider_id | int | ID провайдера |
| provider_code | string | Код провайдера |
| model_id | int | ID модели |
| model_code | string | Код модели |
| cost | float | Стоимость запроса |
| is_cached | boolean | Был ли ответ получен из кэша |
| model_preference_id | int | ID предпочтения модели |
| meta_data | json | Метаданные сообщения |
| created_at | datetime | Дата и время создания |

### Сохраненный промпт (SavedPrompt)

| Поле | Тип | Описание |
|------|-----|----------|
| id | int | Уникальный идентификатор промпта |
| user_id | int | ID пользователя |
| category_id | int | ID категории (опционально) |
| title | string | Название промпта |
| content | string | Содержание промпта |
| description | string | Описание промпта |
| is_favorite | boolean | Добавлен ли промпт в избранное |
| created_at | datetime | Дата и время создания |
| updated_at | datetime | Дата и время последнего обновления |

### Настройки модели (ModelPreferences)

| Поле | Тип | Описание |
|------|-----|----------|
| id | int | Уникальный идентификатор настроек |
| user_id | int | ID пользователя |
| provider_id | int | ID провайдера |
| model_id | int | ID модели |
| max_tokens | int | Максимальное количество токенов для ответа |
| temperature | float | Температура (случайность) ответа |
| system_prompt | string | Системный промпт по умолчанию |
| is_default | boolean | Используется ли по умолчанию для провайдера |
| use_count | int | Количество использований |
| last_used_at | datetime | Дата и время последнего использования |
| created_at | datetime | Дата и время создания |
| updated_at | datetime | Дата и время последнего обновления |

## Общие паттерны

### Пагинация

Многие эндпоинты поддерживают пагинацию с помощью параметров `skip` и `limit`. Например:

```
GET /threads?skip=20&limit=10
```

Это вернет 10 тредов, начиная с 21-го.

### Фильтрация

Эндпоинты часто поддерживают фильтрацию по различным параметрам. Например:

```
GET /threads?category_id=1&is_archived=false
```

Это вернет неархивированные треды из категории с ID 1.

### Поиск

Некоторые эндпоинты поддерживают текстовый поиск с помощью параметра `search`. Например:

```
GET /threads?search=OpenAI
```

Это вернет все треды, в названии которых содержится "OpenAI".

## Примеры на JavaScript

### Аутентификация

```javascript
// Получение токена
async function login(email, password) {
  try {
    const response = await fetch('https://api.example.com/api/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ email, password })
    });
    
    if (!response.ok) {
      throw new Error(`Ошибка аутентификации: ${response.status}`);
    }
    
    const data = await response.json();
    // Сохраняем токен в localStorage
    localStorage.setItem('auth_token', data.access_token);
    return data;
  } catch (error) {
    console.error('Ошибка при входе:', error);
    throw error;
  }
}

// Функция для использования в API запросах
function getAuthHeader() {
  const token = localStorage.getItem('auth_token');
  return {
    'Authorization': `Bearer ${token}`
  };
}
```

### Создание треда и отправка сообщения

```javascript
// Создание нового треда
async function createThread(title, modelPreferencesId, initialMessage) {
  try {
    const response = await fetch('https://api.example.com/api/threads', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader()
      },
      body: JSON.stringify({
        title,
        model_preferences_id: modelPreferencesId,
        initial_message: initialMessage
      })
    });
    
    if (!response.ok) {
      throw new Error(`Ошибка создания треда: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Ошибка при создании треда:', error);
    throw error;
  }
}

// Отправка сообщения в существующий тред
async function sendMessage(threadId, content) {
  try {
    const response = await fetch(`https://api.example.com/api/threads/${threadId}/send`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader()
      },
      body: JSON.stringify({ content })
    });
    
    if (!response.ok) {
      throw new Error(`Ошибка отправки сообщения: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Ошибка при отправке сообщения:', error);
    throw error;
  }
}
```

### Использование потоковой генерации

```javascript
// Потоковая генерация ответа
async function streamMessage(threadId, content) {
  try {
    const response = await fetch(`https://api.example.com/api/threads/${threadId}/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader()
      },
      body: JSON.stringify({ content })
    });
    
    if (!response.ok) {
      throw new Error(`Ошибка при инициализации потока: ${response.status}`);
    }

    // Создаем обработчик событий
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    // Возвращаем генератор, который будет возвращать куски ответа
    return {
      async *[Symbol.asyncIterator]() {
        try {
          while (true) {
            const { done, value } = await reader.read();
            
            if (done) {
              break;
            }
            
            buffer += decoder.decode(value, { stream: true });
            
            // Разделяем буфер по строкам с префиксом "data: "
            const lines = buffer.split("\n\n");
            buffer = lines.pop() || ""; // Оставляем последнюю (возможно неполную) строку в буфере
            
            for (const line of lines) {
              if (line.startsWith('data: ')) {
                try {
                  const data = JSON.parse(line.slice(6)); // Удаляем "data: " и парсим JSON
                  yield data;
                  
                  if (data.done || data.error) {
                    return; // Завершаем поток при получении done или error
                  }
                } catch (e) {
                  console.warn('Ошибка при парсинге ответа:', e);
                }
              }
            }
          }
        } finally {
          reader.releaseLock();
        }
      }
    };
  } catch (error) {
    console.error('Ошибка при потоковой генерации:', error);
    throw error;
  }
}

// Пример использования
async function exampleStreamUsage() {
  const stream = await streamMessage(1, 'Какие есть библиотеки для работы с OpenAI API на Python?');
  
  let fullResponse = '';
  
  for await (const chunk of stream) {
    if (chunk.text) {
      fullResponse += chunk.text;
      console.log('Получен кусок текста:', chunk.text);
      // Здесь можно обновлять UI
    }
    
    if (chunk.error) {
      console.error('Ошибка генерации:', chunk.error_message);
      break;
    }
    
    if (chunk.done) {
      console.log('Генерация завершена, ID сообщения:', chunk.message_id);
      console.log('Полный ответ:', fullResponse);
      break;
    }
  }
}
```

## Решение проблем интеграции

### Общие проблемы и решения

1. **Ошибка аутентификации (401):**
   - Убедитесь, что токен правильно передается в заголовке `Authorization`
   - Проверьте срок действия токена (токен может истечь)
   - Попробуйте повторно войти в систему и получить новый токен

2. **Ошибка доступа (403):**
   - Проверьте, что у пользователя есть права на запрашиваемый ресурс
   - Для некоторых эндпоинтов требуются права администратора

3. **Ресурс не найден (404):**
   - Убедитесь, что запрашиваемый идентификатор (ID) существует
   - Проверьте, что URL построен правильно
   - Помните, что ресурсы других пользователей недоступны

4. **Проблемы с API ключами:**
   - Убедитесь, что API ключи добавлены и активированы
   - Проверьте наличие средств на счете провайдера API (OpenAI, Anthropic и т.д.)
   - Проверьте, что API ключи имеют необходимые разрешения

5. **Потоковая генерация прерывается:**
   - Убедитесь, что соединение остается открытым
   - Обрабатывайте таймауты и прерывания соединения
   - Используйте эндпоинт `/threads/{thread_id}/stream/stop` для корректной остановки генерации

### CORS-проблемы

Если вы сталкиваетесь с ошибками CORS при разработке на локальном сервере:

1. Убедитесь, что ваш домен включен в список `ALLOWED_ORIGINS` на сервере
2. Используйте полные URL с протоколом в запросах (например, `http://localhost:8000/api` вместо `/api`)
3. Для локальной разработки можно использовать прокси-сервер или CORS-плагины для браузера

### Советы по отладке

1. **Логирование запросов и ответов:**
   ```javascript
   // Утилита для отладки запросов
   async function debugFetch(url, options) {
     console.log('Запрос:', { url, ...options });
     try {
       const response = await fetch(url, options);
       const data = await response.clone().json().catch(() => null);
       console.log('Ответ:', { status: response.status, data });
       return response;
     } catch (error) {
       console.error('Ошибка запроса:', error);
       throw error;
     }
   }
   ```

2. **Использование инструментов разработчика:**
   - Вкладка "Network" в DevTools позволяет видеть все HTTP-запросы
   - Проверяйте заголовки запросов и ответов
   - Отслеживайте коды состояния (200, 400, 401 и т.д.)

3. **Организация тестовых сценариев:**
   - Создавайте отдельные тестовые функции для проверки API
   - Проверяйте сценарии успеха и ошибок
   - Документируйте обнаруженные проблемыd`: Требуется аутентификация

#### PUT /users/me

**Назначение:** Обновление информации о текущем пользователе.

**Требуется аутентификация:** Да

**Тело запроса:**
```json
{
  "email": "new_email@example.com",
  "username": "new_username",
  "password": "new_password"
}
```

**Пример ответа:**
```json
{
  "id": 1,
  "email": "new_email@example.com",
  "username": "new_username",
  "is_active": true,
  "created_at": "2023-08-15T10:00:00"
}
```

**Коды ответов:**
- `200 OK`: Успешное обновление
- `400 Bad Request`: Email уже зарегистрирован или имя пользователя уже занято
- `401 Unauthorized`: Требуется аутентификация

### API ключи

#### GET /api-keys

**Назначение:** Получение списка API ключей текущего пользователя.

**Требуется аутентификация:** Да

**Пример ответа:**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "provider_id": 1,
    "name": "My OpenAI Key",
    "api_key": "sk-****XXXX",
    "is_active": true,
    "created_at": "2023-08-15T10:00:00",
    "updated_at": "2023-08-15T10:00:00"
  }
]
```

**Коды ответов:**
- `200 OK`: Успешный запрос
- `401 Unauthorized`: Требуется аутентификация

#### POST /api-keys

**Назначение:** Создание нового API ключа для текущего пользователя.

**Требуется аутентификация:** Да

**Тело запроса:**
```json
{
  "provider_id": 1,
  "api_key": "sk-actual-api-key",
  "name": "My OpenAI Key",
  "is_active": true
}
```

**Пример ответа:**
```json
{
  "id": 1,
  "user_id": 1,
  "provider_id": 1,
  "name": "My OpenAI Key",
  "api_key": "sk-****XXXX",
  "is_active": true,
  "created_at": "2023-08-15T10:00:00",
  "updated_at": "2023-08-15T10:00:00"
}
```

**Коды ответов:**
- `201 Created`: Ключ успешно создан
- `400 Bad Request`: Провайдер с ID не найден или API ключ с такими параметрами уже существует
- `401 Unauthorized`: Требуется аутентификация

#### PUT /api-keys/{key_id}

**Назначение:** Обновление существующего API ключа.

**Требуется аутентификация:** Да

**Параметры пути:**
- `key_id` - ID API ключа

**Тело запроса:**
```json
{
  "provider_id": 1,
  "api_key": "sk-new-api-key",
  "name": "Updated OpenAI Key",
  "is_active": true
}
```

**Пример ответа:**
```json
{
  "id": 1,
  "user_id": 1,
  "provider_id": 1,
  "name": "Updated OpenAI Key",
  "api_key": "sk-****XXXX",
  "is_active": true,
  "created_at": "2023-08-15T10:00:00",
  "updated_at": "2023-08-15T10:05:00"
}
```

**Коды ответов:**
- `200 OK`: Успешное обновление
- `400 Bad Request`: Провайдер с ID не найден
- `401 Unauthorized`: Требуется аутентификация
- `404 Not Found`: API ключ не найден

#### DELETE /api-keys/{key_id}

**Назначение:** Удаление API ключа.

**Требуется аутентификация:** Да

**Параметры пути:**
- `key_id` - ID API ключа

**Коды ответов:**
- `204 No Content`: Успешное удаление
- `401 Unauthorized`: Требуется аутентификация
- `404 Not Found`: API ключ не найден

### AI модели

#### GET /ai-models/providers

**Назначение:** Получение списка всех доступных провайдеров.

**Требуется аутентификация:** Да

**Параметры запроса:**
- `is_active` (bool, опционально): Фильтр по активности провайдера. По умолчанию `true`.

**Пример ответа:**
```json
[
  {
    "id": 1,
    "code": "openai",
    "name": "OpenAI",
    "description": "OpenAI API provider",
    "is_active": true,
    "service_class": "OpenAIService",
    "config": {},
    "created_at": "2023-08-15T10:00:00",
    "updated_at": "2023-08-15T10:00:00"
  }
]
```

**Коды ответов:**
- `200 OK`: Успешный запрос
- `401 Unauthorized`: Требуется аутентификация
- `403 Forbidden`: Только администраторы могут просматривать неактивных провайдеров

#### GET /ai-models/providers/with-models

**Назначение:** Получение списка всех доступных провайдеров с их моделями.

**Требуется аутентификация:** Да

**Параметры запроса:**
- `is_active` (bool, опционально): Фильтр по активности провайдера. По умолчанию `true`.
- `models_active` (bool, опционально): Фильтр по активности моделей. По умолчанию `true`.

**Пример ответа:**
```json
[
  {
    "id": 1,
    "code": "openai",
    "name": "OpenAI",
    "description": "OpenAI API provider",
    "is_active": true,
    "service_class": "OpenAIService",
    "config": {},
    "created_at": "2023-08-15T10:00:00",
    "updated_at": "2023-08-15T10:00:00",
    "models": [
      {
        "id": 1,
        "provider_id": 1,
        "code": "gpt-3.5-turbo",
        "name": "GPT-3.5 Turbo",
        "description": "Базовая модель чат-бота",
        "is_active": true,
        "max_context_length": 4096,
        "supports_streaming": true,
        "input_price": 0.0015,
        "output_price": 0.002,
        "created_at": "2023-08-15T10:00:00",
        "updated_at": "2023-08-15T10:00:00"
      }
    ]
  }
]
```

**Коды ответов:**
- `200 OK`: Успешный запрос
- `401 Unauthorized`: Требуется аутентификация
- `403 Forbidden`: Только администраторы могут просматривать неактивных провайдеров или модели

#### GET /ai-models/providers/{provider_id}

**Назначение:** Получение информации о конкретном провайдере по ID.

**Требуется аутентификация:** Да

**Параметры пути:**
- `provider_id` - ID провайдера

**Пример ответа:**
```json
{
  "id": 1,
  "code": "openai",
  "name": "OpenAI",
  "description": "OpenAI API provider",
  "is_active": true,
  "service_class": "OpenAIService",
  "config": {},
  "created_at": "2023-08-15T10:00:00",
  "updated_at": "2023-08-15T10:00:00"
}
```

**Коды ответов:**
- `200 OK`: Успешный запрос
- `401 Unauthorized`: Требуется аутентификация
- `404 Not Found`: Провайдер не найден или неактивен

#### GET /ai-models/providers/by-code/{provider_code}

**Назначение:** Получение информации о конкретном провайдере по коду.

**Требуется аутентификация:** Да

**Параметры пути:**
- `provider_code` - Код провайдера (например, "openai")

**Пример ответа:**
```json
{
  "id": 1,
  "code": "openai",
  "name": "OpenAI",
  "description": "OpenAI API provider",
  "is_active": true,
  "service_class": "OpenAIService",
  "config": {},
  "created_at": "2023-08-15T10:00:00",
  "updated_at": "2023-08-15T10:00:00"
}
```

**Коды ответов:**
- `200 OK`: Успешный запрос
- `401 Unauthorized`: Требуется аутентификация
- `404 Not Found`: Провайдер не найден или неактивен

#### GET /ai-models/providers/{provider_id}/models

**Назначение:** Получение списка моделей указанного провайдера.

**Требуется аутентификация:** Да

**Параметры пути:**
- `provider_id` - ID провайдера

**Параметры запроса:**
- `is_active` (bool, опционально): Фильтр по активности моделей. По умолчанию `true`.

**Пример ответа:**
```json
[
  {
    "id": 1,
    "provider_id": 1,
    "code": "gpt-3.5-turbo",
    "name": "GPT-3.5 Turbo",
    "description": "Базовая модель чат-бота",
    "is_active": true,
    "max_context_length": 4096,
    "supports_streaming": true,
    "input_price": 0.0015,
    "output_price": 0.002,
    "created_at": "2023-08-15T10:00:00",
    "updated_at": "2023-08-15T10:00:00"
  }
]
```

**Коды ответов:**
- `200 OK`: Успешный запрос
- `401 Unauthorized`: Требуется аутентификация
- `403 Forbidden`: Только администраторы могут просматривать неактивные модели
- `404 Not Found`: Провайдер не найден или неактивен

#### GET /ai-models/available

**Назначение:** Получение списка доступных для пользователя провайдеров и моделей.

**Требуется аутентификация:** Да

**Пример ответа:**
```json
[
  {
    "id": 1,
    "code": "openai",
    "name": "OpenAI",
    "description": "OpenAI API provider",
    "is_active": true,
    "service_class": "OpenAIService",
    "config": {},
    "created_at": "2023-08-15T10:00:00",
    "updated_at": "2023-08-15T10:00:00",
    "models": [
      {
        "id": 1,
        "provider_id": 1,
        "code": "gpt-3.5-turbo",
        "name": "GPT-3.5 Turbo",
        "description": "Базовая модель чат-бота",
        "is_active": true,
        "max_context_length": 4096,
        "supports_streaming": true,
        "input_price": 0.0015,
        "output_price": 0.002,
        "created_at": "2023-08-15T10:00:00",
        "updated_at": "2023-08-15T10:00:00"
      }
    ]
  }
]
```

**Коды ответов:**
- `200 OK`: Успешный запрос
- `401 Unauthorized`: Требуется аутентификация

#### POST /ai-models/sync/{provider_id}

**Назначение:** Синхронизация моделей провайдера с API.

**Требуется аутентификация:** Да (только администраторы)

**Параметры пути:**
- `provider_id` - ID провайдера

**Пример ответа:**
```json
{
  "new_models": ["gpt-4"],
  "updated_models": ["gpt-3.5-turbo"],
  "deactivated_models": ["davinci-002"]
}
```

**Коды ответов:**
- `200 OK`: Успешная синхронизация
- `400 Bad Request`: У вас нет активного API ключа для провайдера
- `401 Unauthorized`: Требуется аутентификация
- `403 Forbidden`: Только администраторы могут синхронизировать модели
- `404 Not Found`: Провайдер не найден
- `500 Internal Server Error`: Ошибка при синхронизации моделей
- `501 Not Implemented`: Синхронизация моделей для данного провайдера не реализована

### Треды (чаты)

#### POST /threads

**Назначение:** Создает новый тред и по желанию добавляет первое сообщение.

**Требуется аутентификация:** Да

**Тело запроса:**
```json
{
  "title": "Вопросы по OpenAI API",
  "model_preferences_id": 7,
  "category_id": 1,
  "is_pinned": false,
  "is_archived": false,
  "initial_message": "Как мне использовать OpenAI API в моем приложении?",
  "system_prompt": "Ты - опытный инженер, специализирующийся на интеграции AI API."
}
```

**Пример ответа:**
```json
{
  "id": 1,
  "title": "Вопросы по OpenAI API",
  "provider_id": 1,
  "provider_code": "openai",
  "model_id": 1,
  "model_code": "gpt-3.5-turbo",
  "category_id": 1,
  "is_pinned": false,
  "is_archived": false,
  "created_at": "2023-08-15T10:00:00",
  "updated_at": "2023-08-15T10:00:00",
  "last_message_at": "2023-08-15T10:00:00",
  "message_count": 1,
  "category": {
    "id": 1,
    "name": "Работа",
    "description": "Треды, связанные с рабочими задачами",
    "color": "#4A90E2",
    "created_at": "2023-08-15T10:00:00",
    "updated_at": "2023-08-15T10:00:00"
  },
  "messages": [
    {
      "id": 1,
      "thread_id": 1,
      "role": "user",
      "content": "Как мне использовать OpenAI API в моем приложении?",
      "tokens_total": 0,
      "provider_id": 1,
      "provider_code": "openai",
      "model_id": 1,
      "model_code": "gpt-3.5-turbo",
      "meta_data": {},
      "created_at": "2023-08-15T10:00:00"
    }
  ]
}
```

**Коды ответов:**
- `201 Created`: Тред успешно создан
- `401 Unauthorized`: Требуется аутентификация
- `404 Not Found`: Категория не найдена
- `500 Internal Server Error`: Ошибка при создании треда

#### POST /threads/stream

**Назначение:** Создает новый тред с первым сообщением и сразу получает потоковый ответ от нейросети.

**Требуется аутентификация:** Да

**Тело запроса:**
```json
{
  "title": "Вопросы по OpenAI API",
  "model_preferences_id": 7,
  "category_id": 1,
  "is_pinned": false,
  "is_archived": false,
  "initial_message": "Как мне использовать OpenAI API в моем приложении?",
  "system_prompt": "Ты - опытный инженер, специализирующийся на интеграции AI API."
}
```

**Ответ:** Событийный поток (Server-Sent Events)

**Пример ответа:**
```
data: {"thread": {"thread_id": 1, "title": "Вопросы по OpenAI API", ...}}

data: {"text": "Для использования OpenAI API вам нужно выполнить следующие шаги:"}

data: {"text": "1. Создать аккаунт на OpenAI..."}

...

data: {"done": true, "message_id": 2}
```

**Коды ответов:**
- `201 Created`: Тред создан и поток начат
- `400 Bad Request`: Для создания треда с потоковой генерацией необходимо начальное сообщение
- `401 Unauthorized`: Требуется аутентификация
- `404 Not Found`: Категория не найдена
- `500 Internal Server Error`: Ошибка при создании треда или генерации ответа

#### GET /threads

**Назначение:** Возвращает список тредов пользователя с пагинацией и фильтрацией.

**Требуется аутентификация:** Да

**Параметры запроса:**
- `category_id` (int, опционально): Фильтр по ID категории
- `is_archived` (bool, опционально): Фильтр по статусу архивации
- `is_pinned` (bool, опционально): Фильтр по статусу закрепления
- `search` (string, опционально): Поисковый запрос
- `skip` (int, опционально): Количество пропускаемых записей. По умолчанию 0.
- `limit` (int, опционально): Максимальное количество записей. По умолчанию 100.

**Пример ответа:**
```json
[
  {
    "id": 1,
    "title": "Вопросы по OpenAI API",
    "provider_id": 1,
    "provider_code": "openai",
    "model_id": 1,
    "model_code": "gpt-3.5-turbo",
    "category_id": 1,
    "max_completion_tokens": 1000,
    "temperature": 0.7,
    "is_pinned": false,
    "is_archived": false,
    "created_at": "2023-08-15T10:00:00",
    "updated_at": "2023-08-15T10:05:00",
    "last_message_at": "2023-08-15T10:05:00",
    "message_count": 2,
    "category": {
      "id": 1,
      "name": "Работа",
      "description": "Треды, связанные с рабочими задачами",
      "color": "#4A90E2",
      "created_at": "2023-08-15T10:00:00",
      "updated_at": "2023-08-15T10:00:00"
    }
  }
]
```

**Коды ответов:**
- `200 OK`: Успешный запрос
- `401 Unauthorized`: Требуется аутентификация
- `500 Internal Server Error`: Ошибка при получении тредов

#### GET /threads/{thread_id}

**Назначение:** Возвращает тред с указанным ID и всеми его сообщениями.

**Требуется аутентификация:** Да

**Параметры пути:**
- `thread_id` - ID треда

**Пример ответа:**
```json
{
  "id": 1,
  "title": "Вопросы по OpenAI API",
  "provider_id": 1,
  "provider_code": "openai",
  "model_id": 1,
  "model_code": "gpt-3.5-turbo",
  "category_id": 1,
  "is_pinned": false,
  "is_archived": false,
  "created_at": "2023-08-15T10:00:00",
  "updated_at": "2023-08-15T10:05:00",
  "last_message_at": "2023-08-15T10:05:00",
  "message_count": 2,
  "category": {
    "id": 1,
    "name": "Работа",
    "description": "Треды, связанные с рабочими задачами",
    "color": "#4A90E2",
    "created_at": "2023-08-15T10:00:00",
    "updated_at": "2023-08-15T10:00:00"
  },
  "messages": [
    {
      "id": 1,
      "thread_id": 1,
      "role": "user",
      "content": "Как мне использовать OpenAI API в моем приложении?",
      "tokens_total": 0,
      "tokens_input": 0,
      "tokens_output": 0,
      "provider_id": 1,
      "provider_code": "openai",
      "model_id": 1,
      "model_code": "gpt-3.5-turbo",
      "meta_data": {},
      "created_at": "2023-08-15T10:00:00"
    },
    {
      "id": 2,
      "thread_id": 1,
      "role": "assistant",
      "content": "Для использования OpenAI API вам нужно получить API ключ и установить библиотеку openai...",
      "tokens_total": 150,
      "tokens_input": 50,
      "tokens_output": 100,
      "provider_id": 1,
      "provider_code": "openai",
      "model_id": 1,
      "model_code": "gpt-3.5-turbo",
      "cost": 0.001,
      "meta_data": {
        "tokens": {
          "prompt_tokens": 50,
          "completion_tokens": 100,
          "total_tokens": 150
        }
      },
      "created_at": "2023-08-15T10:05:05"
    }
  ]
}
```

**Коды ответов:**
- `200 OK`: Успешный запрос
- `401 Unauthorized`: Требуется аутентификация
- `403 Forbidden`: Нет доступа к треду
- `404 Not Found`: Тред не найден
- `500 Internal Server Error`: Ошибка при получении треда

#### PUT /threads/{thread_id}

**Назначение:** Обновляет информацию о треде.

**Требуется аутентификация:** Да

**Параметры пути:**
- `thread_id` - ID треда

**Тело запроса:**
```json
{
  "title": "Интеграция с OpenAI API",
  "category_id": 2,
  "is_pinned": true,
  "is_archived": false,
  "model_preference_id": 5,
  "max_completion_tokens": 2000,
  "temperature": 0.8
}
```

**Пример ответа:**
```json
{
  "id": 1,
  "title": "Интеграция с OpenAI API",
  "provider_id": 1,
  "provider_code": "openai",
  "model_id": 1,
  "model_code": "gpt-3.5-turbo",
  "category_id": 2,
  "is_pinned": true,
  "is_archived": false,
  "created_at": "2023-08-15T10:00:00",
  "updated_at": "2023-08-15T10:10:00",
  "last_message_at": "2023-08-15T10:05:00",
  "message_count": 2,
  "category": {
    "id": 2,
    "name": "Разработка",
    "description": "Треды, связанные с разработкой приложений",
    "color": "#2E86C1",
    "created_at": "2023-08-15T10:00:00",
    "updated_at": "2023-08-15T10:00:00"
  },
  "messages": [
    // Список сообщений
  ]
}
```

**Коды ответов:**
- `200 OK`: Успешное обновление
- `401 Unauthorized`: Требуется аутентификация
- `403 Forbidden`: Нет доступа к треду
- `404 Not Found`: Тред или категория не найдены
- `500 Internal Server Error`: Ошибка при обновлении треда

#### DELETE /threads/{thread_id}

**Назначение:** Удаляет тред с указанным ID.

**Требуется аутентификация:** Да

**Параметры пути:**
- `thread_id` - ID треда

**Коды ответов:**
- `204 No Content`: Успешное удаление
- `401 Unauthorized`: Требуется аутентификация
- `403 Forbidden`: Нет доступа к треду
- `404 Not Found`: Тред не найден
- `500 Internal Server Error`: Ошибка при удалении треда

#### POST /threads/bulk-delete

**Назначение:** Массовое удаление тредов.

**Требуется аутентификация:** Да

**Тело запроса:**
```json
{
  "thread_ids": [1, 2, 3, 4, 5]
}
```

**Коды ответов:**
- `204 No Content`: Успешное удаление
- `401 Unauthorized`: Требуется аутентификация
- `500 Internal Server Error`: Ошибка при массовом удалении тредов

#### POST /threads/bulk-archive

**Назначение:** Массовое архивирование тредов.

**Требуется аутентификация:** Да

**Тело запроса:**
```json
{
  "thread_ids": [1, 2, 3, 4, 5]
}
```

**Пример ответа:**
```json
[
  {
    "id": 1,
    "title": "Вопросы по OpenAI API",
    "provider_id": 1,
    "provider_code": "openai",
    "model_id": 1,
    "model_code": "gpt-3.5-turbo",
    "category_id": 1,
    "is_pinned": false,
    "is_archived": true,
    "created_at": "2023-08-15T10:00:00",
    "updated_at": "2023-08-15T10:15:00",
    "last_message_at": "2023-08-15T10:05:00",
    "message_count": 2,
    "category": {
      "id": 1,
      "name": "Работа",
      "description": "Треды, связанные с рабочими задачами",
      "color": "#4A90E2",
      "created_at": "2023-08-15T10:00:00",
      "updated_at": "2023-08-15T10:00:00"
    }
  },
  // Другие архивированные треды
]
```

**Коды ответов:**
- `200 OK`: Успешное архивирование
- `401 Unauthorized`: Требуется аутентификация
- `500 Internal Server Error`: Ошибка при массовом архивировании тредов

#### POST /threads/{thread_id}/messages

**Назначение:** Добавляет новое сообщение в тред.

**Требуется аутентификация:** Да

## Параметры пути:
- `thread_id` - ID треда

## Тело запроса
```json
{
    "content": "Какие есть библиотеки для работы с OpenAI API на Python?",
    "role": "user"
}
```

## Пример ответа
```json
{
    "id": 3,
    "thread_id": 1,
    "role": "user",
    "content": "Какие есть библиотеки для работы с OpenAI API на Python?",
    "tokens_input": 0,
    "tokens_output": 0,
    "tokens_total": 0,
    "provider_id": 1,
    "provider_code": "openai",
    "model_id": 1,
    "model_code": "gpt-3.5-turbo",
    "cost": 0.0,
    "is_cached": false,
    "model_preference_id": 2,
    "meta_data": {},
    "created_at": "2023-08-15T10:15:00"
}
```

## Поля ответа
- `id` (int): Уникальный идентификатор сообщения
- `thread_id` (int): ID треда, к которому относится сообщение
- `role` (string): Роль отправителя (user, assistant, system)
- `content` (string): Текст сообщения
- `tokens_input` (int): Количество входных токенов
- `tokens_output` (int): Количество выходных токенов
- `tokens_total` (int): Общее количество токенов
- `provider_id` (int): ID провайдера
- `provider_code` (string): Код провайдера (например, "openai")
- `model_id` (int): ID модели
- `model_code` (string): Код модели (например, "gpt-3.5-turbo")
- `cost` (float): Стоимость запроса в долларах (для сообщений пользователя обычно 0)
- `is_cached` (boolean): Был ли ответ получен из кэша
- `model_preference_id` (int): ID предпочтения модели
- `meta_data` (object): Дополнительные метаданные сообщения
- `created_at` (string): Дата и время создания в формате ISO

## Коды ответов
- **200 OK**: Успешное добавление сообщения
- **401 Unauthorized**: Требуется аутентификация
- **404 Not Found**: Тред не найден
- **500 Internal Server Error**: Ошибка при добавлении сообщения

#### POST /threads/{thread_id}/send

**Назначение:** Отправляет сообщение пользователя в тред и получает ответ от ИИ.

**Требуется аутентификация:** Да

**Параметры пути:**
- `thread_id` - ID треда

**Параметры запроса:**
- `use_context` (bool, опционально): Использовать ли контекст для генерации ответа. По умолчанию `true`.

**Тело запроса:**
```json
{
  "content": "Какие есть библиотеки для работы с OpenAI API на Python?",
  "system_prompt": "Ты - опытный Python разработчик.",
  "max_tokens": 1000,
  "temperature": 0.7
}
```

**Пример ответа:**
```json
{
  "id": 4,
  "thread_id": 1,
  "role": "assistant",
  "content": "Для работы с OpenAI API на Python есть несколько библиотек...",
  "tokens_total": 180,
  "tokens_input": 60,
  "tokens_output": 120,
  "provider_id": 1,
  "provider_code": "openai",
  "model_id": 1,
  "model_code": "gpt-3.5-turbo",
  "cost": 0.0015,
  "meta_data": {
    "tokens": {
      "prompt_tokens": 60,
      "completion_tokens": 120,
      "total_tokens": 180
    },
    "with_context": true
  },
  "created_at": "2023-08-15T10:16:00"
}
```

**Коды ответов:**
- `200 OK`: Успешная отправка и получение ответа
- `401 Unauthorized`: Требуется аутентификация
- `403 Forbidden`: Нет доступа к треду
- `404 Not Found`: Тред не найден
- `500 Internal Server Error`: Ошибка при отправке сообщения или генерации ответа

#### POST /threads/completion

**Назначение:** Генерирует ответ на основе запроса пользователя без сохранения в тред.

**Требуется аутентификация:** Да

**Тело запроса:**
```json
{
  "prompt": "Напиши простую функцию на Python для подсчета слов в тексте",
  "provider_id": 1,
  "model_preference_id": 7,
  "system_prompt": "Ты - опытный Python разработчик.",
  "max_tokens": 1000,
  "temperature": 0.7
}
```

**Пример ответа:**
```json
{
  "text": "Вот простая функция для подсчета слов в тексте:\n\n```python\ndef count_words(text):\n    if not text:\n        return 0\n    words = text.split()\n    return len(words)\n```\n\nПример использования:\n\n```python\ntext = 'Привет, мир! Это пример текста.'\nword_count = count_words(text)\nprint(f'Количество слов: {word_count}')\n# Выведет: Количество слов: 5\n```",
  "model": "gpt-3.5-turbo",
  "provider": "openai",
  "tokens": {
    "prompt_tokens": 50,
    "completion_tokens": 120,
    "total_tokens": 170
  },
  "cost": 0.0015,
  "from_cache": false
}
```

**Коды ответов:**
- `200 OK`: Успешная генерация
- `400 Bad Request`: API ключ не найден или другие проблемы с запросом
- `401 Unauthorized`: Требуется аутентификация
- `500 Internal Server Error`: Ошибка при генерации ответа

#### POST /threads/token-count

**Назначение:** Подсчитывает количество токенов в тексте.

**Требуется аутентификация:** Да

**Тело запроса:**
```json
{
  "text": "Напиши простую функцию на Python для подсчета слов в тексте",
  "model_preferences_id": 7
  // Или альтернативно:
  // "provider_id": 1,
  // "model_id": 1
}
```

**Пример ответа:**
```json
{
  "token_count": 12,
  "estimated": false
}
```

**Коды ответов:**
- `200 OK`: Успешный подсчет
- `400 Bad Request`: Ошибка в запросе
- `401 Unauthorized`: Требуется аутентификация
- `404 Not Found`: Модель или предпочтение не найдены
- `500 Internal Server Error`: Ошибка при подсчете токенов

#### POST /threads/{thread_id}/stream

**Назначение:** Отправляет сообщение пользователя в тред и получает потоковый ответ от ИИ.

**Требуется аутентификация:** Да

**Параметры пути:**
- `thread_id` - ID треда

**Параметры запроса:**
- `use_context` (bool, опционально): Использовать ли контекст для генерации ответа. По умолчанию `true`.
- `timeout` (int, опционально): Таймаут генерации в секундах. По умолчанию 120.

**Тело запроса:**
```json
{
  "content": "Какие есть библиотеки для работы с OpenAI API на Python?",
  "system_prompt": "Ты - опытный Python разработчик.",
  "max_tokens": 1000,
  "temperature": 0.7
}
```

**Ответ:** Событийный поток (Server-Sent Events)

**Пример ответа:**
```
data: {"status": "created", "user_message_id": 5}

data: {"text": "Для работы с OpenAI API на Python есть несколько библиотек:"}

data: {"text": "\n\n1. `openai` - официальная библиотека от OpenAI, "}

...

data: {"done": true, "message_id": 6}
```

**Коды ответов:**
- `200 OK`: Поток успешно начат
- `401 Unauthorized`: Требуется аутентификация
- `403 Forbidden`: Нет доступа к треду
- `404 Not Found`: Тред не найден
- `500 Internal Server Error`: Ошибка при инициализации потока

#### POST /threads/{thread_id}/stream/stop

**Назначение:** Прерывает генерацию ответа и сохраняет текущий результат.

**Требуется аутентификация:** Да

## Параметры пути:
- `thread_id` - ID треда

## Параметры запроса:
- `message_id` (int, опционально): ID сообщения, если оно уже было сохранено в базе данных

## Тело запроса
Не требуется

## Пример ответа
```json
{
    "success": true,
    "message": "Генерация прервана"
}
```

## Коды ответов
- **200 OK**: Успешная остановка
- **401 Unauthorized**: Требуется аутентификация
- **403 Forbidden**: Нет доступа к треду
- **404 Not Found**: Тред не найден
- **500 Internal Server Error**: Ошибка при остановке потока

### Категории

#### GET /categories

**Назначение:** Получает список всех категорий тредов пользователя.

**Требуется аутентификация:** Да

**Пример ответа:**
```json
[
  {
    "id": 1,
    "user_id": 123,
    "name": "Работа",
    "description": "Треды, связанные с рабочими задачами",
    "color": "#4A90E2",
    "created_at": "2023-08-15T10:00:00",
    "updated_at": "2023-08-15T10:00:00"
  },
  {
    "id": 2,
    "user_id": 123,
    "name": "Обучение",
    "description": "Треды по изучению ИИ",
    "color": "#E74C3C",
    "created_at": "2023-08-18T14:30:00",
    "updated_at": "2023-08-18T14:30:00"
  }
]
```

**Коды ответов:**
- `200 OK`: Успешный запрос
- `401 Unauthorized`: Требуется аутентификация

#### POST /categories

**Назначение:** Создает новую категорию тредов.

**Требуется аутентификация:** Да

**Тело запроса:**
```json
{
  "name": "Работа",
  "description": "Треды, связанные с рабочими задачами",
  "color": "#4A90E2"
}
```

**Пример ответа:**
```json
{
  "id": 1,
  "user_id": 123,
  "name": "Работа",
  "description": "Треды, связанные с рабочими задачами",
  "color": "#4A90E2",
  "created_at": "2023-08-15T10:00:00",
  "updated_at": "2023-08-15T10:00:00"
}
```

**Коды ответов:**
- `201 Created`: Категория успешно создана
- `400 Bad Request`: Категория с таким именем уже существует
- `401 Unauthorized`: Требуется аутентификация

#### PUT /categories/{category_id}

**Назначение:** Обновляет информацию о категории.

**Требуется аутентификация:** Да

**Параметры пути:**
- `category_id` - ID категории

**Тело запроса:**
```json
{
  "name": "Рабочие задачи",
  "description": "Треды, связанные с задачами на работе",
  "color": "#2E86C1"
}
```

**Пример ответа:**
```json
{
  "id": 1,
  "user_id": 123,
  "name": "Рабочие задачи",
  "description": "Треды, связанные с задачами на работе",
  "color": "#2E86C1",
  "created_at": "2023-08-15T10:00:00",
  "updated_at": "2023-08-15T10:20:00"
}
```

**Коды ответов:**
- `200 OK`: Успешное обновление
- `400 Bad Request`: Категория с таким именем уже существует
- `401 Unauthorized`: Требуется аутентификация
- `404 Not Found`: Категория не найдена

#### DELETE /categories/{category_id}

**Назначение:** Удаляет категорию. Треды из этой категории остаются, но их category_id устанавливается в NULL.

**Требуется аутентификация:** Да

**Параметры пути:**
- `category_id` - ID категории

**Коды ответов:**
- `204 No Content`: Успешное удаление
- `401 Unauthorized`: Требуется аутентификация
- `404 Not Found`: Категория не найдена

### Промпты

#### GET /prompts

**Назначение:** Возвращает список сохраненных промптов пользователя с фильтрацией.

**Требуется аутентификация:** Да

**Параметры запроса:**
- `skip` (int, опционально): Пропустить указанное количество промптов. По умолчанию 0.
- `limit` (int, опционально): Максимальное количество возвращаемых промптов. По умолчанию 100.
- `category_id` (int, опционально): Фильтр по ID категории.
- `is_favorite` (bool, опционально): Фильтр по избранным промптам.
- `search` (string, опционально): Текст для поиска в названиях и содержании промптов.

**Пример ответа:**
```json
[
  {
    "id": 42,
    "user_id": 123,
    "title": "Генерация идей для статьи",
    "content": "Предложи 5 креативных идей для статьи на тему {тема}",
    "description": "Промпт для быстрой генерации идей для контент-плана",
    "category_id": 5,
    "is_favorite": false,
    "created_at": "2023-08-15T14:30:45",
    "updated_at": "2023-08-16T09:12:33",
    "category": {
      "id": 5,
      "name": "Контент-маркетинг",
      "description": "Промпты для создания контента",
      "color": "#27AE60"
    }
  }
]
```

**Коды ответов:**
- `200 OK`: Успешный запрос
- `401 Unauthorized`: Требуется аутентификация

#### GET /prompts/{prompt_id}

**Назначение:** Возвращает сохраненный промпт по ID.

**Требуется аутентификация:** Да

**Параметры пути:**
- `prompt_id` - ID промпта

**Пример ответа:**
```json
{
  "id": 42,
  "user_id": 123,
  "title": "Генерация идей для статьи",
  "content": "Предложи 5 креативных идей для статьи на тему {тема}",
  "description": "Промпт для быстрой генерации идей для контент-плана",
  "category_id": 5,
  "is_favorite": false,
  "created_at": "2023-08-15T14:30:45",
  "updated_at": "2023-08-16T09:12:33",
  "category": {
    "id": 5,
    "name": "Контент-маркетинг",
    "description": "Промпты для создания контента",
    "color": "#27AE60"
  }
}
```

**Коды ответов:**
- `200 OK`: Успешный запрос
- `401 Unauthorized`: Требуется аутентификация
- `404 Not Found`: Промпт не найден

#### POST /prompts

**Назначение:** Создает новый сохраненный промпт.

**Требуется аутентификация:** Да

**Тело запроса:**
```json
{
  "title": "План маркетингового исследования",
  "content": "Проанализируй целевую аудиторию продукта {название_продукта} и предложи стратегию продвижения в социальных сетях.",
  "description": "Промпт для создания маркетингового плана по продвижению продукта",
  "category_id": 3,
  "is_favorite": true
}
```

**Пример ответа:**
```json
{
  "id": 43,
  "user_id": 123,
  "title": "План маркетингового исследования",
  "content": "Проанализируй целевую аудиторию продукта {название_продукта} и предложи стратегию продвижения в социальных сетях.",
  "description": "Промпт для создания маркетингового плана по продвижению продукта",
  "category_id": 3,
  "is_favorite": true,
  "created_at": "2023-08-16T11:30:00",
  "updated_at": "2023-08-16T11:30:00",
  "category": {
    "id": 3,
    "name": "Маркетинг",
    "description": "Промпты для маркетинговых задач",
    "color": "#F39C12"
  }
}
```

**Коды ответов:**
- `201 Created`: Промпт успешно создан
- `401 Unauthorized`: Требуется аутентификация
- `404 Not Found`: Категория не найдена

#### PUT /prompts/{prompt_id}

**Назначение:** Обновляет информацию о сохраненном промпте.

**Требуется аутентификация:** Да

**Параметры пути:**
- `prompt_id` - ID промпта

**Тело запроса:**
```json
{
  "title": "Улучшенный план исследования",
  "content": "Разработай детальный план исследования по теме {тема_исследования}, включающий методологию, ключевые вопросы и ожидаемые результаты.",
  "description": "Обновленная версия промпта для научных исследований",
  "category_id": 2,
  "is_favorite": true
}
```

**Пример ответа:**
```json
{
  "id": 42,
  "user_id": 123,
  "title": "Улучшенный план исследования",
  "content": "Разработай детальный план исследования по теме {тема_исследования}, включающий методологию, ключевые вопросы и ожидаемые результаты.",
  "description": "Обновленная версия промпта для научных исследований",
  "category_id": 2,
  "is_favorite": true,
  "created_at": "2023-08-15T14:30:45",
  "updated_at": "2023-08-16T12:00:00",
  "category": {
    "id": 2,
    "name": "Наука",
    "description": "Промпты для научных задач",
    "color": "#3498DB"
  }
}
```

**Коды ответов:**
- `200 OK`: Успешное обновление
- `401 Unauthorized`: Требуется аутентификация
- `404 Not Found`: Промпт или категория не найдены

#### DELETE /prompts/{prompt_id}

**Назначение:** Удаляет сохраненный промпт.

**Требуется аутентификация:** Да

**Параметры пути:**
- `prompt_id` - ID промпта

**Коды ответов:**
- `204 No Content`: Успешное удаление
- `401 Unauthorized`: Требуется аутентификация
- `404 Not Found`: Промпт не найден

### Настройки моделей

#### GET /model_preferences/available

**Назначение:** Возвращает список доступных моделей из всех настроенных провайдеров.

**Требуется аутентификация:** Да

**Пример ответа:**
```json
{
  "models": [
    {
      "provider_id": 1,
      "id": 1,
      "code": "gpt-4",
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
      "provider_id": 2,
      "id": 5,
      "code": "claude-3-opus",
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

**Коды ответов:**
- `200 OK`: Успешный запрос
- `401 Unauthorized`: Требуется аутентификация

#### GET /model_preferences/preferences

**Назначение:** Возвращает список настроек моделей пользователя.

**Требуется аутентификация:** Да

**Пример ответа:**
```json
[
  {
    "id": 15,
    "user_id": 123,
    "provider_id": 1,
    "model_id": 1,
    "max_tokens": 1500,
    "temperature": 0.7,
    "system_prompt": "Ты аналитик данных, помогающий интерпретировать сложные наборы данных и строить прогнозы",
    "is_default": false,
    "created_at": "2023-08-10T12:30:45",
    "updated_at": "2023-08-15T18:22:33"
  }
]
```

**Коды ответов:**
- `200 OK`: Успешный запрос
- `401 Unauthorize