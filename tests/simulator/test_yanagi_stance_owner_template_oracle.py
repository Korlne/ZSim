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


class _FakeYanagiPreparationContext:
    def __init__(
        self,
        *,
        index: str,
        buff_0: object,
        calls: list[tuple[str, object]],
        registry: dict[str, dict[str, object]] | None = None,
    ) -> None:
        self._index = index
        self._buff_0 = buff_0
        self._calls = calls
        self._registry = registry

    def find_sub_exist_buff_dict(self, owner_name: str) -> dict[str, object]:
        self._calls.append(("find_sub_exist_buff_dict", owner_name))
        if self._registry is not None:
            return self._registry[owner_name]
        return {self._index: self._buff_0}


def _install_preparation_context(
    monkeypatch: pytest.MonkeyPatch,
    *,
    module: Any,
    harness: SimpleNamespace,
    buff_0: SimpleNamespace,
    registry: dict[str, dict[str, object]] | None = None,
) -> tuple[list[object], list[tuple[str, object]]]:
    context_build_calls: list[object] = []
    context_calls: list[tuple[str, object]] = []

    def fake_build_preparation_context_from_buff(
        buff_instance: object,
    ) -> _FakeYanagiPreparationContext:
        context_build_calls.append(buff_instance)
        return _FakeYanagiPreparationContext(
            index=harness.buff_instance.ft.index,
            buff_0=buff_0,
            calls=context_calls,
            registry=registry,
        )

    monkeypatch.setattr(
        module,
        "build_preparation_context_from_buff",
        fake_build_preparation_context_from_buff,
    )
    return context_build_calls, context_calls


@pytest.mark.parametrize(
    ("module", "logic_cls", "record_cls"),
    [
        (jougen_module, jougen_module.YanagiStanceJougen, jougen_module.YanagiStanceJougenRecord),
        (kagen_module, kagen_module.YanagiStanceKagen, kagen_module.YanagiStanceKagenRecord),
    ],
)
def test_yanagi_stance_check_record_module_pins_context_owner_template_and_record_identity(
    monkeypatch: pytest.MonkeyPatch,
    module: Any,
    logic_cls: type[Any],
    record_cls: type[Any],
) -> None:
    harness = _logic_harness(module, logic_cls, index="yanagi-template-index")
    buff_0 = _buff_0()
    context_build_calls, context_calls = _install_preparation_context(
        monkeypatch,
        module=module,
        harness=harness,
        buff_0=buff_0,
    )

    harness.logic.check_record_module()

    assert context_build_calls == [harness.buff_instance]
    assert context_calls == [("find_sub_exist_buff_dict", "柳")]
    assert harness.logic.buff_0 is buff_0
    assert isinstance(buff_0.history.record, record_cls)
    assert harness.logic.record is buff_0.history.record
    assert cast(Any, harness.logic.record).char is None

    existing_record = harness.logic.record
    harness.logic.check_record_module()

    assert context_build_calls == [harness.buff_instance]
    assert context_calls == [("find_sub_exist_buff_dict", "柳")]
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
    buff_0 = _buff_0()
    _install_preparation_context(
        monkeypatch,
        module=module,
        harness=harness,
        buff_0=buff_0,
        registry=registry,
    )

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
    context_build_calls, context_calls = _install_preparation_context(
        monkeypatch,
        module=module,
        harness=harness,
        buff_0=buff_0,
    )
    preparation_calls: list[dict[str, object]] = []

    def fake_check_preparation(
        *,
        buff_instance: object,
        buff_0: object,
        preparation_context: object,
        **kwargs: object,
    ) -> None:
        assert buff_instance is harness.buff_instance
        assert buff_0 is buff_0_ref
        assert isinstance(preparation_context, _FakeYanagiPreparationContext)
        preparation_calls.append(dict(kwargs))
        record = cast(Any, buff_0_ref.history.record)
        record.char = SimpleNamespace(
            CID=1221,
            stance_manager=SimpleNamespace(stance_now=stance_now),
        )

    buff_0_ref = buff_0
    monkeypatch.setattr(module, "check_preparation", fake_check_preparation)

    result = harness.logic.special_judge_logic()

    assert result is expected
    assert context_build_calls == [harness.buff_instance, harness.buff_instance]
    assert context_calls == [("find_sub_exist_buff_dict", "柳")]
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
    _install_preparation_context(
        monkeypatch,
        module=module,
        harness=harness,
        buff_0=buff_0,
    )

    def fake_check_preparation(
        *,
        buff_instance: object,
        buff_0: object,
        preparation_context: object,
        **kwargs: object,
    ) -> None:
        assert buff_instance is harness.buff_instance
        assert buff_0 is buff_0_ref
        assert isinstance(preparation_context, _FakeYanagiPreparationContext)
        assert kwargs == {"char_CID": 1221}

    buff_0_ref = buff_0
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
    _install_preparation_context(
        monkeypatch,
        module=module,
        harness=harness,
        buff_0=buff_0,
    )

    def fake_check_preparation(
        *,
        buff_instance: object,
        buff_0: object,
        preparation_context: object,
        **kwargs: object,
    ) -> None:
        assert buff_instance is harness.buff_instance
        assert buff_0 is buff_0_ref
        assert isinstance(preparation_context, _FakeYanagiPreparationContext)
        assert kwargs == {"char_CID": 1221}
        record = cast(Any, buff_0_ref.history.record)
        record.char = SimpleNamespace(stance_manager=_BrokenStanceManager())

    buff_0_ref = buff_0
    monkeypatch.setattr(module, "check_preparation", fake_check_preparation)

    with pytest.raises(ValueError, match="invalid Yanagi stance state"):
        harness.logic.special_judge_logic()
