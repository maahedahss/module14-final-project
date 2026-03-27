# app.py
# Simple Flask REST API for CodeCraftHub
# - CRUD operations on "courses" stored in a JSON file (courses.json)
# - Endpoints:
#     POST   /api/courses            -> create a new course
#     GET    /api/courses            -> get all courses
#     GET    /api/courses/<id>       -> get a specific course by id
#     PUT    /api/courses            -> update a course (requires id in body)
#     DELETE /api/courses            -> delete a course (requires id in body)
#
# Notes:
# - Each course has: id, name, description, target_date (YYYY-MM-DD),
#   status (Not Started, In Progress, Completed), created_at (timestamp)
# - The app creates courses.json automatically if it doesn't exist
# - Includes basic error handling and lots of comments for beginners

from flask import Flask, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

DATA_FILE = "courses.json"
ALLOWED_STATUSES = {"Not Started", "In Progress", "Completed"}


def ensure_data_file():
    """
    Ensure the JSON data file exists.
    If it doesn't exist, create it and initialize with an empty list.
    """
    if not os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "w") as f:
                json.dump([], f, indent=2)
        except Exception as e:
            # If we cannot create the file, print a warning for debugging
            print(f"Error creating data file {DATA_FILE}: {e}")


def load_courses():
    """
    Load and return the list of courses from the JSON file.
    If the file is missing or empty, return an empty list.
    Handles JSON decode errors gracefully by resetting to an empty list.
    """
    try:
        with open(DATA_FILE, "r") as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    except FileNotFoundError:
        # Should not happen if we call ensure_data_file() at startup
        ensure_data_file()
        return []
    except json.JSONDecodeError:
        # If JSON is corrupted, reset to empty list (safe recovery for learning)
        return []
    except Exception as e:
        # Other file I/O errors
        print(f"Error reading data file: {e}")
        raise


def save_courses(courses):
    """
    Persist the list of courses to the JSON file.
    """
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(courses, f, indent=2)
    except Exception as e:
        print(f"Error writing to data file: {e}")
        raise


def is_valid_date(date_str):
    """
    Validate that date_str is in YYYY-MM-DD format.
    """
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except Exception:
        return False


def is_valid_status(status):
    """
    Check if the status is one of the allowed values.
    """
    return status in ALLOWED_STATUSES


@app.route("/api/courses", methods=["POST"])
def create_course():
    """
    Create a new course.
    Expected JSON body:
    {
        "name": "Course name",
        "description": "Course description",
        "target_date": "YYYY-MM-DD",
        "status": "Not Started" | "In Progress" | "Completed"
    }
    """
    try:
        data = request.get_json(force=True)
    except Exception:
        data = None

    if not data:
        return jsonify({"error": "Request must be JSON with required fields."}), 400

    # Validate required fields
    required = ["name", "description", "target_date", "status"]
    missing = [field for field in required if not data.get(field)]
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    name = data.get("name").strip()
    description = data.get("description").strip()
    target_date = data.get("target_date").strip()
    status = data.get("status").strip()

    # More field validation
    if not is_valid_date(target_date):
        return jsonify({"error": "target_date must be in YYYY-MM-DD format."}), 400
    if not is_valid_status(status):
        return jsonify({"error": f"status must be one of {sorted(list(ALLOWED_STATUSES))}."}), 400
    if not name:
        return jsonify({"error": "name cannot be empty."}), 400
    if not description:
        return jsonify({"error": "description cannot be empty."}), 400

    # Load existing courses
    try:
        courses = load_courses()
    except Exception:
        return jsonify({"error": "Failed to read data file."}), 500

    # Compute new ID (start from 1)
    max_id = max([c.get("id", 0) for c in courses], default=0)
    new_id = max_id + 1

    created_at = datetime.utcnow().isoformat()

    new_course = {
        "id": new_id,
        "name": name,
        "description": description,
        "target_date": target_date,
        "status": status,
        "created_at": created_at
    }

    courses.append(new_course)

    try:
        save_courses(courses)
    except Exception:
        return jsonify({"error": "Failed to write data to file."}), 500

    return jsonify(new_course), 201


