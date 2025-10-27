# CRM Celery Beat Setup

This document describes how to configure and run Celery and Celery Beat for the CRM application.

---

## 1. Install Redis and Dependencies

1. Make sure Redis is installed and running on your local machine.
   ```bash
   sudo apt update
   sudo apt install redis-server
   sudo systemctl enable redis-server
   sudo systemctl start redis-server
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## 2. Run Migrations

Before starting Celery, ensure your database is ready:
```bash
python manage.py migrate
```

---

## 3. Start Celery Worker

Run the Celery worker to process background tasks:
```bash
celery -A crm worker -l info
```

This command starts the Celery worker that executes scheduled and asynchronous tasks defined in the project.

---

## 4. Start Celery Beat

Run Celery Beat to schedule recurring tasks:
```bash
celery -A crm beat -l info
```

Celery Beat will automatically trigger the **generate_crm_report** task every Monday at 6:00 AM, as configured in `crm/settings.py`.

---

## 5. Verify Logs

After a few minutes of running both services, check the log file:
```bash
cat /tmp/crm_report_log.txt
```

You should see entries like:
```
2025-10-27 06:00:00 - Report: 15 customers, 30 orders, 12000 revenue
```

This confirms that the Celery Beat job ran successfully and that the CRM application is generating reports correctly.

---

## 6. Troubleshooting

- Ensure Redis is running on `localhost:6379`.
- Verify `django_celery_beat` is added to `INSTALLED_APPS` in `crm/settings.py`.
- Check that `CELERY_BROKER_URL` and `CELERY_BEAT_SCHEDULE` are properly configured.

---

✅ **Summary**
- Install Redis  
- Run migrations  
- Start Celery worker  
- Start Celery Beat  
- Verify logs in `/tmp/crm_report_log.txt`

All required steps are now covered.
