import yt_dlp as youtube_dl

from yt_dlp.utils import DownloadError, ExtractorError, UnsupportedError

from collections import defaultdict
from typing import Dict, List

from hydrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from iytdl.types import SearchResult

from ..helpers.utils import humanbytes, sublists


YT = "https://www.youtube.com/"
YT_VID_URL = YT + "watch?v="


class Mytdl:
    def get_download_button(yt_id: str, user_id: int) -> SearchResult:
        """Generate Inline Buttons for YouTube Video

        Parameters:
        ----------
            - yt_id (`str`): YouTube video key.

        Returns:
        -------
            `SearchResult`: `~iytdl.types.SearchResult`
        """
        buttons = [
            [
                InlineKeyboardButton(
                    "⭐️ BEST - 📹 MP4",
                    callback_data=f"yt_dl|{yt_id}|mp4|{user_id}|v",
                ),
            ]
        ]
        best_audio_btn = [
            [
                InlineKeyboardButton(
                    "⭐️ BEST - 🎵 320Kbps - MP3",
                    callback_data=f"yt_dl|{yt_id}|mp3|{user_id}|a",
                )
            ]
        ]
        params = {"no-playlist": True, "quiet": True, "logtostderr": False}
        try:
            vid_data = youtube_dl.YoutubeDL(params).extract_info(
                f"{YT_VID_URL}{yt_id}", download=False
            )
        except ExtractorError:
            vid_data = None
            buttons += best_audio_btn
        else:
            # ------------------------------------------------ #
            qual_dict = defaultdict(lambda: defaultdict(int))
            qual_list = ("1440p", "1080p", "720p", "480p", "360p", "240p", "144p")
            audio_dict: Dict[int, str] = {}
            # ------------------------------------------------ #
            for video in vid_data["formats"]:
                fr_note = video.get("format_note")
                fr_id = video.get("format_id")
                fr_size = video.get("filesize")
                if video.get("ext") == "mp4":
                    for frmt_ in qual_list:
                        if fr_note in (frmt_, frmt_ + "60"):
                            qual_dict[frmt_][fr_id] = fr_size
                if video.get("acodec") != "none":
                    bitrrate = video.get("abr")
                    if bitrrate == (0 or "None"):
                        pass
                    else:
                        audio_dict[
                            bitrrate
                        ] = f"🎵 {bitrrate}Kbps ({humanbytes(fr_size) or 'N/A'})"
            audio_dict = delete_none(audio_dict)
            video_btns: List[InlineKeyboardButton] = []
            for frmt in qual_list:
                frmt_dict = qual_dict[frmt]
                if len(frmt_dict) != 0:
                    frmt_id = sorted(list(frmt_dict))[-1]
                    frmt_size = humanbytes(frmt_dict.get(frmt_id)) or "N/A"
                    video_btns.append(
                        InlineKeyboardButton(
                            f"📹 {frmt} ({frmt_size})",
                            callback_data=f"yt_dl|{yt_id}|{frmt_id}|{user_id}|v",
                        )
                    )
            buttons += sublists(video_btns, width=2)
            buttons += best_audio_btn
            buttons += sublists(
                list(
                    map(
                        lambda x: InlineKeyboardButton(
                            audio_dict[x], callback_data=f"yt_dl|{yt_id}|{x}|{user_id}|a"
                        ),
                        sorted(audio_dict.keys(), reverse=True),
                    )
                ),
                width=2,
            )

        return SearchResult(
            yt_id,
            (
                f"<a href={YT_VID_URL}{yt_id}>{vid_data.get('title')}</a>"
                if vid_data
                else ""
            ),
            vid_data.get("thumbnail")
            if vid_data
            else "https://s.clipartkey.com/mpngs/s/108-1089451_non-copyright-youtube-logo-copyright-free-youtube-logo.png",
            InlineKeyboardMarkup(buttons),
        )


def delete_none(_dict):
    """Delete None values recursively from all of the dictionaries, tuples, lists, sets"""
    if isinstance(_dict, dict):
        for key, value in list(_dict.items()):
            if isinstance(value, (list, dict, tuple, set)):
                _dict[key] = delete_none(value)
            elif value is None or key is None:
                del _dict[key]

    elif isinstance(_dict, (list, set, tuple)):
        _dict = type(_dict)(delete_none(item) for item in _dict if item is not None)

    return _dict
