# CRM Celery + Celery Beat Setup

## 📘 Overview
This guide explains how to set up and run Celery and Celery Beat to generate weekly CRM reports that summarize:
- Total number of customers
- Total number of orders
- Total revenue

Reports are logged to `/tmp/crm_report_log.txt`.

---

## ⚙️ 1. Installation

### Install Redis
Ensure Redis is installed and running:
```bash
sudo apt update
sudo apt install redis-server -y
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

### Install Python Dependencies
Add to your `requirements.txt`:
```
Django
graphene-django
gql
requests
django-crontab
celery
django-celery-beat
redis
```

Then install:
```bash
pip install -r requirements.txt
```

---

## 🧱 2. Database Migrations
Apply migrations to create Celery Beat tables:
```bash
python manage.py migrate
```

---

## 🚀 3. Running Celery

### Start the Celery Worker
```bash
celery -A crm worker -l info
```

### Start Celery Beat
```bash
celery -A crm beat -l info
```

---

## 📅 4. Scheduling
Celery Beat runs the `generate_crm_report` task weekly according to the following schedule:

```python
CELERY_BEAT_SCHEDULE = {
    'generate-crm-report': {
        'task': 'crm.tasks.generate_crm_report',
        'schedule': crontab(day_of_week='mon', hour=6, minute=0),
    },
}
```

You can manually trigger it:
```bash
python manage.py shell
>>> from crm.tasks import generate_crm_report
>>> generate_crm_report.delay()
```

---

## 📄 5. Verify Logs
Check `/tmp/crm_report_log.txt`:
```
2025-10-27 06:00:00 - Report: 45 customers, 120 orders, 540000 total revenue
```

If you see this type of entry, your task and scheduler are running correctly. ✅
