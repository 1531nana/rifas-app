import logging

from apscheduler.schedulers.background import BackgroundScheduler

from app.services.raffles import run_expiration_job

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def start_scheduler() -> None:
    scheduler.add_job(run_expiration_job, "interval", minutes=15, id="expire_reservations", replace_existing=True)
    scheduler.start()
    logger.info("Scheduler de expiracion de reservas iniciado (cada 15 minutos)")


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler de expiracion de reservas detenido")
