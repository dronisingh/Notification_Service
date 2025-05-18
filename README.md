# 📢 Notification Service System

A microservice-based **Notification Delivery System** using **FastAPI**, **RabbitMQ**, and **PostgreSQL**. It supports **Email**, **SMS**, and **In-App** notifications, includes **retry logic**, and is fully **Dockerized** for smooth local development.

---

## 🚀 Features

- ✅ Send notifications via REST API
- ✅ Supports Email, SMS, and In-App delivery
- ✅ Retry logic with exponential backoff on failure
- ✅ RabbitMQ queue with support for headers (`x-retries`)
- ✅ Docker + Docker Compose setup
- ✅ PostgreSQL for storing notification records
- ✅ Swagger UI for testing API endpoints

---

## 🧱 Tech Stack

| Component     | Tech               |
|---------------|--------------------|
| Backend       | FastAPI (Python)   |
| Messaging     | RabbitMQ           |
| Database      | PostgreSQL         |
| Queue Client  | `pika` (Python)    |
| Containerization | Docker + Compose |
| Async Worker  | Custom Python script |

---

## 📂 Project Structure

```
## 📁 Project Structure

NOTIFICATION_SERVICE/
├── .venv/                           # Python virtual environment
├── app/
│   ├── __pycache__/
│   ├── database.py                  # Database connection/config
│   ├── main.py                      # FastAPI app entry point
│   ├── models/
│   │   └── __init__.py
│   ├── routes/
│   │   └── __init__.py              # API routing setup
│   └── services/
│       ├── __pycache__/
│       ├── email.py                 # Email service logic
│       ├── in_app.py                # In-app notification logic
│       └── sms.py                   # SMS service logic
├── workers/
│   ├── __pycache__/
│   ├── __init__.py
│   ├── consumer.py                  # Consumes messages from queue
│   ├── rabbitmq_client.py          # RabbitMQ client setup
│   └── worker.py                   # Worker process logic
├── include/
├── lib/
├── Scripts/
├── .gitignore
├── docker-compose.yml              # Docker Compose setup
├── Dockerfile                      # Dockerfile for container
├── README.md                       # Project documentation
└── requirements.txt                # Project dependencies
```

---

## ⚙️ Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/dronisingh/notification_service.git
cd notification_service
```

### 2. Start all services using Docker

```bash
docker-compose up --build
```

This will:
- Start **FastAPI app** on `localhost:8000`
- Start **RabbitMQ** on port `5672` and UI at `localhost:15672`
- Start **PostgreSQL** on port `5432`

> You can access the RabbitMQ UI at: [http://localhost:15672](http://localhost:15672)  
> Default user/pass: `guest / guest`

### 3. Run the Worker (in a separate terminal)

```bash
# From project root
python -m app.workers.worker
```
### 4. Run Uvicorn (if not using Docker Compose for FastAPI)

```bash
uvicorn main:app --reload
```

---

## 🧪 API Usage

### ▶️ POST `/notify`

Send a notification.

**Request Body:**

```json
{
  "user_id": 12,
  "type": "email",  // "email" | "sms" | "in_app"
  "message": "Hello user!"
}
```

### 🔍 GET `/notifications/{user_id}`

Retrieve all notifications for a given user.

---

## 📘 Example

To simulate a failure and trigger retry logic, send:

```json
{
  "user_id": 12,
  "type": "email",
  "message": "force_fail"
}
```

Retries will occur with exponential backoff (1s, 2s, 4s), then be discarded after 3 failures.

---

## ⚠️ Assumptions

- Queue name is hardcoded as `notifications`
- `x-retries` RabbitMQ header is used to track retry attempts
- Queue must match `durable` flag across producer and consumer
- Only simulates actual delivery (no third-party APIs connected)

---

## 📚 Documentation

Once running, you can access the **Swagger API docs** at:

👉 [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 👨‍💻 Author

- **Name:** Droni Singh
- **GitHub:** [dronisingh](https://github.com/dronisingh)  
- **Email:** droni1603@gmail.com

---


## 📜 License

MIT License – Use freely, improve freely!
