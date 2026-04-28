from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dnf.route_loader import list_routes, load_route_config, load_route_directions


def test_load_route_config_reads_yaml_directions() -> None:
    config = load_route_config("yaoqi_default")

    assert config["name"] == "yaoqi_default"
    assert config["display_name"] == "妖气追踪默认路线"
    assert config["directions"] == ["RIGHT", "RIGHT", "UP", "RIGHT"]


def test_list_routes_includes_yaml_files() -> None:
    routes = list_routes()
    assert "yaoqi_default" in routes


def test_load_route_config_rejects_invalid_direction(tmp_path: Path) -> None:
    route_path = tmp_path / "bad_route.yaml"
    route_path.write_text(
        yaml.safe_dump(
            {
                "name": "bad_route",
                "directions": ["RIGHT", "RIGHT_UP"],
            },
            allow_unicode=True,
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="非法方向"):
        load_route_config("bad_route", tmp_path)


def test_load_route_directions_returns_list_only() -> None:
    assert load_route_directions("yaoqi_default") == ["RIGHT", "RIGHT", "UP", "RIGHT"]
