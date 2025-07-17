#!/usr/bin/env -S uv run -q
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "click",
#     "dnspython",
#     "httpx",
#     "httpx-ws",
#     "zstandard",
# ]
# ///
import typing as t
from pathlib import Path
from urllib.parse import urlencode

import click
import zstandard as zstd
from httpx_ws import connect_ws

from .handle_resolver import require_resolve_handle_to_did
from .url_utils import get_jetstream_query_url, get_public_jetstream_base_url
from .zstd_utils import get_zstd_decompressor


PUBLIC_URL_FMT = "wss://jetstream{instance}.{geo}.bsky.network/subscribe"


def get_public_jetstream_base_url(
    geo: t.Literal["us-west", "us-east"] = "us-west",
    instance: int = 1,
) -> str:
    """Return a public Jetstream URL with the given options."""
    return PUBLIC_URL_FMT.format(geo=geo, instance=instance)


@click.option(
    "--handle",
    "-h",
    "handles",
    multiple=True,
    help="The ATProto handles to subscribe to. If not provided, subscribe to all.",
    type=str,
)
@click.option(
    "--cursor",
    "-u",
    help="The cursor to start from. If not provided, start from 'now'.",
    type=int,
    default=0,
)
@click.option(
    "--url",
    "base_url",
    help="The Jetstream URL to connect to.",
    type=str,
    default=None,
)
@click.option(
    "--geo",
    "-g",
    help="The public Jetstream service geography to connect to.",
    type=click.Choice(["us-west", "us-east"]),
    default="us-west",
)
@click.option(
    "--instance",
    "-i",
    help="The public Jetstream instance number to connect to.",
    type=int,
    default=1,
)
@click.option(
    "--compress",
    is_flag=True,
    help="Enable Zstandard compression.",
    default=False,
)
def jetstream(
    collections: t.Sequence[str],
    dids: t.Sequence[str],
    handles: t.Sequence[str],
    cursor: int,
    base_url: str | None,
    geo: t.Literal["us-west", "us-east"],
    instance: int,
    compress: bool,
):
    """Emit Jetstream JSON messages to the console, one per line."""
    # Resolve handles and form the final list of DIDs to subscribe to.
    handle_dids = [require_resolve_handle_to_did(handle) for handle in handles]
    dids = list(dids) + handle_dids

    decompressor = get_zstd_decompressor() if compress else None
    base_url = base_url or get_public_jetstream_base_url(geo, instance)
    url = get_jetstream_query_url(
        base_url, collections, dids, cursor, compress)

    with connect_ws(url) as ws:
        while True:
            if decompressor:
                message = ws.receive_bytes()
                with decompressor.stream_reader(message) as reader:
                    message = reader.read()
                message = message.decode("utf-8")
            else:
                message = ws.receive_text()
            print(message)


if __name__ == "__main__":
    jetstream()
