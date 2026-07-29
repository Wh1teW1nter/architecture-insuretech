# Task 4 — Проектирование продажи ОСАГО

Схема: `InsureTech_C4_OSAGO_to-be.drawio` (доработка C4 из Task3).

## Решения

### 1. osago-aggregator — своё хранилище?
**Да.** `osago-db` (PostgreSQL): `quoteId`, id заявок в СК, статус polling, deadline 60с, полученные офферы.

Нужно, потому что сервис в **нескольких репликах**: состояние опроса должно быть общим, иначе при рестарте/балансировке теряется прогресс.

### 2. API osago-aggregator ↔ core-app
**Event Streaming (Kafka)**, тот же подход, что для продуктов/тарифов:
| Направление | Topic | Содержимое |
|-------------|-------|------------|
| core-app → aggregator | `osago.quote.requested` | данные заявки (авто, водитель, quoteId) |
| aggregator → core-app | `osago.offer.received` | оффер одной СК (по мере готовности) |
| aggregator → core-app | `osago.quote.completed` / `osago.quote.timeout` | итог сбора (все ответили / 60с) |

Sync REST между ними для happy-path **не используем** (избегаем блокирующего fan-out на 10 СК).

### 3. Web ↔ core-app
| Протокол | Назначение |
|----------|------------|
| **REST** | `POST /api/osago/applications` — создать заявку (202 + id); выбор оффера / оформление |
| **SSE** | `GET /api/osago/applications/{id}/stream` — предложения появляются на UI сразу, как пришли от СК |

SSE отражён отдельной стрелкой на схеме (не REST).

### 4. Паттерны отказоустойчивости
| Паттерн | Где | Зачем |
|---------|-----|-------|
| **Rate Limiting** | вход core-app (Web/B2B); исходящие вызовы osago-aggregator → каждая СК | 2500 concurrent + квоты партнёров |
| **Circuit Breaker** | osago-aggregator → СК (на компанию) | изоляция «больной» СК |
| **Retry** | create/poll к СК (ограниченно, с backoff) | транзиентные сбои |
| **Timeout** | HTTP к СК; общий deadline сбора офферов **60с**; SSE-сессия | требование бизнеса |

На схеме — цветные бейджи (легенда в правом верхнем углу).

### 5. Multi-instance
- Kafka consumer group, key = `quoteId`.
- Состояние опроса в `osago-db`.
- SSE: Redis Pub/Sub по `quoteId` — pod с активным SSE получает оффер независимо от того, какой pod потребил Kafka-событие.
- Transactional Outbox у core-app и osago-aggregator.
