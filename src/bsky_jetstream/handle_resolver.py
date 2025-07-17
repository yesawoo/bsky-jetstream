def raw_handle(handle: str) -> str:
    return handle[1:] if handle.startswith("@") else handle


def resolve_handle_to_did_dns(handle: str) -> str | None:
    import dns.resolver
    try:
        answers = dns.resolver.resolve(f"_atproto.{handle}", "TXT")
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
        return None
    for answer in answers:
        txt = answer.to_text()
        if txt.startswith('"did='):
            return txt[5:-1]
    return None


def resolve_handle_to_did_well_known(handle: str) -> str | None:
    import httpx
    try:
        response = httpx.get(
            f"https://{handle}/.well-known/atproto-did", timeout=5)
        response.raise_for_status()
    except (httpx.ConnectError, httpx.HTTPStatusError, httpx.TimeoutException):
        return None
    return response.text.strip()


def resolve_handle_to_did(handle: str) -> str | None:
    handle = raw_handle(handle)
    maybe_did = resolve_handle_to_did_dns(handle)
    maybe_did = maybe_did or resolve_handle_to_did_well_known(handle)
    return maybe_did


def require_resolve_handle_to_did(handle: str) -> str:
    did = resolve_handle_to_did(handle)
    if did is None:
        raise ValueError(f"Could not resolve handle '{handle}' to a DID.")
    return did
