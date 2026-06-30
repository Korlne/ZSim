from collections.abc import Callable
from typing import Any, TypeVar


RecordT = TypeVar("RecordT")


def prepare_with_context(
    logic: Any,
    *,
    check_preparation_func: Callable[..., Any],
    context_builder: Callable[[Any], Any],
    **kwargs: Any,
) -> Any:
    preparation_context = context_builder(logic.buff_instance)
    return check_preparation_func(
        buff_instance=logic.buff_instance,
        buff_0=logic.buff_0,
        preparation_context=preparation_context,
        **kwargs,
    )


def ensure_owner_template_record(
    logic: Any,
    *,
    owner_name: str,
    record_factory: Callable[[], RecordT],
    context_builder: Callable[[Any], Any],
) -> RecordT:
    if logic.buff_0 is None:
        preparation_context = context_builder(logic.buff_instance)
        logic.buff_0 = preparation_context.find_sub_exist_buff_dict(owner_name)[
            logic.buff_instance.ft.index
        ]
    if logic.buff_0.history.record is None:
        logic.buff_0.history.record = record_factory()
    logic.record = logic.buff_0.history.record
    return logic.record


def ensure_equipper_template_record(
    logic: Any,
    *,
    item_name: str,
    record_factory: Callable[[], RecordT],
    context_builder: Callable[[Any], Any],
) -> RecordT:
    preparation_context = None
    if logic.equipper is None:
        preparation_context = context_builder(logic.buff_instance)
        logic.equipper = preparation_context.find_equipper(item_name)
    if logic.buff_0 is None:
        if preparation_context is None:
            preparation_context = context_builder(logic.buff_instance)
        logic.buff_0 = preparation_context.find_sub_exist_buff_dict(logic.equipper)[
            logic.buff_instance.ft.index
        ]
    if logic.buff_0.history.record is None:
        logic.buff_0.history.record = record_factory()
    logic.record = logic.buff_0.history.record
    return logic.record
