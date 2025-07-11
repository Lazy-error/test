from trainer_bot.app.services.parser import parse_strength_cell, parse_cardio_cell


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


def test_parse_cardio_cell():
    data = parse_cardio_cell("5 km 25:30 150")
    assert data["distance_km"] == 5.0
    assert data["duration_sec"] == 1530
    assert data["avg_hr"] == 150


def test_parse_strength_cell_with_spaces():
    sets = parse_strength_cell(" 75 kg ×5 ×2 ")
    assert len(sets) == 2
    assert sets[0]["weight"] == 75.0


def test_parse_strength_cell_with_rest():
    sets = parse_strength_cell("50 kg ×5 ×2 60")
    assert all(s["rest_sec"] == 60 for s in sets)


def test_parse_cardio_cell_distance_only():
    data = parse_cardio_cell("3 km")
    assert data["distance_km"] == 3.0
    assert data["duration_sec"] is None
    assert data["avg_hr"] is None


def test_parse_cardio_cell_invalid():
    import pytest
    with pytest.raises(ValueError):
        parse_cardio_cell("bad data")
