# VK SQL API for VS Code

Модульный проект на FastAPI + DuckDB.

Что сделано:
- базы всегда сохраняются в папку `data` в корне проекта
- добавен UI на главной странице `/`
- добавено скачивание базы через `GET /api/db/download/{db_name}`
- если баз еще нет, кнопка скачивания блокируется
- убраны 404 для `favicon` и `apple-touch-icon`

## Запуск

```bash
python -m venv .venv
```

### Windows
```bash
.venv\Scripts\activate
```

### macOS / Linux
```bash
source .venv/bin/activate
```

Установка зависимостей:

```bash
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

Создайте `.env` на основе `.env.example` и укажите VK token:

```env
VK_TOKEN=ваш_токен
```

Запуск:

```bash
uvicorn app.main:app --reload
```

Открыть:
- `http://127.0.0.1:8000/` — главная страница
- `http://127.0.0.1:8000/docs` — Swagger

## Создание базы

Через Swagger вызовите `POST /api/collect`.

Пример body:

```json
{
  "keyword": "искусственный интеллект",
  "period": "2025",
  "max_posts": 100,
  "load_comments": true,
  "comments_per_post_limit": 100
}
```

После выполнения файл появится в папке:

```text
data/
```

Пример имени:

```text
data/vk_iskusstvennyy_intellekt_2025.duckdb
```

## API

- `POST /api/collect` — собрать данные и создать `.duckdb`
- `GET /api/db/list` — список баз
- `GET /api/db/download/{db_name}` — скачать базу
- `GET /api/db/summary?name=...` — сводка по базе

## Важное замечание

Если VK API вернет ошибку из-за токена или лимита, файл базы все равно будет создан с таблицами в папке `data`, потому что схема и файл инициализируются сразу при запуске сбора.
