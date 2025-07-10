
# One-Time Secret App

A secure API for sharing secrets that can only be viewed once, built with FastAPI, SQLAlchemy, and PostgreSQL. Secrets are encrypted and stored in a PostgreSQL database, and can be retrieved only a single time.

## Features
- Store secrets securely with encryption
- Retrieve secrets only once (self-destruct after reading)
- RESTful API built with FastAPI
- PostgreSQL database for persistence
- Dockerized for easy deployment

## Getting Started

### 1. Clone the repository

git clone <repo-url>
cd one-time-secret-app


### 2. Configure Environment Variables
Edit the `.env` file to set your encryption key and database credentials:

ENCRYPTION_KEY=your-32-byte-base64-key
POSTGRES_USER=postgres
POSTGRES_PASSWORD=yourpassword
POSTGRES_DB=secrets


### 3. Start the Application

docker compose up --build

The API will be available at `http://localhost:8000`.

### 4. API Usage
- Visit `http://localhost:8000/docs` for interactive API documentation (Swagger UI).

## Project Structure

app/
  crypto.py      # Encryption utilities
  db.py          # Database connection and models
  main.py        # FastAPI app entrypoint
  models.py      # SQLAlchemy models
  routes.py      # API routes
  ...
docker-compose.yml
Dockerfile
requirements.txt
.env


## Running Tests
Add your tests in the `tests/` directory and run them as needed.

## License
MIT License

