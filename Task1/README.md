# Task 1 — Технологическая архитектура to-be

Файл схемы: `InureTech_технологическая архитектура_to-be.drawio`

Открыть в [diagrams.net](https://app.diagrams.net) / draw.io.

## Ключевые решения (также на схеме)

| Аспект | Решение |
|--------|---------|
| Масштабирование | Горизонтальное для приложений (HPA/CA); вертикальное точечно для БД |
| Зоны доступности | 3 AZ в `ru-central1` (a/b/d) |
| Kubernetes | Один региональный Managed Kubernetes + node groups в каждой AZ |
| Балансировка | Cloud DNS → CDN (статика) + ALB L7 (API); health checks `/healthz` |
| Failover | Active-Active через ALB; DNS failover на резервный endpoint |
| БД | Managed PostgreSQL HA: master + sync + async; WAL/backup в Object Storage |
| Шардирование | Не применяется (~50 GB) |
| Latency по РФ | Yandex CDN |
| Цели | SLA 99.9%, RTO ≤ 45 мин, RPO ≤ 15 мин |
