# Ayako Youtube Downloader
# Copyright (C) 2022 KuuhakuTeam
#
# This file is a part of < https://github.com/KuuhakuTeam/AyakoRobot/ >
# PLease read the GNU v3.0 License Agreement in
# <https://www.github.com/KuuhakuTeam/AyakoRobot/blob/master/LICENSE/>.

import re
import os
import shutil
import logging
import requests
import tempfile

from uuid import uuid4
from wget import download
from datetime import datetime
from youtubesearchpython.__future__ import VideosSearch

from hydrogram import filters
from hydrogram.errors import MessageNotModified
from hydrogram.types import (
    Message,
    CallbackQuery,
    InputMediaVideo,
    InputMediaAudio,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    InlineQuery,
    InlineQueryResultArticle,
    InlineQueryResultPhoto,
    InputTextMessageContent,
)

from my_ytdl import Downloader, Mytdl

from .. import Ayako


_YT = re.compile(
    r"(?m)http(?:s?):\/\/(?:www\.)?(?:music\.)?youtu(?:be\.com\/(watch\?v=|shorts/|embed/)|\.be\/|)(?P<id>([\w\-\_]{11}))(&(amp;)?‌​[\w\?‌​=]*)?"
)


logger = logging.getLogger(__name__)

YT_DATA = {}


async def ytdl_handler(_, message: Message):
    query = input_str(message)
    if not query:
        return await message.reply("<i>Insert a link or query to search.</i>")
    match = _YT.match(query)
    if match is None:
        search_key = rand_key()
        YT_DATA[search_key] = query
        search = await VideosSearch(query).next()
        if search["result"] == []:
            return await message.reply(f"No result found for `{query}`")
        i = search["result"][0]
        out = f"<b><a href={i['link']}>{i['title']}</a></b>"
        out += f"\nPublished {i['publishedTime']}\n"
        out += f"\n<b>❯ Duration:</b> {i['duration']}"
        out += f"\n<b>❯ Views:</b> {i['viewCount']['short']}"
        out += f"\n<b>❯ Uploader:</b> <a href={i['channel']['link']}>{i['channel']['name']}</a>\n\n"
        btn = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        f"1/{len(search['result'])}",
                        callback_data=f"ytdl_scroll|{search_key}|1|{message.from_user.id}",
                    )
                ],
                [
                    InlineKeyboardButton(
                        "Download",
                        callback_data=f"yt_gen|{i['id']}|{None}|{message.from_user.id}",
                    )
                ],
            ]
        )
        img = await get_ytthumb(i["id"])
        caption = out
        markup = btn
        await message.reply_photo(photo=img, caption=caption, reply_markup=markup)
    else:
        key = match.group("id")
        deatils = Mytdl.get_download_button(key, message.from_user.id)
        img = await get_ytthumb(key)
        caption = deatils.caption
        markup = deatils.buttons
        await message.reply_photo(photo=img, caption=caption, reply_markup=markup)


