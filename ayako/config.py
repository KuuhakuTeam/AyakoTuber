# Ayako Youtube Downloader
# Copyright (C) 2022 KuuhakuTeam
#
# This file is a part of < https://github.com/KuuhakuTeam/AyakoRobot/ >
# PLease read the GNU v3.0 License Agreement in
# <https://www.github.com/KuuhakuTeam/AyakoRobot/blob/master/LICENSE/>.

import os
from dotenv import load_dotenv

if os.path.isfile("config.env"):
    load_dotenv("config.env")

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
GP_LOGS = int(os.environ.get("GP_LOGS"))
DATABASE_URL = os.environ.get("DATABASE_URL")
TRIGGER = os.environ.get("TRIGGER", "/ ! . :".split())
VERSION = "v1.0.1"
DEV = [838926101]