@app.route("/api/courses", methods=["GET"])
def get_all_courses():
    """
    Retrieve all courses.
    """
    try:
        courses = load_courses()
    except Exception:
        return jsonify({"error": "Failed to read data file."}), 500

    return jsonify(courses), 200


# Supporting endpoint to fetch a specific course by id
@app.route("/api/courses/<int:course_id>", methods=["GET"])
def get_course(course_id):
    """
    Retrieve a specific course by its id.
    """
    try:
        courses = load_courses()
    except Exception:
        return jsonify({"error": "Failed to read data file."}), 500

    course = next((c for c in courses if c.get("id") == course_id), None)
    if not course:
        return jsonify({"error": "Course not found."}), 404

    return jsonify(course), 200


@app.route("/api/courses", methods=["PUT"])
def update_course():
    """
    Update a course (full replacement).
    Required JSON body:
    {
        "id": <int>,
        "name": "...",
        "description": "...",
        "target_date": "YYYY-MM-DD",
        "status": "Not Started" | "In Progress" | "Completed"
    }
    """
    try:
        data = request.get_json(force=True)
    except Exception:
        data = None

    if not data:
        return jsonify({"error": "Missing required data"}), 400
    if "id" not in data:
        return jsonify({"error": "Missing required field: id"}), 400

    course_id = data.get("id")
    # Validate required fields for full update
    required = ["name", "description", "target_date", "status"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    name = data.get("name").strip()
    description = data.get("description").strip()
    target_date = data.get("target_date").strip()
    status = data.get("status").strip()

    if not is_valid_date(target_date):
        return jsonify({"error": "target_date must be in YYYY-MM-DD format."}), 400
    if not is_valid_status(status):
        return jsonify({"error": f"status must be one of {sorted(list(ALLOWED_STATUSES))}."}), 400
    if not name:
        return jsonify({"error": "name cannot be empty."}), 400
    if not description:
        return jsonify({"error": "description cannot be empty."}), 400

    try:
        courses = load_courses()
    except Exception:
        return jsonify({"error": "Failed to read data file."}), 500

    # Find existing course
    index = next((i for i, c in enumerate(courses) if c.get("id") == course_id), None)
    if index is None:
        return jsonify({"error": "Course not found."}), 404

    # Preserve created_at; update other fields
    existing_created_at = courses[index].get("created_at", datetime.utcnow().isoformat())

    updated_course = {
        "id": course_id,
        "name": name,
        "description": description,
        "target_date": target_date,
        "status": status,
        "created_at": existing_created_at
    }

    courses[index] = updated_course

    try:
        save_courses(courses)
    except Exception:
        return jsonify({"error": "Failed to write data to file."}), 500

    return jsonify(updated_course), 200


@app.route("/api/courses", methods=["DELETE"])
def delete_course():
    """
    Delete a course by id.
    Expected JSON body:
    {
        "id": <int>
    }
    """
    try:
        data = request.get_json(force=True)
    except Exception:
        data = None

    if not data or "id" not in data:
        return jsonify({"error": "Missing required field: id"}), 400

    course_id = data.get("id")

    try:
        courses = load_courses()
    except Exception:
        return jsonify({"error": "Failed to read data file."}), 500

    index = next((i for i, c in enumerate(courses) if c.get("id") == course_id), None)
    if index is None:
        return jsonify({"error": "Course not found."}), 404

    # Remove the course
    deleted_course = courses.pop(index)

    try:
        save_courses(courses)
    except Exception:
        return jsonify({"error": "Failed to write data to file."}), 500

    return jsonify({"message": "Course deleted", "id": course_id}), 200


if __name__ == "__main__":
    # Ensure the data file exists before starting the server
    ensure_data_file()
    # Run the Flask development server
    app.run(host="0.0.0.0", port=5000, debug=True)

