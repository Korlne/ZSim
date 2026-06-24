import asyncio

import pytest
from fastapi.testclient import TestClient

from zsim.api import app
from zsim.api_src.services.database.session_db import get_session_db
from zsim.api_src.services.sim_controller import sim_controller as controller_module
from zsim.api_src.services.sim_controller.sim_controller import SimController
from zsim.models.session.session_result import (
    BUFF_TIMELINE_PUBLIC_FIELDS,
    DAMAGE_RESULT_SECTIONS,
    BuffResult,
    DmgResult,
    NormalModeResult,
    NormalResultPayload,
)
from zsim.simulator.simulator_class import Confirmation


client = TestClient(app)
SMOKE_SESSION_ID = "electron-smoke-contract-session"


def _session_payload() -> dict[str, object]:
    return {
        "session_id": SMOKE_SESSION_ID,
        "session_name": "Electron smoke contract",
    }


def _session_run_payload() -> dict[str, object]:
    return {
        "stop_tick": 1,
        "mode": "normal",
        "common_config": {
            "session_id": SMOKE_SESSION_ID,
            "char_config": [
                {"name": "仪玄"},
                {"name": "耀嘉音"},
                {"name": "扳机"},
            ],
            "enemy_config": {"index_id": 11412, "adjustment_id": 22412},
            "apl_path": "zsim/data/APLData/仪玄-耀嘉音-扳机.toml",
        },
    }


@pytest.mark.asyncio
async def test_electron_normal_full_simulation_smoke_contract(monkeypatch) -> None:
    db = await get_session_db()
    await db.delete_session(SMOKE_SESSION_ID)

    controller = SimController()
    controller._queue = asyncio.Queue()
    controller._running_tasks.clear()

    def fake_runtime_simulator(common_cfg, sim_cfg, stop_tick):
        assert common_cfg.session_id == SMOKE_SESSION_ID
        assert sim_cfg is None
        assert stop_tick == 1
        return Confirmation(
            session_id=common_cfg.session_id,
            status="completed",
            timestamp=1,
            sim_cfg=sim_cfg,
        )

    async def fake_process_simulation_result(self, confirmation):
        assert confirmation.session_id == SMOKE_SESSION_ID
        damage_payload = {section: [] for section in DAMAGE_RESULT_SECTIONS}
        return NormalModeResult(
            mode="normal",
            result=NormalResultPayload(
                dmg_result=DmgResult(root=damage_payload),
                buff_result=BuffResult(
                    root={
                        "smoke-agent": [
                            {
                                "Task": "smoke-buff",
                                "Start": 1,
                                "Finish": 2,
                                "Value": 1.0,
                            }
                        ]
                    }
                ),
            ),
        )

    monkeypatch.setattr(
        controller_module,
        "_run_default_runtime_simulator",
        fake_runtime_simulator,
    )
    monkeypatch.setattr(
        SimController,
        "_process_simulation_result",
        fake_process_simulation_result,
    )

    try:
        create_response = client.post("/api/sessions/", json=_session_payload())
        assert create_response.status_code == 200

        run_response = client.post(
            f"/api/sessions/{SMOKE_SESSION_ID}/run?test_mode=true",
            json=_session_run_payload(),
        )
        assert run_response.status_code == 200
        assert run_response.json() == {
            "code": 0,
            "message": "Session started successfully",
            "session_id": SMOKE_SESSION_ID,
        }

        status_response = client.get(f"/api/sessions/{SMOKE_SESSION_ID}/status")
        assert status_response.status_code == 200
        status_payload = status_response.json()
        assert status_payload["status"] == "completed"

        result_payload = status_payload["result"]
        assert isinstance(result_payload, list)
        assert result_payload[0]["mode"] == "normal"

        data_analysis_payload = result_payload[0]["result"]
        assert tuple(data_analysis_payload) == ("dmg_result", "buff_result")
        assert tuple(data_analysis_payload["dmg_result"]) == DAMAGE_RESULT_SECTIONS

        buff_entry = data_analysis_payload["buff_result"]["smoke-agent"][0]
        assert tuple(buff_entry) == BUFF_TIMELINE_PUBLIC_FIELDS

        read_response = client.get(f"/api/sessions/{SMOKE_SESSION_ID}")
        assert read_response.status_code == 200
        assert read_response.json()["session_result"] == result_payload
    finally:
        await db.delete_session(SMOKE_SESSION_ID)
        controller._queue = asyncio.Queue()
