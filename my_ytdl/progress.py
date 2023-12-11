__all__ = ["progress"]

import asyncio
import logging
import time

from math import floor
from typing import Dict, Tuple

from hydrogram import Client, ContinuePropagation, StopPropagation, StopTransmission
from hydrogram.errors import FloodWait, MessageNotModified

from .process import Process

from ayako.helpers import humanbytes, time_formatter


_PROGRESS: Dict[str, Tuple[int, int]] = {}
LOG = logging.getLogger(__name__)


async def progress(
    current: int,
    total: int,
    client: Client,
    process: Process,
    filename: str,
    mode: str = "upload",
    edit_rate: int = 8,
):
    """hydrogram Upload / Download Progress Bar

    Parameters:
    ----------
        - current (`int`): The amount of bytes transmitted so far.
        - total (`int`): The total size of the file.
        - client (`Client`): hydrogram Client.
        - process (`Process`): iytdl.process.Process.
        - filename (`str`): Display name of the file.
        - mode (`str`, optional): `"upload"` or `"download"`. (Defaults to `"upload"`)
        - edit_rate (`int`, optional): Message edit rate. (Defaults to `8`)
    """
    if process.is_cancelled:
        LOG.warning("Upload process is Cancelled")
        # Stop Uploading
        await client.stop_transmission()

    if current == total:
        if process.id not in _PROGRESS:
            return
        del _PROGRESS[process.id]
        try:
            await process.edit(f"`Finalizing {mode} process ...`")
        except FloodWait as f_w:
            await asyncio.sleep(f_w.x + 2)
        return
    now = int(time.time())
    if process.id not in _PROGRESS:
        _PROGRESS[process.id] = (now, now)
    start, last_update_time = _PROGRESS[process.id]
    # ------------------------------------ #
    if (now - last_update_time) >= edit_rate:
        _PROGRESS[process.id] = (start, now)
        # Only edit message once every 8 seconds to avoid ratelimits
        after = now - start
        speed = current / after
        eta = round((total - current) / speed)
        percentage = round(current / total * 100)
        progress_bar = (
            f"[{'█' * floor(15 * percentage / 100)}"
            f"{'░' * floor(15 * (1 - percentage / 100))}]"
        )
        progress = f"""
<i>{mode.title()}ing:</i>  <code>{filename}</code>
<b>Completed:</b>  <code>{humanbytes(current)} / {humanbytes(total)}</code>
<b>Progress:</b>  <code>{progress_bar} {percentage} %</code>
<b>Speed:</b>  <code>{humanbytes(speed)}</code>
<b>ETA:</b>  <code>{time_formatter(eta)}</code>
"""
        try:
            await process.edit(progress, reply_markup=process.cancel_markup)
        except FloodWait as f:
            await asyncio.sleep(f.x + 2)
        except (ContinuePropagation, MessageNotModified):
            pass
        except (StopPropagation, StopTransmission) as p_e:
            raise p_e
        except Exception:
            LOG.exception("Unable to Edit message")
