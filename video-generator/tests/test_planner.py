import os

import pytest

from videogen import planner

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


def test_load_plan_file():
    plan = planner.load_plan_file(os.path.join(FIXTURES, "plan.json"))
    assert plan.title == "Test video"
    assert len(plan.scenes) == 2
    assert plan.scenes[0].duration == 2
    assert "red cube" in plan.scenes[0].prompt


def test_plan_from_dict_defaults_duration():
    plan = planner.plan_from_dict({"title": "t", "scenes": [{"prompt": "p"}]})
    assert plan.scenes[0].duration == 5


@pytest.mark.parametrize(
    "data",
    [
        {"scenes": [{"prompt": "p"}]},                      # missing title
        {"title": "t"},                                      # missing scenes
        {"title": "t", "scenes": []},                        # empty scenes
        {"title": "t", "scenes": [{"duration": 5}]},         # scene missing prompt
        {"title": "t", "scenes": [{"prompt": "   "}]},       # blank prompt
    ],
)
def test_plan_from_dict_rejects_invalid(data):
    with pytest.raises(ValueError):
        planner.plan_from_dict(data)


def test_plan_roundtrip():
    plan = planner.plan_from_dict({"title": "t", "scenes": [{"prompt": "p", "duration": 6}]})
    assert planner.plan_from_dict(plan.to_dict()).scenes[0].duration == 6


PLAN_JSON = '{"title": "t", "scenes": [{"prompt": "p1", "duration": 5}, {"prompt": "p2", "duration": 5}]}'


@pytest.mark.parametrize(
    "text",
    [
        PLAN_JSON,
        f"```json\n{PLAN_JSON}\n```",
        f"Here is your plan:\n\n{PLAN_JSON}\n\nEnjoy!",
    ],
)
def test_extract_json_object_tolerates_wrapping(text):
    assert planner.extract_json_object(text)["title"] == "t"


def test_extract_json_object_rejects_no_json():
    with pytest.raises(ValueError, match="no JSON object"):
        planner.extract_json_object("sorry, I cannot do that")


class FakePost:
    def __init__(self, content=PLAN_JSON, status_code=200):
        self.status_code = status_code
        self.text = ""
        self._content = content
        self.captured = None

    def __call__(self, url, json=None, headers=None, timeout=None):
        self.captured = {"url": url, "body": json, "headers": headers}
        return self

    def json(self):
        return {"choices": [{"message": {"content": self._content}}]}


def test_generate_plan_deepseek(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "dsk")
    fake = FakePost()
    monkeypatch.setattr(planner.requests, "post", fake)
    plan = planner.generate_plan("cats", 2, 5, provider_name="deepseek")
    assert plan.title == "t" and len(plan.scenes) == 2
    assert fake.captured["url"] == "https://api.deepseek.com/chat/completions"
    assert fake.captured["body"]["model"] == "deepseek-chat"
    assert fake.captured["body"]["response_format"] == {"type": "json_object"}
    assert fake.captured["headers"]["Authorization"] == "Bearer dsk"


def test_generate_plan_minimax(monkeypatch):
    monkeypatch.setenv("MINIMAX_API_KEY", "mmx")
    fake = FakePost(content=f"```json\n{PLAN_JSON}\n```")
    monkeypatch.setattr(planner.requests, "post", fake)
    plan = planner.generate_plan(None, 2, 5, provider_name="minimax", model="MiniMax-Text-01")
    assert len(plan.scenes) == 2
    assert fake.captured["url"] == "https://api.minimax.io/v1/chat/completions"
    assert fake.captured["body"]["model"] == "MiniMax-Text-01"
    assert "response_format" not in fake.captured["body"]


def test_generate_plan_truncates_extra_scenes(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "dsk")
    monkeypatch.setattr(planner.requests, "post", FakePost())
    plan = planner.generate_plan("cats", 1, 5, provider_name="deepseek")
    assert len(plan.scenes) == 1


def test_generate_plan_missing_key(monkeypatch):
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="DEEPSEEK_API_KEY"):
        planner.generate_plan("cats", 2, 5, provider_name="deepseek")


def test_generate_plan_unknown_provider():
    with pytest.raises(ValueError, match="unknown planner"):
        planner.generate_plan("cats", 2, 5, provider_name="gpt9000")
