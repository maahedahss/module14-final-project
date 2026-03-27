# CodeCraftHub Learning Management System
A simple personalized learning platform for developers to track courses they want to learn.

## Features
Add courses with target completion dates
View all your courses
Update course information and status
Delete completed courses
JSON file-based storage (no database needed)
RESTful API design
Proper error handling
Installation
Clone or download the project

### Install Python dependencies:
bash
pip install -r requirements.txt
Run

### Running the Application
Start the Flask server:
bash
python app.py
Run
The API will be available at http://localhost:5000

## API Endpoints
### 1. Add a Course
POST /api/courses

Request body:
json
{
  "name": "Python Basics",
  "description": "Learn Python fundamentals",
  "target_date": "2025-12-31",
  "status": "Not Started"
}
### 2. Get All Courses
GET /api/courses

### 3. Get Specific Course
GET /api/courses/<id>

### 4. Update Course
PUT /api/courses/<id>
Request body (all fields optional):
json
{
  "status": "In Progress"
}
### 5. Delete Course
DELETE /api/courses/<id>

## Testing
Use the provided curl commands or import the Postman collection to test all endpoints.

## Troubleshooting
Problem: "Module not found: flask"
Solution: Run pip install -r requirements.txt

Problem: "Port already in use"
Solution: Stop other applications using port 5000 or change the port in app.py

## Project Structure

plaintext
codecrafthub/
├── app.py           # Main Flask application
├── courses.json     # Data storage (auto-created)
└── requirements.txt # Dependencies
