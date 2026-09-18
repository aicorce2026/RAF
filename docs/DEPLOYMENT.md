# Deployment

Phase 19 prepared the production configuration. Phase 20 deployed and accepted
the V1 free demonstration.

## Live demo

https://wahibalkabodi.pythonanywhere.com

This is a free/demo deployment on PythonAnywhere Free.

- PythonAnywhere username: `wahibalkabodi`
- Project path: `/home/wahibalkabodi/RAF`
- Virtual environment: `/home/wahibalkabodi/.virtualenvs/rafenv`
- Python: 3.13.1
- Django: 5.2.17
- Database: SQLite
- WSGI configuration: working
- `DEBUG=False`
- `ALLOWED_HOSTS=wahibalkabodi.pythonanywhere.com`
- `CSRF_TRUSTED_ORIGINS=https://wahibalkabodi.pythonanywhere.com`
- The real `SECRET_KEY` is loaded outside the repository.
- No real secret was committed.
- HSTS remains disabled for this demo with `SECURE_HSTS_SECONDS=0`.

## Runtime assumptions

- Python 3.14 is the verified local development runtime; the deployed
  PythonAnywhere runtime is Python 3.13.1.
- The production host must support Python and a Linux-compatible WSGI process.
- Django remains pinned to 5.2.17.
- The PythonAnywhere WSGI configuration serves the deployed application;
  Gunicorn remains available for compatible generic Linux deployments.
- WhiteNoise serves collected static assets only.
- SQLite is the V1 demo database.

## Installation

```bash
python -m pip install -r requirements.txt
```

## Required environment variables

- `SECRET_KEY`: required whenever `DEBUG=False`; use a long random value.
- `DEBUG`: set to `False` in production.
- `ALLOWED_HOSTS`: comma-separated hostnames without schemes.

Example structure only:

```text
DEBUG=False
ALLOWED_HOSTS=example.com,www.example.com
```

## Optional deployment environment variables

- `CSRF_TRUSTED_ORIGINS`: comma-separated HTTPS origins, including schemes,
  when the final host requires them.
- `DATABASE_PATH`: SQLite file path. Point this at persistent storage when the
  provider supplies one; otherwise it defaults to `db.sqlite3` in the project.
- `SECURE_SSL_REDIRECT`: defaults to enabled when `DEBUG=False`; it may be
  explicitly controlled for a provider-specific setup.
- `SECURE_HSTS_SECONDS`: defaults to `0`. Set a positive value only after the
  HTTPS domain and subdomain policy have been verified for a long-term
  production deployment. It remains `0` for the current demo.

`SECURE_PROXY_SSL_HEADER` is configured for hosts that send
`X-Forwarded-Proto: https`. Secure session and CSRF cookies are enabled whenever
`DEBUG=False`.

## Build and release commands

Apply migrations:

```bash
python manage.py migrate
```

Collect static files:

```bash
python manage.py collectstatic --noinput
```

Create the first administrator when needed:

```bash
python manage.py createsuperuser
```

Start the production WSGI server:

```bash
gunicorn config.wsgi:application
```

Other hosting providers may require a bind option based on their assigned port.
PythonAnywhere uses its configured WSGI file for the current demo.

## Static and uploaded media

WhiteNoise serves files collected into `staticfiles/`. That generated directory
is ignored by Git and must not be committed.

WhiteNoise must not serve `MEDIA_ROOT`. Book PDFs and payment receipts are
protected application data:

- books are streamed only through the subscription-protected PDF endpoint;
- direct `/media/books/pdfs/` requests remain blocked;
- receipts are streamed only through the staff-protected receipt endpoint.

Free hosting has resource and storage limitations. The current PythonAnywhere
demo uses SQLite and locally uploaded media. This is acceptable for the demo,
but a long-term production architecture should use appropriately managed
persistent database and uploaded-media storage. No external object storage was
introduced for V1.

## Phase 20 deployment result

- Static collection succeeded: 128 files copied and 384 post-processed.
- The observed collected-static size was approximately 5.1 MiB.
- No `/media/` static mapping was added intentionally. Protected uploads remain
  behind application-controlled endpoints.
- The deployed acceptance journey passed for HTTPS, static/RTL rendering, the
  developer footer, Django Admin and content creation, public catalog display,
  login and subscription gates, subscription approval, protected reading,
  reading progress, My Library, and Favorites.
- The raw `/media/books/pdfs/...` deployment URL bypass test was intentionally
  skipped by the user. Automated regression/security tests previously cover raw
  media blocking, but deployed raw-media-path behavior was not manually
  re-tested during Phase 20.

## Free demo limitations

PythonAnywhere Free has resource and storage limitations. SQLite and locally
uploaded media are acceptable for this demonstration, but they are not the
recommended long-term production architecture. A long-term production system
should use appropriately managed persistent database and uploaded-media storage.
