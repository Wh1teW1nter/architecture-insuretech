# Task 2 — Dynamic scaling (Minikube + HPA)

## Важно про окружение
Сейчас Minikube не стартует, потому что Docker Desktop Linux Engine недоступен.
Для продолжения включите Docker Desktop (или договоритесь со мной — пересоздам Minikube на другом драйвере).

## 1) Подготовка кластера
```bash
minikube start
minikube addons enable metrics-server
```

## 2) Сборка образа тестового приложения
```bash
# собрать Docker-образ прямо в окружение minikube (нужен доступ к Docker)
minikube image build -t insuretech-test-app:1 . -- --file Task2\Dockerfile
```

## 3) Deployment / Service / HPA (memory)
```bash
kubectl apply -f Task2\deployment.yaml
kubectl apply -f Task2\service.yaml
kubectl apply -f Task2\hpa-memory.yaml
```

Проверка:
```bash
kubectl get pods -w
kubectl get hpa -w
```

Открыть приложение:
```bash
minikube service insuretech-app --url
```

## 4) Нагрузка (Locust)
Locustfile: `Task2/locustfile.py`

Запуск (в отдельном терминале):
```bash
cd Task2
locust -f locustfile.py
```

UI: `http://localhost:8089`

## 5) Prometheus и HPA по RPS
### 5.1 Prometheus
```bash
kubectl apply -f Task2/prometheus.yaml
```

Проверить метрики:
```bash
kubectl port-forward -n monitoring deploy/prometheus 9090:9090
# затем открыть Prometheus: http://localhost:9090
```

### 5.2 prometheus-adapter (для HPA custom metrics)
```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm install prometheus-adapter prometheus-community/prometheus-adapter \
  -n monitoring --create-namespace \
  -f Task2/prometheus-adapter-values.yaml
```

### 5.3 HPA по RPS
```bash
kubectl apply -f Task2/hpa-rps.yaml
```

## 6) Что нужно положить в репозиторий (Task2)
- Логи/скриншоты, подтверждающие рост `replicas` для:
  - HPA memory
  - HPA RPS (http_requests_rps)

Сейчас пока этот блок будет заполнен после запуска кластера и выполнения тестов.

