import logging

from apscheduler.schedulers.background import BackgroundScheduler

from app.services.raffles import run_expiration_job
from app.services.recordatorio import send_payment_reminders

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def start_scheduler() -> None:
    scheduler.add_job(run_expiration_job, "interval", minutes=15, id="expire_reservations", replace_existing=True)
    scheduler.add_job(send_payment_reminders, "interval", hours=24, id="payment_reminders", replace_existing=True)
    scheduler.start()
    logger.info("Scheduler iniciado: expiracion cada 15 min, recordatorios cada 24 h")


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler de expiracion de reservas detenido")
