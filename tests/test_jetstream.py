import pytest
from src.jetstream import jetstream


def test_raw_handle():
    assert jetstream.raw_handle("@foo.com") == "foo.com"
    assert jetstream.raw_handle("bar.com") == "bar.com"


def test_get_public_jetstream_base_url():
    url = jetstream.get_public_jetstream_base_url("us-west", 2)
    assert url == "wss://jetstream2.us-west.bsky.network/subscribe"


def test_get_jetstream_query_url():
    url = jetstream.get_jetstream_query_url(
        "base", ["col1"], ["did1"], 123, True
    )
    assert "wantedCollections=col1" in url
    assert "wantedDids=did1" in url
    assert "cursor=123" in url
    assert "compress=true" in url


def test_get_cache_directory(tmp_path, monkeypatch):
    monkeypatch.setattr("platform.system", lambda: "Linux")
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))
    path = jetstream.get_cache_directory("jetstream")
    assert path.exists()
    assert path.name == "jetstream"


def test_resolve_handle_to_did_dns(monkeypatch):
    class FakeAnswer:
        def to_text(self):
            return '"did=did:plc:12345"'

    def fake_resolve(*args, **kwargs):
        return [FakeAnswer()]
    monkeypatch.setattr("dns.resolver.resolve", fake_resolve)
    did = jetstream.resolve_handle_to_did_dns("foo.com")
    assert did == "did:plc:12345"


def test_resolve_handle_to_did_well_known(monkeypatch):
    class FakeResponse:
        text = "did:plc:67890"
        def raise_for_status(self): pass
    monkeypatch.setattr("httpx.get", lambda *a, **k: FakeResponse())
    did = jetstream.resolve_handle_to_did_well_known("bar.com")
    assert did == "did:plc:67890"


def test_require_resolve_handle_to_did(monkeypatch):
    monkeypatch.setattr(jetstream, "resolve_handle_to_did", lambda h: None)
    with pytest.raises(ValueError):
        jetstream.require_resolve_handle_to_did("baz.com")
