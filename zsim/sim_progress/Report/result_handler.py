import asyncio
import csv
import os
import queue
from typing import Any

from zsim.define import DEBUG

result_queue: queue.Queue[dict[str, Any]] = queue.Queue()

_BASE_FIELDNAMES = [
    "tick",
    "skill_tag",
    "element_type",
    "dmg_expect",
    "dmg_crit",
    "stun",
    "buildup",
    "is_anomaly",
    "is_disorder",
    "UUID",
    "crit_rate",
    "crit_dmg",
]


def report_dmg_result(**kwargs: Any) -> None:
    if not DEBUG:
        return
    result_queue.put(dict(kwargs))


def _write_damage_csv(report_file_path: str, records: list[dict[str, Any]]) -> None:
    os.makedirs(os.path.dirname(report_file_path), exist_ok=True)

    fieldnames = list(_BASE_FIELDNAMES)
    seen = set(fieldnames)
    for record in records:
        for key in record:
            if key not in seen:
                seen.add(key)
                fieldnames.append(key)

    with open(report_file_path, "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for record in records:
            writer.writerow(record)


async def async_result_writer(result_id: str) -> None:
    report_file_path = f"{result_id}/damage.csv"
    records: list[dict[str, Any]] = []

    while True:
        try:
            record = result_queue.get_nowait()
        except queue.Empty:
            await asyncio.sleep(0.01)
            continue

        records.append(record)
        await asyncio.to_thread(_write_damage_csv, report_file_path, records)
        result_queue.task_done()
