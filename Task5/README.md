# Task 5 — GraphQL API для client-info

Файл схемы: `schema.graphql`

## Соответствие REST → GraphQL

| REST | GraphQL |
|------|---------|
| `GET /clients/{id}` | `query { client(id) { id name age } }` |
| `GET /clients/{id}/documents` | `query { clientDocuments(clientId) { ... } }` или `client(id) { documents { ... } }` |
| `GET /clients/{id}/relatives` | `query { clientRelatives(clientId) { ... } }` или `client(id) { relatives { ... } }` |

Один запрос может выбрать только нужные поля и вложенные коллекции — без over-fetching и без N отдельных REST-вызовов.
