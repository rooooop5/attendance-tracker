from apscheduler.schedulers.background import BackgroundScheduler
from datetime import date

from database import SessionLocal
from services.attendance import backfill_attendance, generate_default_attendance_for_date


def backfill_attendance_task():
    session = SessionLocal()
    try:
        backfill_attendance(session)
    except:
        print("sem start date not found")
    finally:
        session.close()


def generate_default_attendance_today_task():
    session = SessionLocal()
    try:
        generate_default_attendance_for_date(date.today(), session)
    finally:
        session.close()


bg_scheduler = BackgroundScheduler()


def setup_bg_scheduler():
    bg_scheduler.add_job(backfill_attendance_task, "cron", day_of_week="mon", hour=5, minute=0)
    bg_scheduler.add_job(generate_default_attendance_today_task, "cron", hour=6, minute=0)
    bg_scheduler.start()
