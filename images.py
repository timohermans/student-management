import json
import requests
import urllib.request

query = """query MyQuery {
  course(id: "12424") {
    name
    sectionsConnection {
      nodes {
        id
        name
        userCount
      }
    }
    enrollmentsConnection {
      nodes {
        id
        user {
          name
          avatarUrl
        }
        section {
          name
          id
        }
      }
    }
  }
}"""
api_url = "https://fhict.test.instructure.com/api/graphql"
token = "Bearer cwFQicKHBN3DQ7U7lecrz3R2rV3TVeOv4wYjAsGnXKhy308FpSqhezxO5qWaOAYY"
r = requests.post(
    api_url,
    json={"operationName": "MyQuery", "query": query, "variables": None},
    headers={"Authorization": token},
)

data = json.load(open("result.json").readlines())

section = "CB-S01"
sections = data["data"]["course"]["sectionsConnection"]["nodes"]

section_id_result = [s["id"] for s in sections if s["name"] == section]

if len(section_id_result) == 0:
    raise f"section {section} not found"

section_id = section_id_result[0]

students_all = data["data"]["course"]["enrollmentsConnection"]["nodes"]

students_of_section = [s for s in students_all if s["section"]["id"] == section_id]

for student in students_of_section:
    student_name = student["user"]["name"]
    avatar_url = student["user"]["avatarUrl"]
    if avatar_url is None:
        continue
    urllib.request.urlretrieve(avatar_url, f"tests/{student_name}.jpg")
