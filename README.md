# Tilespot

Tilespot is a production-oriented Nigerian tile marketplace built with Django 5.2.17.

## Core features
- Buyer/seller accounts and business profiles
- Tile catalogue with search, filters, sorting and saved searches
- Tile brands, categories, sizes, finishes, colours, materials and stock
- Multiple photos and video uploads
- Real remote seed photography plus local uploads
- Likes, favourites, comments, buyer questions and enquiries
- Notifications and messaging foundation
- Seller dashboard
- Admin at `/admin/`
- Ads placement model and homepage-ready advertising area
- Nigerian states + FCT
- SEO title/meta, canonical URLs, sitemap.xml, robots.txt, structured-friendly URLs
- PostgreSQL via `DATABASE_URL` in production; SQLite locally
- WhiteNoise static files and Gunicorn

## Local setup
```powershell
python -m venv venv
.\\venv\\Scripts\\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py seed_tilespot
python manage.py createsuperuser
python manage.py runserver
```
Demo seller accounts are seeded with password `Tilespot123!`; change them immediately if used outside local testing.

## Production
Set `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=False`, `DJANGO_ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, and `DATABASE_URL`. Run `python manage.py collectstatic --noinput` and serve with Gunicorn.

Google visibility is supported with crawlable listing pages, metadata, sitemap and robots rules, but no website can guarantee a Google ranking or first-page placement.
