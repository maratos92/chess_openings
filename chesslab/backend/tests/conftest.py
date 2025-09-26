from __future__ import annotations

import pytest

from ..db import Base, init_engine, get_engine, db_session


def pytest_configure():
    init_engine("sqlite:///:memory:")
    engine = get_engine()
    Base.metadata.create_all(engine)


@pytest.fixture(autouse=True)
def session_scope():
    connection = get_engine().connect()
    trans = connection.begin()
    db_session.configure(bind=connection)
    yield
    db_session.remove()
    trans.rollback()
    connection.close()
