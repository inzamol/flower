import os
import time
from datetime import datetime, timedelta
from celery import Celery
from celery.schedules import crontab

# Configure Celery App
app = Celery(
    "beat_demo",
    broker=os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/0"),
)

app.conf.update(
    timezone="UTC",
    worker_send_task_events=True,
    task_send_sent_event=True,
    result_extended=True,
)

# Define Recurring Tasks Schedule
app.conf.beat_schedule = {
    "add-every-15-seconds": {
        "task": "beat_demo.add",
        "schedule": 15.0,
        "args": (10, 20),
        "options": {"queue": "celery"},
    },
    "report-every-minute": {
        "task": "beat_demo.generate_report",
        "schedule": timedelta(minutes=1),
        "kwargs": {"report_type": "summary", "notify": True},
    },
    "healthcheck-every-30-seconds": {
        "task": "beat_demo.healthcheck",
        "schedule": 30.0,
    },
    "cron-hourly-maintenance": {
        "task": "beat_demo.maintenance_job",
        "schedule": crontab(minute=0, hour="*"),
        "kwargs": {"mode": "deep_clean"},
    },
}


@app.task(name="beat_demo.add")
def add(x, y):
    return x + y


@app.task(name="beat_demo.healthcheck")
def healthcheck():
    return {"status": "ok", "timestamp": str(datetime.now())}


@app.task(name="beat_demo.generate_report")
def generate_report(report_type="summary", notify=False):
    time.sleep(1)
    return {"report": f"{report_type} report generated successfully", "notify": notify}


@app.task(name="beat_demo.maintenance_job")
def maintenance_job(mode="standard"):
    return f"Maintenance performed in {mode} mode."


if __name__ == "__main__":
    app.start()
