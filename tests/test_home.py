from datetime import datetime

import pytest
from student.database import db
from student.models import Semester


def test_shows_no_initial_semesters(client, app):
    response = client.get("/")

    assert response.status_code == 200

    assert b"No semesters managed yet" in response.data


def test_shows_semesters_in_db(client, app):
    semester = Semester(
        name="INTERN5-CMK",
        section="Ass1 T. Hermans",
        term="2122vj",
        start_at=datetime(2022, 1, 16),
        end_at=datetime(2022, 8, 7),
    )
    with app.app_context():
        db.session.add(semester)
        db.session.commit()

    response = client.get("/")

    assert response.status_code == 200
    assert b'href="/semester/1"' in response.data
    assert b'INTERN5-CMK - Ass1 T. Hermans - 2122vj'

