# STUDENT API

from flask import Flask, jsonify, request
from uuid import uuid4

app = Flask(__name__)

LOCALHOST:dict = {
    "host" : "127.0.0.1",
    "port" : 5000,
    "debug" : True      # only for localhost3
}

STUDENTS:list = [
    {'id': 'testcase_d', 'name': 'inevitable', 'gpa': 5.0}
]

# ----------------------

@app.route("/students", methods=["POST"])
def create_student():
    body = request.get_json(silent=True) or {}

    name = body.get("name")
    if not name:
        return jsonify({"Error": "Require student \"name\" which is missing."}), 400

    student = {
        "id": str(uuid4()),
        "name": name,
        "gpa": body.get("gpa", 0.0)
    }
    STUDENTS.append(student)

    return jsonify({
        "id": student["id"],
        "name": student["name"],
    }), 201 # CREATED


@app.route("/students", methods=["GET"])
def get_student_by_name():
    limit = int(request.args.get("limit", 5))
    q = request.args.get("q", "").strip().lower()

    students = [st for st in STUDENTS if q in st['name'].lower()]

    if not students:
        return jsonify({"Error": "not found"}), 404

    students = students[:limit]
    return jsonify({"students": students}), 200


@app.route("/students/<string:student_id>", methods=["GET"])
def get_student_by_id(student_id):
    students = [st for st in STUDENTS if st['id'] == student_id]

    if not students:
        return jsonify({"Error": "not found"}), 404

    if len(students) > 1:
        return jsonify({"Error": "internal error"}), 500
    
    return jsonify(students[0]), 200
    

@app.route("/students", methods=["DELETE", "PUT"])
def update_student():
    body = request.get_json(silent=True) or {}
    
    id = body.get("id", None)
    if not id:
        return jsonify({"Error": "ID is missing"}), 400
    
    student_indexes = [(i, st) for i, st in enumerate(STUDENTS) if st['id'] == id]

    if not student_indexes:
        return jsonify({"Error": "not found"}), 404
    elif len(student_indexes) > 1:
        return jsonify({"Error": "internal error"}), 500
    else:
        idx, target = student_indexes[0]


    match request.method:
        case "DELETE":
            STUDENTS.pop(idx)
            return "", 204  # Deleting success, without return body

        case "PUT":    
            new_gpa = body.get("gpa", None)
            if not new_gpa or not target.get("gpa", None) or new_gpa == target["gpa"]:
                return jsonify({"Error": "Nothing to update"}), 400

            target['gpa'] = new_gpa
            return jsonify(target), 200    
        
        case _:
            return jsonify({"Error": f"unsupported request method {request.method}"}), 400


# ---------------------

if __name__ == "__main__":
    app.run(
        **LOCALHOST
    )


# Server:
## python3 -m students

# Client:
## curl -i -X POST localhost:5000/students -H "Content-Type: application/json" -d '{"name": "Son", "age": 22}'
## curl -i -X POST localhost:5000/students -H "Content-Type: application/json" -d '{"name": "An", "age": 22, "gpa": 3.4}'
## curl -i 'localhost:5000/students?q="inev"&limit=1'
## curl -i -X PUT localhost:5000/students -H "Content-Type: application/json" -d '{"id": "testcase_d", "gpa": 3.6}'
## curl -i -X DELETE localhost:5000/students -H "Content-Type: application/json" -d '{"id": "testcase_d"}'
