from urllib.parse import urlencode
import typing as t

PUBLIC_URL_FMT = "wss://jetstream{instance}.{geo}.bsky.network/subscribe"


def get_public_jetstream_base_url(
    geo: t.Literal["us-west", "us-east"] = "us-west",
    instance: int = 1,
) -> str:
    """Return a public Jetstream URL with the given options."""
    return PUBLIC_URL_FMT.format(geo=geo, instance=instance)


def get_jetstream_query_url(
    base_url: str,
    collections: t.Sequence[str],
    dids: t.Sequence[str],
    cursor: int,
    compress: bool,
) -> str:
    """Return a Jetstream URL with the given query parameters."""
    query = [("wantedCollections", collection) for collection in collections]
    query += [("wantedDids", did) for did in dids]
    if cursor:
        query.append(("cursor", str(cursor)))
    if compress:
        query.append(("compress", "true"))
    query_enc = urlencode(query)
    return f"{base_url}?{query_enc}" if query_enc else base_url
