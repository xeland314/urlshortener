# URL Shortener

A simple and efficient URL shortening service built with Django and Django REST Framework. This service allows users to shorten long URLs, track the number of times they are accessed, and manage their URLs through a RESTful API.

## Technologies Used

- **Backend:** Django, Django REST Framework
- **Database:** PostgreSQL (recommended), SQLite (default)
- **Cache/Broker:** Redis
- **Asynchronous Tasks:** Celery
- **Frontend:** HTML, Tailwind CSS, HTMX

## Features

- Shorten long URLs
- Retrieve original URLs from shortened URLs
- Track the number of times a shortened URL has been accessed
- Create, retrieve, update, and delete shortened URLs via API
- **User Authentication:** Register, login, and logout functionality.
- **User-Specific URLs:** Shortened URLs can be associated with authenticated users.
- **Permissions:** Only the owner or a superuser can modify/delete a user's URL.
- **Interactive Dashboard:** Authenticated users can manage their URLs (delete, change password, regenerate token) directly from the homepage using HTMX.
- **URL Expiration:**
    - Anonymous URLs expire and are deleted after a set time.
    - User-owned URLs expire and are deactivated (marked inactive) after a set time.
- **Background Tasks:** Uses Celery for asynchronous operations like URL expiration.
- **Customizable Forms:** Styled Django forms with Tailwind CSS.
- Use Redis as cache for improved performance

## Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/yourusername/urlshortener.git
    cd urlshortener
    ```

2.  **Create a virtual environment and install dependencies (using `uv`):**

    ```bash
    uv venv
    source .venv/bin/activate # On Windows use `.venv\Scripts\activate`
    uv pip install -r requirements.txt
    ```

3.  **Configure environment variables:**
    Create a `.env` file in the root of your project and add the necessary environment variables:

    ```env
    DATABASE_URL=sqlite:///db.sqlite3
    SECRET_KEY=your_django_secret_key
    REDIS_LOCATION=redis://127.0.0.1:6379/0 # For Celery broker and result backend, and Django cache
    ```

4.  **Apply migrations:**

    ```bash
    python manage.py makemigrations && python manage.py migrate
    ```

5.  **Create a superuser (optional, but recommended for admin access):**

    ```bash
    python manage.py createsuperuser
    ```

6.  **Install Node.js dependencies for frontend:**

    ```bash
    npm install
    ```

7.  **Build Tailwind CSS:**

    ```bash
    npm run build:css
    ```
    For development, you can use `npm run watch:css` to automatically recompile CSS on changes.

## Running the Application

To run the full application, you need to start the Django development server, a Redis server, and Celery workers.

1.  **Start Redis Server:**
    Ensure you have a Redis server running. If you have Docker, you can run:
    ```bash
    docker run -d -p 6379:6379 redis/redis-stack-server:latest
    ```

2.  **Start Celery Worker:**
    In a new terminal, from the project root:
    ```bash
    celery -A urlshortener worker -l info
    ```

3.  **Start Celery Beat (for scheduled tasks like URL expiration):**
    In another new terminal, from the project root:
    ```bash
    celery -A urlshortener beat -l info
    ```

4.  **Run the Django Development Server:**
    In your main terminal:
    ```bash
    python manage.py runserver
    ```

Access the application at `http://127.0.0.1:8000/`.

## Usage

-   **Homepage (`/`):** Serves as an interactive dashboard. Authenticated users can manage their URLs. Unauthenticated users can shorten URLs.
-   **Register (`/register/`):** Create a new user account.
-   **Login (`/login/`):** Log in to an existing account.
-   **Logout (`/logout/`):** Log out of the current session.
-   **Admin Panel (`/admin/`):** Access the Django administration interface. Users must have `is_staff=True` to access. Superusers see all URLs; staff users see only their own.

### API Endpoints (for direct API interaction or advanced usage)

-   **Create Short URL:** `POST /shorten/`
-   **List Short URLs:** `GET /shorten/`
-   **Retrieve/Update/Delete Short URL:** `GET/PUT/PATCH/DELETE /shorten/<short_url>/`
-   **Redirect to Original URL:** `GET /<short_url>/`

## Documentation

For more detailed information on specific components and configurations, refer to the `docs/` directory:

-   [`docs/frontend.md`](docs/frontend.md): Frontend setup with Tailwind CSS and HTMX.
-   [`docs/celery.md`](docs/celery.md): Celery configuration and task management.
-   [`docs/deployment.md`](docs/deployment.md): General deployment considerations.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE](LICENSE) file for details.

## Acknowledgements

This project was inspired and guided by the [URL Shortening Service Project](https://roadmap.sh/projects/url-shortening-service) from [roadmap.sh](https://roadmap.sh/). Their comprehensive guide provided valuable insights and structure for developing this URL shortening service.