@Ayako.on_inline_query()
async def iytdl_handler(_, iq: InlineQuery):
    results = []
    user_id = iq.from_user.id
    query = iq.query
    match = _YT.match(query)
    found_ = True
    if match is None:
        search_key = rand_key()
        YT_DATA[search_key] = query
        search = await VideosSearch(query).next()
        if search["result"] == []:
            found_ = False
        i = search["result"][0]
        out = f"<b><a href={i['link']}>{i['title']}</a></b>"
        out += f"\nPublished {i['publishedTime']}\n"
        out += f"\n<b>❯ Duration:</b> {i['duration']}"
        out += f"\n<b>❯ Views:</b> {i['viewCount']['short']}"
        out += f"\n<b>❯ Uploader:</b> <a href={i['channel']['link']}>{i['channel']['name']}</a>\n\n"
        btn = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        f"1/{len(search['result'])}",
                        callback_data=f"ytdl_scroll|{search_key}|1|{user_id}",
                    )
                ],
                [
                    InlineKeyboardButton(
                        "Download",
                        callback_data=f"yt_gen|{i['id']}|{None}|{user_id}",
                    )
                ],
            ]
        )
        img = await get_ytthumb(i["id"])
        if found_:
            results.append(
                InlineQueryResultPhoto(
                    photo_url=img,
                    thumb_url=img,
                    caption=out,
                    reply_markup=btn,
                )
            )
        else:
            results.append(
                InlineQueryResultArticle(
                    title="not found",
                    input_message_content=InputTextMessageContent(
                        f"No result found for `{query}`"
                    ),
                    description="INVALID",
                )
            )
    else:
        key = match.group("id")
        deatils = Mytdl.get_download_button(key, user_id)
        img = await get_ytthumb(key)
        results = [
                InlineQueryResultPhoto(
                    photo_url=img,
                    thumb_url=img,
                    caption=deatils.caption,
                    reply_markup=deatils.buttons,
                )
            ]
    await iq.answer(results=results, is_gallery=False, is_personal=True)
    iq.stop_propagation()


@Ayako.on_callback_query(filters=filters.regex(pattern=r"ytdl_scroll\|(.*)"))
async def ytdl_scroll_callback(_, cq: CallbackQuery):
    callback = cq.data.split("|")
    search_key = callback[1]
    page = int(callback[2])
    user_id = int(callback[3])
    if not cq.from_user.id == user_id:
        return await cq.answer("not for you", show_alert=True)
    try:
        query = YT_DATA[search_key]
        search = await VideosSearch(query).next()
        i = search["result"][page]
        out = f"<b><a href={i['link']}>{i['title']}</a></b>"
        out += f"\nPublished {i['publishedTime']}\n"
        out += f"\n<b>❯ Duration:</b> {i['duration']}"
        out += f"\n<b>❯ Views:</b> {i['viewCount']['short']}"
        out += f"\n<b>❯ Uploader:</b> <a href={i['channel']['link']}>{i['channel']['name']}</a>\n\n"
        scroll_btn = [
            [
                InlineKeyboardButton(
                    "Back", callback_data=f"ytdl_scroll|{search_key}|{page-1}|{user_id}"
                ),
                InlineKeyboardButton(
                    f"{page+1}/{len(search['result'])}",
                    callback_data=f"ytdl_scroll|{search_key}|{page+1}|{user_id}",
                ),
            ]
        ]
        if page == 0:
            if len(search["result"]) == 1:
                return await cq.answer("That's the end of list", show_alert=True)
            scroll_btn = [[scroll_btn.pop().pop()]]
        elif page == (len(search["result"]) - 1):
            scroll_btn = [[scroll_btn.pop().pop(0)]]
        btn = [
            [
                InlineKeyboardButton(
                    "Download", callback_data=f"yt_gen|{i['id']}|{None}|{user_id}"
                )
            ]
        ]
        btn = InlineKeyboardMarkup(scroll_btn + btn)
        await cq.edit_message_media(
            InputMediaPhoto(await get_ytthumb(i["id"]), caption=out), reply_markup=btn
        )
    except (KeyError, MessageNotModified):
        return await cq.answer(
            "error when obtaining information, perform a new search", show_alert=True
        )


