from trainer_bot.app.services.parser import parse_strength_cell


def test_parse_strength_cell():
    sets = parse_strength_cell("75 kg ×5 ×3")
    assert len(sets) == 3
    assert sets[0] == {"weight": 75.0, "reps": 5, "order": 1}
