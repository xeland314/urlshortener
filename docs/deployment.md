# Deployment Considerations

This document outlines important considerations when deploying the URL Shortener application to a production environment.

## Environment Variables

All sensitive information and environment-specific configurations should be managed using environment variables. A `.env` file is used for local development, but for production, you should set these variables directly in your hosting environment.

Key environment variables:

-   `DATABASE_URL`: Connection string for your PostgreSQL or other production database.
-   `SECRET_KEY`: A strong, unique secret key for Django. **Never hardcode this in production.**
-   `REDIS_LOCATION`: URL for your Redis server, used by Django's cache and Celery.
-   `DEBUG`: Set to `False` in production. This disables debug mode, which is crucial for security and performance.
-   `ALLOWED_HOSTS`: A comma-separated list of domain names that your Django site can serve. E.g., `ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com`.
-   `CORS_ORIGIN_WHITELIST`: If you have a separate frontend application, list its origins here.
-   `CSRF_TRUSTED_ORIGINS`: List trusted origins for CSRF protection.

## Static Files

In production, Django's development server (`runserver`) should **not** be used to serve static files. A dedicated web server (like Nginx or Apache) or a CDN should handle static file serving.

1.  **Collect Static Files:**

    Before deployment, you need to collect all static files into the `STATIC_ROOT` directory:

    ```bash
    python manage.py collectstatic
    ```

    This will gather all static files from your apps and `STATICFILES_DIRS` into the directory specified by `STATIC_ROOT` in `urlshortener/settings.py` (which is `staticfiles/` by default).

2.  **Web Server Configuration:**

    Configure your web server (e.g., Nginx) to serve the contents of `STATIC_ROOT` at `STATIC_URL` (`/static/`).

    Example Nginx configuration snippet:

    ```nginx
    location /static/ {
        alias /path/to/your/project/staticfiles/;
    }
    ```

## Celery Deployment

For production, Celery workers and Celery Beat should be run as persistent background processes, often managed by a process supervisor like `systemd`, `Supervisor`, or `pm2`.

-   **Worker:** Run one or more Celery worker instances.
-   **Beat:** Run a single instance of Celery Beat.

Ensure your Redis server is robust and properly secured for production use.

## Database

Use a robust production-ready database like PostgreSQL. Configure `DATABASE_URL` accordingly.

## Gunicorn/uWSGI

Use a WSGI HTTP server like [Gunicorn](https://gunicorn.org/) or [uWSGI](https://uwsgi-docs.readthedocs.io/en/latest/) to serve your Django application in production. These servers provide better performance, stability, and security than Django's built-in development server.

Example Gunicorn command:

```bash
gunicorn urlshortener.wsgi:application --bind 0.0.0.0:8000
```

## HTTPS

Always use HTTPS in production to encrypt communication between your users and the server. This typically involves configuring your web server (Nginx/Apache) with SSL certificates.
