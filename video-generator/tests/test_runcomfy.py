import pytest
import requests

from videogen import runcomfy


class FakeResponse:
    def __init__(self, status_code=200, json_data=None, text=""):
        self.status_code = status_code
        self._json = json_data or {}
        self.text = text

    def json(self):
        return self._json


class FakeSession:
    """Scripted session: pops one canned response (or exception) per request."""

    def __init__(self, script):
        self.script = list(script)
        self.headers = {}
        self.calls = []

    def request(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs.get("json")))
        item = self.script.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


def make_client(script):
    session = FakeSession(script)
    client = runcomfy.RunComfyClient(token="tok", session=session)
    return client, session


def test_submit_returns_request_id():
    client, session = make_client([FakeResponse(json_data={"request_id": "req_1"})])
    data = client.submit("wan-ai/wan-2-6/text-to-video", {"prompt": "x"})
    assert data["request_id"] == "req_1"
    method, url, payload = session.calls[0]
    assert method == "POST"
    assert url.endswith("/v1/models/wan-ai/wan-2-6/text-to-video")
    assert payload == {"prompt": "x"}


def test_submit_retries_on_server_error(monkeypatch):
    monkeypatch.setattr("time.sleep", lambda _s: None)
    client, session = make_client([
        FakeResponse(status_code=503),
        requests.ConnectionError("boom"),
        FakeResponse(json_data={"request_id": "req_2"}),
    ])
    assert client.submit("a/b/c", {})["request_id"] == "req_2"
    assert len(session.calls) == 3


def test_submit_does_not_retry_client_error():
    client, session = make_client([FakeResponse(status_code=401, text="bad token")])
    with pytest.raises(runcomfy.RunComfyError, match="401"):
        client.submit("a/b/c", {})
    assert len(session.calls) == 1


def test_wait_polls_until_completed(monkeypatch):
    monkeypatch.setattr("time.sleep", lambda _s: None)
    client, session = make_client([
        FakeResponse(json_data={"status": "in_queue"}),
        FakeResponse(json_data={"status": "in_progress"}),
        FakeResponse(json_data={"status": "completed"}),
    ])
    assert client.wait("req_1")["status"] == "completed"
    assert len(session.calls) == 3


def test_wait_raises_on_failed_status():
    client, _ = make_client([FakeResponse(json_data={"status": "failed", "error": "nsfw"})])
    with pytest.raises(runcomfy.GenerationFailed, match="failed"):
        client.wait("req_1")


def test_missing_token_rejected():
    with pytest.raises(runcomfy.RunComfyError, match="RUNCOMFY_API_TOKEN"):
        runcomfy.RunComfyClient(token=None)


@pytest.mark.parametrize(
    "result,expected",
    [
        ({"outputs": [{"url": "https://cdn.x/video.mp4"}]}, "https://cdn.x/video.mp4"),
        ({"video": {"url": "https://cdn.x/a.webm?sig=1"}}, "https://cdn.x/a.webm?sig=1"),
        ({"video_url": "https://cdn.x/out"}, "https://cdn.x/out"),
        ({"data": {"nested": [{"file": "https://cdn.x/clip.mov"}]}}, "https://cdn.x/clip.mov"),
        ({"thumbnail": "https://cdn.x/img.png"}, None),
        ({}, None),
    ],
)
def test_extract_video_url(result, expected):
    assert runcomfy.extract_video_url(result) == expected


def test_extract_prefers_video_extension_over_generic_url():
    result = {"url": "https://cdn.x/page", "outputs": [{"url": "https://cdn.x/final.mp4"}]}
    assert runcomfy.extract_video_url(result) == "https://cdn.x/final.mp4"
