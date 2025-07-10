import datetime
from trainer_bot.app.models import Role, Invite, User, Workout, Athlete
import uuid
from trainer_bot.app.services.db import get_session


def test_role_enum_values():
    assert [r.value for r in Role] == ["coach", "athlete", "superadmin"]


def test_invite_defaults():
    with get_session() as session:
        user = session.query(User).filter(User.telegram_id == 9999).first()
        if not user:
            user = User(telegram_id=9999, first_name="Coach", role=Role.coach.value)
            session.add(user)
            session.commit()
            session.refresh(user)
        invite = Invite(jti=str(uuid.uuid4()), issued_by=user.id)
        session.add(invite)
        session.commit()
        session.refresh(invite)
        assert invite.used is False
        assert invite.role == Role.athlete.value


def test_user_default_timezone():
    with get_session() as session:
        user = session.query(User).filter(User.telegram_id == 9998).first()
        if not user:
            user = User(telegram_id=9998, first_name="U")
            session.add(user)
            session.commit()
            session.refresh(user)
        assert user.timezone == "Europe/Moscow"


def test_workout_time_optional():
    with get_session() as session:
        athlete = Athlete(name="A")
        session.add(athlete)
        session.commit()
        session.refresh(athlete)
        w = Workout(
            athlete_id=athlete.id,
            date=datetime.date(2025, 1, 1),
            type="strength",
            title="W",
        )
        session.add(w)
        session.commit()
        session.refresh(w)
        assert w.time is None


