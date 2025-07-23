
# 🔐 One-Time Secret App

A secure API for sharing secrets that can only be viewed **once**, built with **FastAPI**, **SQLAlchemy**, and **PostgreSQL**. Secrets are encrypted and stored securely, and they self-destruct after being retrieved.

---

## 🚀 Features

- 🔒 Store secrets securely with AES encryption
- 🧨 Self-destruct secrets after one retrieval
- 🔐 Optional password protection
- 🕒 Optional expiration after set time
- 📦 Dockerized for easy setup
- 🛠️ pgAdmin interface for DB access
- 📄 Swagger (OpenAPI) documentation

---

## 🛠️ Getting Started

### 1. Clone the Repository

```bash
git clone <repo-url>
cd one-time-secret-app
```

### 2. Configure Environment Variables

Create and edit a `.env` file in the root directory:

```env
# App settings
ENCRYPTION_KEY=your-32-byte-base64-key

# PostgreSQL settings
POSTGRES_USER=your_pg_user
POSTGRES_PASSWORD=your_pg_password
POSTGRES_DB=secrets

# pgAdmin settings
PGADMIN_DEFAULT_EMAIL=your_email@example.com
PGADMIN_DEFAULT_PASSWORD=your_pgadmin_password
```

> 💡 Use a secure random 32-byte base64 key for `ENCRYPTION_KEY`.

---

### 3. Start the Application

```bash
docker compose up --build
```

- The API will be available at 👉 `http://localhost:8000`
- pgAdmin will be available at 👉 `http://localhost:5050`

Login to pgAdmin using:
- **Email**: `your_email@example.com`
- **Password**: `your_pgadmin_password`

Once inside pgAdmin, you can register the server with:
- **Host**: `db`
- **Username**: `your_pg_user`
- **Password**: `your_pg_password`

---

## 📬 API Usage

### 📤 Create a Secret

```http
POST /secret
```

**Request JSON:**

```json
{
  "secret": "my super secret message",
  "password": "optional-password",
  "expire_after_minutes": 30
}
```

**Response:**

```json
{
  "id": "abc123",
  "url": "http://localhost:8000/secret/abc123"
}
```

---

### 📥 Retrieve a Secret

To retrieve (and destroy) a one-time secret, send a **POST** request to `/secret/retrieve` with the secret `id` and optional `password`.

#### ✅ Without Password

```bash
curl -X POST http://localhost:8000/secret/retrieve \
     -H "Content-Type: application/json" \
     -d '{"id": "abc123"}'
```

#### 🔐 With Password

```bash
curl -X POST http://localhost:8000/secret/retrieve \
     -H "Content-Type: application/json" \
     -d '{"id": "abc123", "password": "mypassword"}'
```

**Response:**

```json
{
  "secret": "your original message"
}
```

> ⚠️ The secret is **permanently deleted** after this request.

---

## 📁 Project Structure

```
one-time-secret-app/
├── alembic/                 # DB migrations
├── app/
│   ├── crypto.py            # Encryption utilities
│   ├── db.py                # DB connection and session
│   ├── main.py              # FastAPI entrypoint
│   ├── models.py            # SQLAlchemy models
│   ├── routes.py            # API endpoints
│   └── schemas.py           # Pydantic models
├── tests/                   # Pytest test suite
├── docker-compose.yml
├── Dockerfile
├── .env
└── requirements.txt
```

---

## 🧪 Running Tests

Make sure your `.env` is set up and run:

```bash
pytest
```

---

## 📣 Contributions

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a new branch: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Commit your changes: `git commit -m "Add feature"`
5. Push to your fork: `git push origin feature/your-feature-name`
6. Open a Pull Request

> 🙌 Feel free to open issues for suggestions, bugs, or improvements!

---

## 📜 License

MIT License