@Ayako.on_callback_query(filters=filters.regex(pattern=r"yt_(gen|dl)\|(.*)"))
async def download_handler(_, cq: CallbackQuery):
    callback = cq.data.split("|")
    key = callback[1]
    user_id = int(callback[3])
    if not cq.from_user.id == user_id:
        return await cq.answer("not for you", show_alert=True)
    try:
        if callback[0] == "yt_gen":
            x = Mytdl.get_download_button(key, user_id)
            await cq.edit_message_caption(caption=x.caption, reply_markup=x.buttons)
        else:
            uid = callback[2]
            type_ = callback[4]
            with tempfile.TemporaryDirectory() as tempdir:
                path_ = os.path.join(tempdir, "ytdl")
            thumb = download(await get_ytthumb(key), "ayako/downloads/")
            if type_ == "a":
                format_ = "audio"
            else:
                format_ = "video"

            await cq.edit_message_caption(caption="<b>Downloading wait...</b>")

            if format_ == "video":
                options = {
                    "addmetadata": True,
                    "geo_bypass": True,
                    "nocheckcertificate": True,
                    "outtmpl": os.path.join(path_, "%(title)s-%(format)s.%(ext)s"),
                    "logger": logger,
                    "format": uid,
                    "writethumbnail": True,
                    "prefer_ffmpeg": True,
                    "postprocessors": [{"key": "FFmpegMetadata"}],
                    "quiet": True,
                    "logtostderr": True,
                }
                file, duration, title = Downloader.ytdownloader(
                    url=f"https://www.youtube.com/watch?v={key}", options=options
                )
                await cq.edit_message_caption(
                    caption="<b>Uploading video may take a few moments.</b>"
                )
                await cq.edit_message_media(
                    media=InputMediaVideo(
                        media=file, duration=duration, caption=title, thumb=thumb
                    )
                )

            elif format_ == "audio":
                options = {
                    "outtmpl": os.path.join(path_, "%(title)s-%(format)s.%(ext)s"),
                    "logger": logger,
                    "writethumbnail": True,
                    "prefer_ffmpeg": True,
                    "format": "bestaudio/best",
                    "geo_bypass": True,
                    "nocheckcertificate": True,
                    "postprocessors": [
                        {
                            "key": "FFmpegExtractAudio",
                            "preferredcodec": "mp3",
                            "preferredquality": uid,
                        },
                        {"key": "EmbedThumbnail"},
                        {"key": "FFmpegMetadata"},
                    ],
                    "quiet": True,
                    "logtostderr": True,
                }
                file, duration, title = Downloader.ytdownloader(
                    url=f"https://www.youtube.com/watch?v={key}", options=options
                )

                await cq.edit_message_caption(
                    caption="<b>Uploading audio may take a few moments.</b>"
                )
                await cq.edit_message_media(
                    media=InputMediaAudio(
                        media=file, duration=duration, caption=title, thumb=thumb
                    )
                )
            else:
                await cq.answer("format not suport", show_alert=True)
            os.remove(thumb)
            shutil.rmtree(tempdir)
    except MessageNotModified:
        return
    except Exception as e:
        logging.error(e)
        return


async def ping_(_, message):
    start = datetime.now()
    replied = await message.reply("pong!")
    end = datetime.now()
    m_s = (end - start).microseconds / 1000
    await replied.edit(f"ping: `{m_s}𝚖𝚜`")


async def start_(_, message: Message):
    msg = """
<b>Hello friend, I'm <a href="https://t.me/ayako_robot">Ayako</a>, the most advanced YouTube and audio/video downloader on Telegram!</b>

» <i>This bot is currently under development and may contain bugs</i>
» <i>Consider <a href="https://t.me/KuuhakuTeam">joining our channel</a> to stay up to date with updates</i>
    """
    await message.reply(msg)


### funcs
def input_str(message) -> str:
    """input string"""
    input_ = message.text
    if " " in input_ or "\n" in input_:
        return str(input_.split(maxsplit=1)[1].strip())
    return ""


async def get_ytthumb(videoid: str):
    thumb_quality = [
        "maxresdefault.jpg",  # Best quality
        "hqdefault.jpg",
        "sddefault.jpg",
        "mqdefault.jpg",
        "default.jpg",  # Worst quality
    ]
    thumb_link = "https://i.imgur.com/4LwPLai.png"
    for qualiy in thumb_quality:
        link = f"https://i.ytimg.com/vi/{videoid}/{qualiy}"
        if requests.get(link).status_code == 200:
            thumb_link = link
            break
    return thumb_link


def rand_key():
    return str(uuid4())[:8]
