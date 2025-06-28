# Celery Configuration and Usage

This project uses [Celery](https://docs.celeryq.dev/en/stable/) for asynchronous task processing, primarily for managing URL expiration.

## Prerequisites

Celery requires a message broker to send and receive messages (tasks). This project is configured to use [Redis](https://redis.io/) as the broker and result backend.

Ensure you have a Redis server running and accessible. You can run Redis using Docker:

```bash
docker run -d -p 6379:6379 redis/redis-stack-server:latest
```

## Configuration

Celery is configured in `urlshortener/settings.py` and initialized in `urlshortener/celery.py`.

-   `CELERY_BROKER_URL`: Specifies the URL of your Redis broker.
-   `CELERY_RESULT_BACKEND`: Specifies the URL where task results are stored.

These are typically set via the `REDIS_LOCATION` environment variable.

## Running Celery

To enable asynchronous tasks, you need to start Celery workers and, for scheduled tasks, Celery Beat.

1.  **Start Celery Worker:**

    The worker executes the tasks. Open a new terminal in your project root and run:

    ```bash
    celery -A urlshortener worker -l info
    ```

    The `-A urlshortener` flag tells Celery to look for a Celery application instance in the `urlshortener` module.
    The `-l info` flag sets the logging level to info, showing more details about task execution.

2.  **Start Celery Beat (for scheduled tasks):**

    Celery Beat is a scheduler that periodically sends tasks to the Celery worker queue. This is essential for tasks like checking URL expirations.

    Open another new terminal in your project root and run:

    ```bash
    celery -A urlshortener beat -l info
    ```

    **Note:** You should only run one instance of Celery Beat. If you need to run multiple workers, that's fine, but only one Beat.

## URL Expiration Tasks

The `shortener/tasks.py` file defines the `expire_shortener_url` task.

-   When a `Shortener` object is created or updated with an `expires_at` date, this task is scheduled to run at that specific time.
-   If the expired URL belongs to an anonymous user (`user is None`), the URL is **deleted**.
-   If the expired URL belongs to an authenticated user, the URL is **deactivated** (`is_active` is set to `False`), but not deleted. This allows users to see their expired URLs in their dashboard.

## Troubleshooting Celery

-   **Tasks not running:** Ensure both the Celery worker and Celery Beat are running.
-   **Connection issues:** Verify your `REDIS_LOCATION` in `.env` and ensure your Redis server is accessible.
-   **Task failures:** Check the logs of your Celery worker for detailed error messages.
