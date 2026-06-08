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


def test_create_schedule_dispatch_port_rebinds_to_current_schedule_data_event_list():
    schedule_data = SimpleNamespace(event_list=[])
    old_event_list = schedule_data.event_list
    stale_port = create_schedule_dispatch_port(schedule_data=schedule_data)
    stale_port.publish_scheduled("old-event")

    schedule_data.event_list = []
    dispatch_port = create_schedule_dispatch_port(schedule_data=schedule_data)
    dispatch_port.publish_scheduled("new-event")

    assert old_event_list == ["old-event"]
    assert schedule_data.event_list == ["new-event"]


def test_schedule_dispatch_port_public_api_does_not_expose_raw_queue_mutation():
    adapter = LegacyEventListScheduleDispatchAdapter([])
    expected_public_api = {"publish_scheduled", "publish_scheduled_batch"}
    raw_queue_api = {
        "append",
        "clear",
        "event_list",
        "event_queue",
        "extend",
        "insert",
        "pop",
        "queue",
        "remove",
    }

    assert {
        name
        for name in dir(ScheduleDispatchPort)
        if not name.startswith("_") and callable(getattr(ScheduleDispatchPort, name))
    } == expected_public_api
    assert {
        name
        for name in dir(adapter)
        if not name.startswith("_") and callable(getattr(adapter, name))
    } == expected_public_api
    for raw_name in raw_queue_api:
        assert not hasattr(ScheduleDispatchPort, raw_name)
        assert not hasattr(adapter, raw_name)


def test_create_schedule_dispatch_port_requires_context():
    with pytest.raises(ValueError, match="sim_instance"):
        create_schedule_dispatch_port()
