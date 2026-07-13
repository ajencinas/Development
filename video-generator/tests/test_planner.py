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
