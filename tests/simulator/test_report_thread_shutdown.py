import queue
from pathlib import Path

import zsim.sim_progress.Report as Report
from zsim.sim_progress.Report.log_handler import log_queue
from zsim.sim_progress.Report.result_handler import result_queue


def _drain_queue(target_queue: queue.Queue) -> None:
    while True:
        try:
            target_queue.get_nowait()
        except queue.Empty:
            return
        target_queue.task_done()


def _assert_report_loop_stopped() -> None:
    loop = Report.__dict__.get("__event_loop")
    loop_thread = Report.__dict__.get("__loop_thread")

    assert loop is None
    assert loop_thread is None or not loop_thread.is_alive()


def test_stop_report_threads_drains_async_writers_and_allows_restart(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.chdir(tmp_path)
    _drain_queue(log_queue)
    _drain_queue(result_queue)
    Report._stop_async_tasks()

    try:
        Report.start_report_threads(None, session_id="session-a")
        log_queue.put("first log line")
        result_queue.put({"tick": 1, "skill_tag": "alpha", "UUID": "uuid-1"})

        Report.stop_report_threads()

        session_a_log = (tmp_path / "logs" / "session-a.log").read_text(encoding="utf-8").strip()
        assert session_a_log == "first log line"
        assert (tmp_path / "results" / "session-a" / "damage.csv").exists()
        _assert_report_loop_stopped()

        Report.start_report_threads(None, session_id="session-b")
        log_queue.put("second log line")

        Report.stop_report_threads()

        session_b_log = (tmp_path / "logs" / "session-b.log").read_text(encoding="utf-8").strip()
        assert session_b_log == "second log line"
        _assert_report_loop_stopped()
    finally:
        Report._stop_async_tasks()
        _drain_queue(log_queue)
        _drain_queue(result_queue)
