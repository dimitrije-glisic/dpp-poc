from sqlalchemy import func, select

from app.models import Battery
from scripts.seed import seed


def test_seed_inserts_sample_data(db_session):
    inserted, skipped = seed(db_session)
    assert inserted >= 5
    assert skipped == 0
    assert all(b.is_demo_data for b in db_session.scalars(select(Battery)))


def test_seed_is_idempotent(db_session):
    first_inserted, _ = seed(db_session)
    inserted, skipped = seed(db_session)
    assert inserted == 0
    assert skipped == first_inserted
    assert db_session.scalar(select(func.count()).select_from(Battery)) == first_inserted
