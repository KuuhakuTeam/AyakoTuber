# Ayako Youtube Downloader
# Copyright (C) 2022 KuuhakuTeam
#
# This file is a part of < https://github.com/KuuhakuTeam/AyakoRobot/ >
# PLease read the GNU v3.0 License Agreement in
# <https://www.github.com/KuuhakuTeam/AyakoRobot/blob/master/LICENSE/>.


import motor.motor_asyncio

from .bot import Ayako
from .plugins.ayako import ytdl_handler, ping_, start_
from .config import DATABASE_URL, TRIGGER

from hydrogram import filters
from hydrogram.handlers import MessageHandler

db_core = motor.motor_asyncio.AsyncIOMotorClient(DATABASE_URL)


Ayako.add_handler(MessageHandler(start_, filters.command("start", TRIGGER)))
Ayako.add_handler(MessageHandler(ping_, filters.command("ping", TRIGGER)))
Ayako.add_handler(MessageHandler(ytdl_handler, filters.command(["ytdl", "ydl"], TRIGGER)))
