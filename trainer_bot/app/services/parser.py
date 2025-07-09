import re
from typing import List

def parse_strength_cell(text: str) -> List[dict]:
    """Parses strings like '75 kg ×5 ×3' into list of sets."""
    pattern = r"(?P<weight>\d+(?:\.\d+)?)\s*kg\s*×(?P<reps>\d+)\s*×(?P<sets>\d+)"
    m = re.match(pattern, text)
    if not m:
        raise ValueError("Invalid format")
    weight = float(m.group("weight"))
    reps = int(m.group("reps"))
    sets = int(m.group("sets"))
    return [{"weight": weight, "reps": reps, "order": i+1} for i in range(sets)]
