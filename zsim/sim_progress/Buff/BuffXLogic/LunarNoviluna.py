from typing import Any

from zsim.sim_progress.data_struct.schedule_dispatch import (
    ScheduledEventEmitter,
    ScheduledEventEmitterProvider,
)

from .. import Buff, JudgeTools, check_preparation, find_tick


class LunarNovilunaRecord:
    def __init__(self):
        self.equipper = None
        self.char = None
        self.enegy_value_map = {1: 3, 2: 3.5, 3: 4, 4: 4.5, 5: 5}
        self.sub_exist_buff_dict = None


class LunarNoviluna(Buff.BuffLogic):
    def __init__(
        self,
        buff_instance,
        scheduled_event_emitter_provider: ScheduledEventEmitterProvider | None = None,
    ):
        super().__init__(buff_instance)
        self.buff_instance: Buff = buff_instance
        self._scheduled_event_emitter_provider = (
            scheduled_event_emitter_provider
            or ScheduledEventEmitterProvider.from_sim_instance_getter(
                lambda: self.buff_instance.sim_instance
            )
        )
        self.xstart = self.special_start_logic
        self.equipper = None
        self.buff_0: Any = None
        self.record: Any = None

    def get_prepared(self, **kwargs):
        return check_preparation(buff_instance=self.buff_instance, buff_0=self.buff_0, **kwargs)

    def _scheduled_event_emitter(self) -> ScheduledEventEmitter:
        return self._scheduled_event_emitter_provider.create_emitter()

    def check_record_module(self):
        if self.equipper is None:
            self.equipper = JudgeTools.find_equipper(
                "「月相」-朔", sim_instance=self.buff_instance.sim_instance
            )
        if self.buff_0 is None:
            self.buff_0 = JudgeTools.find_exist_buff_dict(
                sim_instance=self.buff_instance.sim_instance
            )[self.equipper][self.buff_instance.ft.index]
        if self.buff_0.history.record is None:
            self.buff_0.history.record = LunarNovilunaRecord()
        self.record = self.buff_0.history.record

    def special_start_logic(self, **kwargs):
        self.check_record_module()
        self.get_prepared(equipper="「月相」-朔", sub_exist_buff_dict=1)

        from zsim.sim_progress.data_struct import ScheduleRefreshData

        energy_value = self.record.enegy_value_map[self.buff_instance.ft.refinement]
        refresh_data = ScheduleRefreshData(
            sp_target=(self.record.char.NAME,),
            sp_value=energy_value,
        )
        self._scheduled_event_emitter().emit_scheduled(refresh_data)
        self.buff_instance.simple_start(
            find_tick(sim_instance=self.buff_instance.sim_instance),
            self.record.sub_exist_buff_dict,
        )
