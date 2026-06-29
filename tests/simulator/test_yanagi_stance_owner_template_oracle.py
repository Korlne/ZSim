from types import SimpleNamespace
from typing import Any, cast

import pytest

import zsim.sim_progress.Buff.BuffXLogic.YanagiStanceJougen as jougen_module
import zsim.sim_progress.Buff.BuffXLogic.YanagiStanceKagen as kagen_module


def _buff_0() -> SimpleNamespace:
    return SimpleNamespace(history=SimpleNamespace(record=None))


def _logic_harness(module: Any, logic_cls: type[Any], *, index: str) -> SimpleNamespace:
    sim_instance = SimpleNamespace(tick=120)
    buff_instance = SimpleNamespace(
        sim_instance=sim_instance,
        ft=SimpleNamespace(index=index),
    )
    logic = logic_cls(cast(Any, buff_instance))
    return SimpleNamespace(
        module=module,
        logic=logic,
        buff_instance=buff_instance,
        sim_instance=sim_instance,
    )


@pytest.mark.parametrize(
    ("module", "logic_cls", "record_cls"),
    [
        (jougen_module, jougen_module.YanagiStanceJougen, jougen_module.YanagiStanceJougenRecord),
        (kagen_module, kagen_module.YanagiStanceKagen, kagen_module.YanagiStanceKagenRecord),
    ],
)
def test_yanagi_stance_check_record_module_pins_legacy_owner_template_and_record_identity(
    monkeypatch: pytest.MonkeyPatch,
    module: Any,
    logic_cls: type[Any],
    record_cls: type[Any],
) -> None:
    harness = _logic_harness(module, logic_cls, index="yanagi-template-index")
    buff_0 = _buff_0()
    lookup_calls: list[object] = []

    def fake_find_exist_buff_dict(*, sim_instance: object) -> dict[str, dict[str, object]]:
        lookup_calls.append(sim_instance)
        return {"柳": {harness.buff_instance.ft.index: buff_0}}

    monkeypatch.setattr(module.JudgeTools, "find_exist_buff_dict", fake_find_exist_buff_dict)

    harness.logic.check_record_module()

    assert lookup_calls == [harness.sim_instance]
    assert harness.logic.buff_0 is buff_0
    assert isinstance(buff_0.history.record, record_cls)
    assert harness.logic.record is buff_0.history.record
    assert cast(Any, harness.logic.record).char is None

    existing_record = harness.logic.record
    harness.logic.check_record_module()

    assert lookup_calls == [harness.sim_instance]
    assert harness.logic.record is existing_record
    assert buff_0.history.record is existing_record


@pytest.mark.parametrize(
    ("module", "logic_cls", "registry"),
    [
        (jougen_module, jougen_module.YanagiStanceJougen, {}),
        (kagen_module, kagen_module.YanagiStanceKagen, {"柳": {}}),
    ],
)
def test_yanagi_stance_check_record_module_pins_missing_owner_or_index_errors(
    monkeypatch: pytest.MonkeyPatch,
    module: Any,
    logic_cls: type[Any],
    registry: dict[str, dict[str, object]],
) -> None:
    harness = _logic_harness(module, logic_cls, index="missing-template-index")

    def fake_find_exist_buff_dict(*, sim_instance: object) -> dict[str, dict[str, object]]:
        assert sim_instance is harness.sim_instance
        return registry

    monkeypatch.setattr(module.JudgeTools, "find_exist_buff_dict", fake_find_exist_buff_dict)

    with pytest.raises(KeyError):
        harness.logic.check_record_module()


