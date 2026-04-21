from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from app.db.session import SessionLocal
from app.services.aggregate_service import aggregate_monthly


scheduler = BackgroundScheduler(timezone="Asia/Jakarta")


def run_monthly_aggregation():
    db = SessionLocal()
    try:
        now = datetime.now()

        # ambil bulan sebelumnya
        year = now.year
        month = now.month - 1

        if month == 0:
            month = 12
            year -= 1

        print(f"Running aggregation for {month}-{year}")

        aggregate_monthly(db, year, month)

    finally:
        db.close()


def start_scheduler():
    # jalan tiap tanggal 1 jam 00:00
    scheduler.add_job(
        run_monthly_aggregation,
        trigger="cron",
        day=1,
        hour=0,
        minute=0
    )

    scheduler.start()