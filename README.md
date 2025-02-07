# URL Shortener

A simple and efficient URL shortening service built with Django and Django REST Framework. This service allows users to shorten long URLs, track the number of times they are accessed, and manage their URLs through a RESTful API.

## Features

- Shorten long URLs
- Retrieve original URLs from shortened URLs
- Track the number of times a shortened URL has been accessed
- Create, retrieve, update, and delete shortened URLs
- Use Redis as cache for improved performance

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/urlshortener.git
   cd urlshortener
   ```

2. **Create a virtual environment:**

   ```bash
   python -m venv myenv
   source myenv/bin/activate  # On Windows use `myenv\Scripts\activate`
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   Create a `.env` file in the root of your project and add the necessary environment variables:

   ```env
   DATABASE_URL=postgres://user:password@host:port/dbname
   DJANGO_SECRET_KEY=your_secret_key
   REDIS_URL=redis://your_redis_host:your_redis_port/1
   ```

5. **Apply migrations:**

   ```bash
   python manage.py makemigrations && python manage.py migrate
   ```

6. **Create a superuser:**

   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

## Database Configuration

You can configure your project to use different databases by setting the `DATABASE_URL` environment variable in your `.env` file.

### PostgreSQL

To use PostgreSQL as your database, set the `DATABASE_URL` like this:

```env
DATABASE_URL=postgres://user:password@host:port/dbname
```

### SQLite

To use SQLite as your database, set the `DATABASE_URL` like this:

```env
DATABASE_URL=sqlite:///db.sqlite3
```

But by default Django use SQLite...

## Cache Configuration

Redis is used as the cache for this project. Make sure to set the `REDIS_URL` environment variable in your `.env` file:

```env
REDIS_URL=redis://your_redis_host:your_redis_port/1
```

## Usage

### Endpoints

- **Create Short URL:**

  ```http
  POST /shorten/
  Content-Type: application/json

  {
    "long_url": "https://www.example.com/some/long/url"
  }
  ```

- **Retrieve Original URL:**

  ```http
  GET /shorten/<short_url>/
  ```

- **Update Short URL:**

  ```http
  PUT /shorten/<short_url>/
  Content-Type: application/json

  {
    "long_url": "https://www.example.com/some/updated/url"
  }
  ```

- **Delete Short URL:**

  ```http
  DELETE /shorten/<short_url>/
  ```

- **Redirect to Original URL:**
  ```http
  GET /<short_url>/
  ```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

This project was inspired and guided by the [URL Shortening Service Project](https://roadmap.sh/projects/url-shortening-service) from [roadmap.sh](https://roadmap.sh/). Their comprehensive guide provided valuable insights and structure for developing this URL shortening service.
