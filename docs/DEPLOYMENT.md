# Deployment Preparation

This document describes the generic production path prepared in Phase 19.
Phase 20 must still select a free hosting provider, configure its final domain,
and perform the actual deployment.

## Runtime assumptions

- Python 3.14 is the verified project runtime.
- The production host must support Python and a Linux-compatible WSGI process.
- Django remains pinned to 5.2.17.
- Gunicorn serves the Django WSGI application.
- WhiteNoise serves collected static assets only.
- SQLite remains the V1 database unless the selected Phase 20 provider requires
  a documented change.

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
  final HTTPS domain and subdomain policy have been verified in Phase 20.

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

The Phase 20 provider may require a bind option based on its assigned port, but
no provider-specific start file is included in Phase 19.

## Static and uploaded media

WhiteNoise serves files collected into `staticfiles/`. That generated directory
is ignored by Git and must not be committed.

WhiteNoise must not serve `MEDIA_ROOT`. Book PDFs and payment receipts are
protected application data:

- books are streamed only through the subscription-protected PDF endpoint;
- direct `/media/books/pdfs/` requests remain blocked;
- receipts are streamed only through the staff-protected receipt endpoint.

Free or ephemeral hosting may erase the SQLite database and uploaded media on
restart or redeploy. Phase 20 must choose a provider and determine whether it
offers persistent storage for both `DATABASE_PATH` and `MEDIA_ROOT`. Until that
is known, uploads and SQLite data must be treated as non-persistent on such a
host. No external object storage is introduced in Phase 19.

## Phase 20 decisions still required

- Select the free hosting provider.
- Configure its final hostname in `ALLOWED_HOSTS`.
- Configure HTTPS origins in `CSRF_TRUSTED_ORIGINS` when required.
- Confirm the provider sends `X-Forwarded-Proto` correctly and strips any
  untrusted client-supplied value before forwarding requests.
- Decide whether persistent SQLite and media storage are available.
- Enable and tune HSTS only after the final HTTPS hostname is verified.
- Run the deployed V1 acceptance journey before declaring Phase 20 complete.
