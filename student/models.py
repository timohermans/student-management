from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import relationship, backref
from .database import Base
from datetime import datetime

semester_students = Table(
    "semester_students",
    Base.metadata,
    Column("student_id", ForeignKey("student.id")),
    Column("semester_id", ForeignKey("semester.id")),
)


note_involved = Table(
    "note_involved",
    Base.metadata,
    Column("student_id", ForeignKey("student.id"), nullable=True),
    Column("note_id", ForeignKey("note.id"))
)


class Student(Base):
    __tablename__ = "student"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=False, nullable=False)
    canvas_id = Column(Integer, unique=True, nullable=False)
    avatar_url = Column(String(300))
    date_created = Column(DateTime, nullable=False, default=datetime.utcnow)

    notes = relationship(
        "Note",
        secondary=note_involved,
        lazy="subquery",
        backref=backref("notes", lazy=True),
    )


class Note(Base):
    __tablename__ = "note"

    id = Column(Integer, primary_key=True)
    text = Column(Text, nullable=False)
    attachment = Column(String(255), nullable=True)
    date_created = Column(DateTime, nullable=False, default=datetime.utcnow)


class Semester(Base):
    __tablename__ = "semester"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=False, nullable=False)
    section = Column(String(255), unique=True, nullable=False)
    term = Column(String(255), unique=False, nullable=False)
    start_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    end_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    canvas_id = Column(Integer, unique=True)
    date_created = Column(DateTime, nullable=False, default=datetime.utcnow)

    students = relationship(
        "Student",
        secondary=semester_students,
        lazy="subquery",
        backref=backref("students", lazy=True),
    )
