import re
from typing import List

def parse_strength_cell(text: str) -> List[dict]:
    """Parses strings like '75 kg ×5 ×3' into list of sets."""
    pattern = r"(?P<weight>[0-9]+(?:\.[0-9]+)?(?:-[0-9]+(?:\.[0-9]+)?)?)\s*kg\s*×\s*(?P<reps>\d+)\s*×\s*(?P<sets>\d+)(?:\s+(?P<rest>\d+))?"
    m = re.match(pattern, text.strip())
    if not m:
        raise ValueError("Invalid format")
    weight_part = m.group("weight")
    weights = [float(w) for w in weight_part.split("-")]
    reps = int(m.group("reps"))
    sets_count = int(m.group("sets"))
    rest = m.group("rest")
    rest_sec = int(rest) if rest else None
    result = []
    for w in weights:
        for i in range(sets_count):
            item = {"weight": w, "reps": reps, "order": i+1}
            if rest_sec is not None:
                item["rest_sec"] = rest_sec
            result.append(item)
    return result


def parse_cardio_cell(text: str) -> dict:
    """Parses strings like '5 km 25:30 150' into a cardio set."""
    pattern = r"(?P<distance>[0-9]+(?:\.[0-9]+)?)\s*km(?:\s+(?P<duration>\d+:\d{2}))?(?:\s+(?P<hr>\d+))?"
    m = re.match(pattern, text.strip())
    if not m:
        raise ValueError("Invalid format")
    distance = float(m.group("distance"))
    duration = m.group("duration")
    dur_sec = None
    if duration:
        minutes, seconds = duration.split(":")
        dur_sec = int(minutes) * 60 + int(seconds)
    hr = m.group("hr")
    return {
        "distance_km": distance,
        "duration_sec": dur_sec,
        "avg_hr": int(hr) if hr else None,
        "order": 1,
    }
