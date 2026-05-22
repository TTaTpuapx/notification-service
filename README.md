# Notification Async Service

Асинхронный сервис для отправки уведомлений (Email, Telegram, SMS) с использованием Flask, RQ (Redis Queue), Redis и PostgreSQL. Проект полностью контейнеризирован и готов к развертыванию одной командой.

## Архитектура и стек технологий

Сервис построен по классической схеме распределенной обработки задач:
1. **Веб-сервер (Flask)** — принимает HTTP-запросы, валидирует входные данные, сохраняет уведомление в базу данных со статусом `queued` и отправляет задачу в брокер сообщений.
2. **Брокер сообщений (Redis)** — выступает в роли хранилища очереди задач.
3. **Фоновый воркер (RQ)** — изолированный процесс, который забирает задачи из Redis, переводит статус в `pending`, имитирует отправку уведомления (вывод в лог) и сохраняет финальный статус (`sent` или `failed`) в БД.
4. **База данных (PostgreSQL)** — реляционная БД для надежного хранения истории уведомлений и их статусов.

---

## Быстрый запуск инфраструктуры

Для запуска всех сервисов, баз данных и воркера одной командой выполните в корне проекта:

```
docker-compose down --volumes && docker-compose up --build
```

После завершения сборки Flask-бэкенд станет доступен по адресу: `http://localhost:5000`

---

## Запуск юнит-тестов

Тесты написаны на базе `pytest` и запускаются в полной изоляции от реальных баз данных и брокера (используется база данных SQLite в памяти `:memory:` и MagicMock-заглушки для сети).

Для запуска тестов выполните:
```
docker-compose run --rm web python -m pytest tests/test_api.py -v -s
```

---

## Примеры cURL запросов для проверки

Проверка работоспособности API:

### 1. Создание уведомления (POST)
```
curl -X POST http://localhost:5000/api/v1/notifications \
  -H "Content-Type: application/json" \
  -d '{
    "type": "email",
    "recipient": "junior@example.com",
    "subject": "Тест ТЗ",
    "message": "Все требования выполнены"
  }'
```
**Ожидаемый ответ (201 Created):**
```json
{"id": "ID", "status": "queued"}
```

### 2. Получение статуса конкретного уведомления (GET)

```bash
curl http://localhost:5000/api/v1/notifications/ID
```
**Ожидаемый ответ (200 OK):**
```json
{"error": null, "id": "ID", "status": "sent"}
```

### 3. Получение списка с пагинацией и фильтрацией (GET)
```bash
curl "http://localhost:5000/api/v1/notifications?status=sent&limit=5&offset=0"
```

### 4. Проверка валидации (POST с некорректными данными)
```bash
curl -X POST http://localhost:5000/api/v1/notifications \
  -H "Content-Type: application/json" \
  -d '{
    "type": "email",
    "recipient": "wrong-email-format",
    "message": "Test"
  }'
```
**Ожидаемый ответ (400 Bad Request):**
```json
{"errors": {"recipient": "Invalid email format"}}
```

---

## Структурированное логирование
Все логи приложения пишутся напрямую в `stdout` в стандартизированном JSON-формате, что упрощает их сбор агрегаторами логов (например, ELK Stack). 

Пример лога при постановке в очередь:
`{"level": "INFO", "module": "notifications", "message": {"event": "notification.queued", "notification_id": "0b3fea77..."}}`

