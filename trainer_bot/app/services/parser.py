import re
from typing import List

def parse_strength_cell(text: str) -> List[dict]:
    """Parses strings like '75 kg ×5 ×3' into list of sets."""
    pattern = r"(?P<weight>[0-9]+(?:\.[0-9]+)?(?:-[0-9]+(?:\.[0-9]+)?)?)\s*kg\s*×\s*(?P<reps>\d+)\s*×\s*(?P<sets>\d+)"
    m = re.match(pattern, text.strip())
    if not m:
        raise ValueError("Invalid format")
    weight_part = m.group("weight")
    weights = [float(w) for w in weight_part.split("-")]
    reps = int(m.group("reps"))
    sets_count = int(m.group("sets"))
    result = []
    for w in weights:
        for i in range(sets_count):
            result.append({"weight": w, "reps": reps, "order": i+1})
    return result
