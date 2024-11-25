# IP Scanner with Celery and Webhook Notifications

This project implements an IP scanning system using **Django**, **Celery**, **Redis**, and **WebSocket**. It validates IP addresses, fetches IP information from the `ipinfo.io` API, processes the data asynchronously with Celery, and notifies the frontend through webhooks and WebSocket.

## Features:
- Validate a list of IP addresses.
- Fetch IP information from [ipinfo.io](https://ipinfo.io/).
- Asynchronous IP scanning using Celery.
- Notify frontend about task completion via webhooks and WebSocket.

---

## Installation

### Clone the repository:
```bash
git clone https://github.com/Amr1997/dphish-IP-Adress-Reputation-Scanning-.git
cd ip-scanner
```

### Set up virtual environment:
1. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
2. Activate the virtual environment:
   - On **Windows**:
     ```bash
     venv\Scripts\activate

### Install dependencies:
1. Install all required dependencies from `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

#### Dependencies:
- Django
- Django Rest Framework
- Celery
- Redis
- Channels
- Requests

### Run Redis:
1. **Install Redis** if not already installed from [here](https://redis.io/download).
2. Start the Redis server:
   ```bash
   redis-server
   ```

### Database setup:
1. **SQLite** (default):
   The project uses SQLite by default for development. You can skip this step if you're using SQLite.

2. **PostgreSQL** (optional):
   For production, configure PostgreSQL in `settings.py`. Make sure PostgreSQL is installed and running.

3. Run migrations to set up the database:
   ```bash
   python manage.py migrate
   ```

---

## Running the project

### Start the Django development server:
1. Run the Django server:
   ```bash
   python manage.py runserver
   ```
   This will start the development server at `http://127.0.0.1:8000/`.

### Start the Celery worker:
In a separate terminal window, start Celery to process tasks asynchronously:
```bash
celery -A ip_scanner worker --loglevel=info
```

---

## API Endpoints

### `POST /scanner/scan/`
This endpoint allows you to submit a list of IP addresses for scanning.

**Request**:
```json
{
    "ips": ["1.1.1.1", "8.8.8.8"]
}
```

**Response (if all IPs are valid)**:
```json
{
    "message": "Tasks initiated",
    "tasks": {
        "1.1.1.1": 123,
        "8.8.8.8": 124
    }
}
```

**Response (if some IPs are invalid)**:
```json
{
    "message": "Tasks initiated, but the following IPs were invalid",
    "invalid_ips": ["999.999.999.999"],
    "tasks": {
        "1.1.1.1": 123,
        "8.8.8.8": 124
    }
}
```

- **Success Response**: If the IPs are valid, the system creates tasks for each valid IP and returns their task IDs.
- **Failure Response**: If any of the IPs are invalid, they will be included in the response along with valid IPs and their task IDs.

---

### `POST /scanner/webhook/`
This endpoint allows you to send task completion details to a frontend via a webhook URL.

**Request**:
```json
{
    "task_id": 1,
    "webhook_url": "https://your-webhook-url.com/api/notify/"
}
```

**Response**:
```json
{
    "message": "Webhook notification sent successfully"
}
```

- **Webhook Notification**: Once the task is completed, the system will send a webhook notification to the provided URL with the task status and details.
  
---

## Example requests and responses

### `POST /scanner/scan/`

**Request**:
```json
{
    "ips": ["1.1.1.1", "8.8.8.8", "999.999.999.999"]
}
```

**Response**:
```json
{
    "message": "Tasks initiated, but the following IPs were invalid",
    "invalid_ips": ["999.999.999.999"],
    "tasks": {
        "1.1.1.1": 123,
        "8.8.8.8": 124
    }
}
```

- **Invalid IP**: `999.999.999.999` is invalid, so it's included in the `invalid_ips` list.
- **Valid IPs**: The valid IPs `1.1.1.1` and `8.8.8.8` have associated task IDs `123` and `124`, respectively.

---

### `POST /scanner/webhook/`

**Request**:
```json
{
    "task_id": 1,
    "webhook_url": "https://webhook.site/your-generated-url"
}
```

**Response**:
```json
{
    "message": "Webhook notification sent successfully"
}
```

- **Webhook Response**: The webhook notification will be sent to the specified URL (`https://webhook.site/your-generated-url`).

---

## Troubleshooting

- **Permission Errors**: On Windows, you might encounter permission issues when using Celery. Use the `solo` pool for development:
  ```bash
  celery -A ip_scanner worker --loglevel=info --pool=solo
  ```

- **Invalid IPs**: If the provided IPs are not valid, they will be returned in the `invalid_ips` field in the response.

- **Redis Connection**: Ensure Redis is running properly and the server can connect to it.
