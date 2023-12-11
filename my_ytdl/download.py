
import asyncio
import logging
import yt_dlp as youtube_dl

from typing import Any, Dict
from yt_dlp.utils import DownloadError, GeoRestrictedError

from hydrogram.types import InputMediaDocument, InputMediaVideo
from hydrogram.enums import ParseMode

from ayako import Ayako

from . import progress as upload_progress
from .process import Process

logger = logging.getLogger(__name__)


class Downloader:
    def ytdownloader(url: str, options: Dict[str, Any]):
        try:
            with youtube_dl.YoutubeDL(options) as ytdl:
                down =  ytdl.extract_info(url, download=True)
                file = down.get("requested_downloads")[0]["filepath"] 
                duration = down.get("duration")
                title = down.get("fulltitle")
                return file, duration, title
        except DownloadError:
            logger.error("[DownloadError] : Failed to Download Video")
        except GeoRestrictedError:
            logger.error(
                "[GeoRestrictedError] : The uploader has not made this video"
                " available in your country"
            )
        except Exception:
            logger.exception("Something Went Wrong")


    async def __upload_video(
        self,
        client: Ayako,
        process: Process,
        caption: str,
        mkwargs: Dict[str, Any],
        with_progress: bool = True,
    ):
        if not (
            uploaded := await client.send_video(
                chat_id=self.log_group_id,
                caption=f"📹  {caption}",
                parse_mode=ParseMode.HTML,
                disable_notification=True,
                progress=upload_progress if with_progress else None,
                progress_args=(client, process, mkwargs["file_name"])
                if with_progress
                else (),
                **mkwargs,
            )
        ):
            return
        await asyncio.sleep(2)
        if not process.is_cancelled:
            if uploaded.video:
                return await process.edit_media(
                    media=InputMediaVideo(
                        uploaded.video.file_id, caption=uploaded.caption.html
                    ),
                    reply_markup=None,
                )
            elif uploaded.document:
                return await process.edit_media(
                    media=InputMediaDocument(
                        uploaded.document.file_id, caption=uploaded.caption.html
                    ),
                    reply_markup=None,
                )
