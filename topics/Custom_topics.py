#!/usr/bin/env python3
"""A /pillars és /gates üzenetek közös adatformátuma.

A meglévő ament_python package megtartása miatt a topicok std_msgs/String
üzenetek, amelyek verziózott JSON-t tartalmaznak. Nem generált .msg típusok.
"""

from dataclasses import asdict, dataclass
import json
import math
from typing import ClassVar

from std_msgs.msg import String


SCHEMA_VERSION = 1


@dataclass(frozen=True)
class Pillar:
    COLOR_UNKNOWN: ClassVar[int] = 0
    COLOR_RED: ClassVar[int] = 1
    COLOR_GREEN: ClassVar[int] = 2
    COLOR_OTHER: ClassVar[int] = 3

    id: int
    x: float
    y: float
    color: int = COLOR_UNKNOWN
    color_confidence: float = 0.0
    last_seen_sec: int = 0
    last_seen_nanosec: int = 0


@dataclass(frozen=True)
class Gate:
    TYPE_UNKNOWN: ClassVar[int] = 0
    TYPE_START: ClassVar[int] = 1
    TYPE_INTERMEDIATE: ClassVar[int] = 2
    TYPE_GOAL: ClassVar[int] = 3

    id: int
    pillar_id_a: int
    pillar_id_b: int
    x: float
    y: float
    yaw: float
    type: int
    post_spacing_m: float


def _message(kind, stamp, items, frame_id):
    data = {
        'version': SCHEMA_VERSION,
        'frame_id': frame_id,
        'stamp': {'sec': int(stamp.sec), 'nanosec': int(stamp.nanosec)},
        kind: [asdict(item) for item in items],
    }
    return String(data=json.dumps(data, separators=(',', ':'), allow_nan=False))


def pillars_to_msg(stamp, pillars, frame_id='map'):
    """A teljes, jelenleg ismert oszloplista -> ROS 2 String."""
    return _message('pillars', stamp, pillars, frame_id)


def gates_to_msg(stamp, gates, frame_id='map'):
    """A teljes, jelenleg érvényes kapulista -> ROS 2 String."""
    return _message('gates', stamp, gates, frame_id)


def _read(msg, kind, item_type):
    try:
        data = json.loads(msg.data)
        if not isinstance(data, dict) or data.get('version') != SCHEMA_VERSION:
            raise ValueError('Nem támogatott üzenetverzió')
        if data.get('frame_id') != 'map':
            raise ValueError('Csak map koordináta-rendszer támogatott')
        stamp = data['stamp']
        if not isinstance(stamp['sec'], int) or not isinstance(stamp['nanosec'], int):
            raise ValueError('Hibás időbélyeg')
        if not isinstance(data[kind], list):
            raise ValueError('Az elemeknek listában kell lenniük')
        items = [item_type(**item) for item in data[kind]]
        ids = [item.id for item in items]
        if any(not isinstance(i, int) or i < 1 for i in ids) or len(ids) != len(set(ids)):
            raise ValueError('Hibás vagy ismétlődő azonosító')
        for item in items:
            if not (math.isfinite(item.x) and math.isfinite(item.y)):
                raise ValueError('Nem véges pozíció')
            if kind == 'pillars':
                if item.color not in (0, 1, 2, 3) or not (0 <= item.color_confidence <= 1):
                    raise ValueError('Hibás oszlopszín vagy bizonyosság')
            else:
                if item.type not in (0, 1, 2, 3):
                    raise ValueError('Hibás kaputípus')
                if not math.isfinite(item.yaw) or not math.isfinite(item.post_spacing_m):
                    raise ValueError('Hibás kapugeometria')
        return stamp, items
    except (TypeError, KeyError, AttributeError, json.JSONDecodeError) as exc:
        raise ValueError(f'Érvénytelen {kind} JSON: {exc}') from exc


def read_pillars(msg):
    """ROS 2 String -> (időbélyeg-szótár, Pillar lista)."""
    return _read(msg, 'pillars', Pillar)


def read_gates(msg):
    """ROS 2 String -> (időbélyeg-szótár, Gate lista)."""
    return _read(msg, 'gates', Gate)

