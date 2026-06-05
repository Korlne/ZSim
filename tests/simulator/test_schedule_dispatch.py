from types import SimpleNamespace

import pytest

from zsim.sim_progress.data_struct.schedule_dispatch import (
    LegacyEventListScheduleDispatchAdapter,
    ScheduleDispatchPort,
    create_schedule_dispatch_port,
)


def test_legacy_event_list_schedule_dispatch_adapter_preserves_queue_order():
    event_list = []
    dispatch_port = LegacyEventListScheduleDispatchAdapter(event_list)

    dispatch_port.publish_scheduled("first")
    dispatch_port.publish_scheduled_batch(["second", "third"])

    assert event_list == ["first", "second", "third"]


def test_create_schedule_dispatch_port_uses_schedule_data_without_exposing_event_list():
    schedule_data = SimpleNamespace(event_list=[])

    dispatch_port = create_schedule_dispatch_port(schedule_data=schedule_data)

    assert isinstance(dispatch_port, ScheduleDispatchPort)
    assert not hasattr(dispatch_port, "event_list")

    dispatch_port.publish_scheduled("scheduled-event")

    assert schedule_data.event_list == ["scheduled-event"]


def test_create_schedule_dispatch_port_supports_sim_instance():
    sim_instance = SimpleNamespace(schedule_data=SimpleNamespace(event_list=[]))

    dispatch_port = create_schedule_dispatch_port(sim_instance=sim_instance)
    dispatch_port.publish_scheduled_batch(["alpha", "beta"])

    assert sim_instance.schedule_data.event_list == ["alpha", "beta"]


def test_create_schedule_dispatch_port_requires_context():
    with pytest.raises(ValueError, match="sim_instance"):
        create_schedule_dispatch_port()
