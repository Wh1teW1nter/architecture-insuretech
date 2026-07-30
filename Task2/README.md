# Task 2 — Dynamic scaling (Minikube + HPA)

## Результаты тестирования

### Часть 1 — HPA по памяти (80%, max 10 replicas)

**Команды:**
```bash
minikube start
minikube addons enable metrics-server
minikube image build -t insuretech-test-app:4 Task2
kubectl apply -f Task2/deployment.yaml
kubectl apply -f Task2/service.yaml
kubectl apply -f Task2/hpa-memory.yaml
kubectl apply -f Task2/load-generator.yaml   # in-cluster нагрузка
```

**Результат:** HPA масштабировал Deployment с **1 → 2** реплик при `memory: 89%/80%`.

Доказательства: `artifacts/hpa-memory-describe.txt`, `artifacts/hpa-memory-watch-summary.txt`, `artifacts/pods-memory-final.txt`

### Часть 2 — HPA по RPS (Prometheus + prometheus-adapter)

**Команды:**
```bash
kubectl apply -f Task2/prometheus.yaml
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm upgrade --install prometheus-adapter prometheus-community/prometheus-adapter \
  -n monitoring -f Task2/prometheus-adapter-values.yaml
kubectl delete hpa insuretech-app-hpa-memory
kubectl scale deployment insuretech-app --replicas=1
kubectl apply -f Task2/hpa-rps.yaml
kubectl apply -f Task2/load-generator.yaml
```

**Prometheus UI:** `kubectl port-forward -n monitoring svc/prometheus 9090:9090` → http://localhost:9090

**Результат:** HPA масштабировал Deployment с **1 → 4** реплик при `5657m/5` (~5.6 RPS на pod, target 5).

Доказательства: `artifacts/hpa-rps-describe.txt`, `artifacts/prometheus-targets.json`, `artifacts/custom-metric-http_requests_rps.json`

## Файлы

| Файл | Назначение |
|------|------------|
| `deployment.yaml` | Deployment (replicas=1, limit 30Mi) |
| `service.yaml` | Service ClusterIP |
| `hpa-memory.yaml` | HPA по memory 80% |
| `hpa-rps.yaml` | HPA по custom metric http_requests_rps |
| `prometheus.yaml` | Prometheus + scrape config |
| `prometheus-adapter-values.yaml` | Helm values для adapter |
| `load-generator.yaml` | Job для in-cluster нагрузки |
| `locustfile.py` | Locust-сценарий (альтернатива) |
| `app.py`, `Dockerfile` | Тестовое приложение |

## Locust (опционально)

```bash
kubectl port-forward svc/insuretech-app 18080:80
cd Task2
locust -f locustfile.py --host http://localhost:18080
```

UI: http://localhost:8089
