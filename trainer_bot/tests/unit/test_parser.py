from trainer_bot.app.services.parser import parse_strength_cell


def test_parse_strength_cell():
    sets = parse_strength_cell("75 kg ×5 ×3")
    assert len(sets) == 3
    assert sets[0] == {"weight": 75.0, "reps": 5, "order": 1}


def test_parse_strength_cell_multiple_weights():
    sets = parse_strength_cell("22-23 kg ×8 ×2")
    assert len(sets) == 4
    assert sets[0]["weight"] == 22.0
    assert sets[1]["weight"] == 22.0
    assert sets[2]["weight"] == 23.0


def test_parse_strength_cell_invalid():
    import pytest
    with pytest.raises(ValueError):
        parse_strength_cell("invalid")
