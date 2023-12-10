# Ayako Youtube Downloader
# Copyright (C) 2022 KuuhakuTeam
#
# This file is a part of < https://github.com/KuuhakuTeam/AyakoRobot/ >
# PLease read the GNU v3.0 License Agreement in
# <https://www.github.com/KuuhakuTeam/AyakoRobot/blob/master/LICENSE/>.

import time
import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pymongo.errors import ConnectionFailure
from logging.handlers import RotatingFileHandler


from . import Ayako, db_core
from .config import GP_LOGS, VERSION

from hydrogram import idle


logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        RotatingFileHandler("ayako.log", maxBytes=10485760, backupCount=2),
        logging.StreamHandler(),
    ],
)


logging.getLogger('apscheduler.executors.default').propagate = False

logging.getLogger("hydrogram").setLevel(logging.WARNING)
logging.getLogger("hydrogram.parser.html").setLevel(logging.ERROR)
logging.getLogger("hydrogram.session.session").setLevel(logging.ERROR)


scheduler = AsyncIOScheduler(timezone="America/Sao_Paulo")
start_time = time.time()


async def db_connect():
    """Check Mongo Client"""
    try:
        logging.info("Conectando ao MongoDB")
        await db_core.server_info()
        logging.info("Database conectada")
    except (BaseException, ConnectionFailure) as e:
        logging.error("Falha ao conectar a database, saindo....")
        logging.error(str(e))
        quit(1)


async def run_better():
    """Start Bot"""
    try:
        await Ayako.start()
    except Exception as e:
        logging.error(e)
    await Ayako.send_message(
        chat_id=GP_LOGS, text=f"[ Ayako ] Bot iniciado com sucesso ...\nVersion: <code>{VERSION}</code>"
    )
    logging.info("[ Ayako Schedule ] Bot iniciado com sucesso ...\n")


async def main():
    await db_connect()
    await run_better()
    await idle()


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())