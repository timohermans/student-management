import json
from datetime import datetime

import requests
from flask import current_app as app


class Course:
    def __init__(self, _id, name, term):
        self._id = _id
        self.name = name
        self.term = Term(**term)


class Term:
    def __init__(self, _id, name, startAt, endAt):
        self._id = _id
        self.name = name
        self.startAt = datetime.fromisoformat(startAt) if startAt is not None else None
        self.endAt = datetime.fromisoformat(endAt) if endAt is not None else None


class Section:
    def __init__(self, _id, name):
        self._id = _id
        self.name = name
        self.students = []


class Enrollment:
    def __init__(self, _id, user, section):
        self._id = _id
        self.user = User(**user)
        self.section = Section(**section)


class User:
    def __init__(self, _id, name, avatarUrl):
        self._id = _id
        self.name = name
        self.avatarUrl = avatarUrl


class CourseDetail:
    def __init__(self, _id, name, term, sectionsConnection, enrollmentsConnection):
        self.id = _id
        self.name = name
        self.term = Term(**term)
        self.sections = [Section(**s) for s in sectionsConnection["nodes"]]
        self.enrollments = [Enrollment(**r) for r in enrollmentsConnection["nodes"]]


def get(query: str) -> requests.Response:
    api_url = app.config["CANVAS_API_URL"]
    token = f"Bearer {app.config['CANVAS_API_TOKEN']}"

    r = requests.post(
        api_url,
        json={"operationName": "MyQuery", "query": query, "variables": None},
        headers={"Authorization": token},
    )

    return r


def get_available_courses():
    query = """query MyQuery {
        allCourses {
            _id
            name
            term {
                _id
                name
                startAt
                endAt
            }
        }
}
    """
    response = get(query)
    courses = []

    if response.status_code == 200:
        data = json.loads(response.text)

        for course_json in data["data"]["allCourses"]:
            course = Course(**course_json)
            if course not in courses:
                courses.append(course)
    else:
        print(f"canvas API call failed with {response.status_code}")

    return courses


def get_course_details(id: str) -> CourseDetail | None:
    query = """query MyQuery {
  course(id: "{id}") {
    _id
    name
    term {
      _id
      name
      startAt
      endAt
    }
    sectionsConnection {
      nodes {
        _id
        name
      }
    }
    enrollmentsConnection {
      nodes {
        _id
        user {
          _id
          name
          avatarUrl
        }
        section {
          _id
          name
        }
      }
    }
  }
}
    """.replace(
        "{id}", id
    )
    response = get(query)

    if response.status_code != 200:
        return None

    course_json = json.loads(response.text)
    return CourseDetail(**course_json["data"]["course"])
