
import logging
import yt_dlp as youtube_dl

from typing import Any, Dict
from yt_dlp.utils import DownloadError, GeoRestrictedError

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

