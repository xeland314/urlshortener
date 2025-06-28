# Frontend Setup (Tailwind CSS & HTMX)

This project uses [Tailwind CSS](https://tailwindcss.com/) for styling and [HTMX](https://htmx.org/) for dynamic frontend interactions without writing much JavaScript.

## Installation

1.  **Install Node.js dependencies:**

    Navigate to the project root and install the necessary packages:

    ```bash
    npm install
    ```

    This will install Tailwind CSS, PostCSS, and Autoprefixer.

## Compiling CSS

Tailwind CSS works by scanning your HTML files for utility classes and generating a corresponding CSS file. You need to compile your CSS whenever you make changes to your templates or Tailwind configuration.

-   **Development Mode (Watch for changes):**

    For continuous development, use the watch command. This will automatically recompile your CSS whenever you save changes to your template files.

    ```bash
    npm run watch:css
    ```

-   **Production Build:**

    For a production deployment, you should generate a minified and optimized CSS file. This command will process your CSS once.

    ```bash
    npm run build:css
    ```

    The compiled CSS will be located at `static/dist/output.css`.

## HTMX Usage

HTMX is included via a CDN in `shortener/templates/shortener/base.html`.

It is used to enhance forms and buttons to make AJAX requests directly from HTML attributes. Key usages include:

-   **URL Shortening Form:** The form on the homepage (`/`) uses `hx-post`, `hx-target`, and `hx-swap` to submit the URL and display the shortened result dynamically without a full page reload.
-   **Dashboard Actions:** Buttons for deleting, changing passwords, and regenerating tokens on the user dashboard (`/`) use HTMX attributes (`hx-delete`, `hx-patch`, `hx-post`, `hx-get`) to perform actions and update individual shortener cards dynamically.

### CSRF Protection with HTMX

For `POST`, `PATCH`, and `DELETE` requests made by HTMX from elements that are not standard HTML forms (e.g., buttons), you need to explicitly include the CSRF token in the request headers. This is done using the `hx-headers` attribute:

```html
<button hx-post="/some-url/" hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'>
    Submit
</button>
```

This ensures that Django's CSRF protection is satisfied.