@pytest.mark.parametrize(
    ("module", "logic_cls", "stance_now", "expected"),
    [
        (jougen_module, jougen_module.YanagiStanceJougen, True, True),
        (jougen_module, jougen_module.YanagiStanceJougen, False, False),
        (kagen_module, kagen_module.YanagiStanceKagen, True, False),
        (kagen_module, kagen_module.YanagiStanceKagen, False, True),
    ],
)
def test_yanagi_stance_special_judge_logic_pins_char_preparation_and_stance_polarity(
    monkeypatch: pytest.MonkeyPatch,
    module: Any,
    logic_cls: type[Any],
    stance_now: bool,
    expected: bool,
) -> None:
    harness = _logic_harness(module, logic_cls, index="yanagi-template-index")
    buff_0 = _buff_0()
    lookup_calls: list[object] = []
    preparation_calls: list[dict[str, object]] = []

    def fake_find_exist_buff_dict(*, sim_instance: object) -> dict[str, dict[str, object]]:
        lookup_calls.append(sim_instance)
        return {"柳": {harness.buff_instance.ft.index: buff_0}}

    def fake_check_preparation(*, buff_instance: object, buff_0: object, **kwargs: object) -> None:
        assert buff_instance is harness.buff_instance
        assert buff_0 is buff_0_ref
        preparation_calls.append(dict(kwargs))
        record = cast(Any, buff_0_ref.history.record)
        record.char = SimpleNamespace(
            CID=1221,
            stance_manager=SimpleNamespace(stance_now=stance_now),
        )

    buff_0_ref = buff_0
    monkeypatch.setattr(module.JudgeTools, "find_exist_buff_dict", fake_find_exist_buff_dict)
    monkeypatch.setattr(module, "check_preparation", fake_check_preparation)

    result = harness.logic.special_judge_logic()

    assert result is expected
    assert lookup_calls == [harness.sim_instance]
    assert preparation_calls == [{"char_CID": 1221}]
    assert harness.logic.buff_0 is buff_0
    assert harness.logic.record is buff_0.history.record
    assert cast(Any, harness.logic.record).char.CID == 1221


@pytest.mark.parametrize(
    ("module", "logic_cls"),
    [
        (jougen_module, jougen_module.YanagiStanceJougen),
        (kagen_module, kagen_module.YanagiStanceKagen),
    ],
)
def test_yanagi_stance_special_judge_logic_pins_missing_prepared_char_error(
    monkeypatch: pytest.MonkeyPatch,
    module: Any,
    logic_cls: type[Any],
) -> None:
    harness = _logic_harness(module, logic_cls, index="yanagi-template-index")
    buff_0 = _buff_0()

    def fake_find_exist_buff_dict(*, sim_instance: object) -> dict[str, dict[str, object]]:
        assert sim_instance is harness.sim_instance
        return {"柳": {harness.buff_instance.ft.index: buff_0}}

    def fake_check_preparation(*, buff_instance: object, buff_0: object, **kwargs: object) -> None:
        assert buff_instance is harness.buff_instance
        assert buff_0 is buff_0_ref
        assert kwargs == {"char_CID": 1221}

    buff_0_ref = buff_0
    monkeypatch.setattr(module.JudgeTools, "find_exist_buff_dict", fake_find_exist_buff_dict)
    monkeypatch.setattr(module, "check_preparation", fake_check_preparation)

    with pytest.raises(AttributeError):
        harness.logic.special_judge_logic()


class _BrokenStanceManager:
    @property
    def stance_now(self) -> bool:
        raise ValueError("invalid Yanagi stance state")


@pytest.mark.parametrize(
    ("module", "logic_cls"),
    [
        (jougen_module, jougen_module.YanagiStanceJougen),
        (kagen_module, kagen_module.YanagiStanceKagen),
    ],
)
def test_yanagi_stance_special_judge_logic_pins_invalid_stance_manager_error(
    monkeypatch: pytest.MonkeyPatch,
    module: Any,
    logic_cls: type[Any],
) -> None:
    harness = _logic_harness(module, logic_cls, index="yanagi-template-index")
    buff_0 = _buff_0()

    def fake_find_exist_buff_dict(*, sim_instance: object) -> dict[str, dict[str, object]]:
        assert sim_instance is harness.sim_instance
        return {"柳": {harness.buff_instance.ft.index: buff_0}}

    def fake_check_preparation(*, buff_instance: object, buff_0: object, **kwargs: object) -> None:
        assert buff_instance is harness.buff_instance
        assert buff_0 is buff_0_ref
        assert kwargs == {"char_CID": 1221}
        record = cast(Any, buff_0_ref.history.record)
        record.char = SimpleNamespace(stance_manager=_BrokenStanceManager())

    buff_0_ref = buff_0
    monkeypatch.setattr(module.JudgeTools, "find_exist_buff_dict", fake_find_exist_buff_dict)
    monkeypatch.setattr(module, "check_preparation", fake_check_preparation)

    with pytest.raises(ValueError, match="invalid Yanagi stance state"):
        harness.logic.special_judge_logic()
