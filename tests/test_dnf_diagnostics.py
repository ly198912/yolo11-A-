import json
import os
import subprocess
import sys
from pathlib import Path

from dnf.bug_check import build_check_report
from dnf.detector import _default_weights
from dnf.diagnostics import write_exception_report


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_exception_report_points_to_exact_project_file_and_line(tmp_path):
    source = tmp_path / "broken_worker.py"
    source.write_text(
        "def explode():\n"
        "    values = {'ok': True}\n"
        "    return values['missing']\n",
        encoding="utf-8",
    )
    namespace = {}
    exec(compile(source.read_text(encoding="utf-8"), str(source), "exec"), namespace)

    try:
        namespace["explode"]()
    except KeyError as exc:
        report_path = write_exception_report(
            type(exc),
            exc,
            exc.__traceback__,
            source="test",
            report_dir=tmp_path / "reports",
            project_root=tmp_path,
        )

    payload = json.loads(report_path.with_suffix(".json").read_text(encoding="utf-8"))
    assert payload["primary_location"]["file"] == str(source.resolve())
    assert payload["primary_location"]["line"] == 3
    assert payload["exception"]["type"] == "KeyError"
    assert "values['missing']" in report_path.read_text(encoding="utf-8")
    assert (tmp_path / "reports" / "LATEST_BUG_REPORT.txt").exists()
    assert (tmp_path / "reports" / "REPORT_FOR_AI.txt").exists()


def test_exception_report_hides_common_secret_values(tmp_path):
    try:
        raise RuntimeError("token=abc123 password:open-sesame")
    except RuntimeError as exc:
        report_path = write_exception_report(
            type(exc),
            exc,
            exc.__traceback__,
            source="test",
            report_dir=tmp_path / "reports",
            project_root=tmp_path,
        )

    report = report_path.read_text(encoding="utf-8")
    assert "abc123" not in report
    assert "open-sesame" not in report
    assert "token=<hidden>" in report


def test_static_check_covers_dnf_sources_dependencies_and_weights(monkeypatch):
    monkeypatch.delenv("DNF_WEIGHTS", raising=False)

    report = build_check_report()

    assert report["checked_files"]
    assert "mss" in report["dependencies"]
    assert report["weight_candidates"] == [str((PROJECT_ROOT / "dnf" / "ldd.pt").resolve())]
    assert report["passed"] is True


def test_detector_uses_ldd_weights_by_default(monkeypatch):
    monkeypatch.delenv("DNF_WEIGHTS", raising=False)

    assert _default_weights() == PROJECT_ROOT / "dnf" / "ldd.pt"


def test_background_thread_exception_creates_report(tmp_path):
    script = (
        "import threading\n"
        "from dnf.diagnostics import install_diagnostics\n"
        "install_diagnostics()\n"
        "def explode():\n"
        "    raise RuntimeError('thread boom')\n"
        "thread = threading.Thread(target=explode, name='diagnostic-test-thread')\n"
        "thread.start()\n"
        "thread.join()\n"
    )
    env = os.environ.copy()
    env["DNF_BUG_REPORT_DIR"] = str(tmp_path)

    subprocess.run([sys.executable, "-c", script], cwd=PROJECT_ROOT, env=env, check=True)

    payload = json.loads((tmp_path / "LATEST_BUG_REPORT.json").read_text(encoding="utf-8"))
    assert payload["source"] == "background-thread"
    assert payload["thread"] == "diagnostic-test-thread"
    assert payload["exception"]["message"] == "thread boom"


def test_outer_launcher_catches_startup_failure(tmp_path):
    module_dir = tmp_path / "modules"
    module_dir.mkdir()
    (module_dir / "bad_startup.py").write_text("raise RuntimeError('startup boom')\n", encoding="utf-8")
    env = os.environ.copy()
    env["DNF_BUG_REPORT_DIR"] = str(tmp_path / "reports")
    env["PYTHONPATH"] = os.pathsep.join([str(PROJECT_ROOT), str(module_dir)])
    script = (
        "from dnf.run_with_diagnostics import run_entrypoint\n"
        "raise SystemExit(run_entrypoint('bad_startup'))\n"
    )

    result = subprocess.run([sys.executable, "-c", script], cwd=PROJECT_ROOT, env=env, check=False)

    assert result.returncode == 1
    payload = json.loads((tmp_path / "reports" / "LATEST_BUG_REPORT.json").read_text(encoding="utf-8"))
    assert payload["source"] == "startup-or-fatal"
    assert payload["exception"]["message"] == "startup boom"


def test_handled_loguru_exception_still_creates_report(tmp_path):
    script = (
        "from loguru import logger\n"
        "from dnf.diagnostics import install_diagnostics\n"
        "install_diagnostics()\n"
        "try:\n"
        "    raise ValueError('handled boom')\n"
        "except ValueError:\n"
        "    logger.exception('caught runtime error')\n"
    )
    env = os.environ.copy()
    env["DNF_BUG_REPORT_DIR"] = str(tmp_path)

    subprocess.run([sys.executable, "-c", script], cwd=PROJECT_ROOT, env=env, check=True)

    payload = json.loads((tmp_path / "LATEST_BUG_REPORT.json").read_text(encoding="utf-8"))
    assert payload["source"] == "handled-loguru"
    assert payload["exception"]["message"] == "handled boom"
