# 🎓 FastAPI Student Records Management

A beginner-friendly REST API project built using **Python and FastAPI** to manage student records stored in a JSON file.

## 🚀 Features

- Get a welcome message
- Retrieve all student records
- Search students by Student ID
- Filter students by course
- Sort students by marks, age, or name
- Paginate student records
- Handle errors using HTTPException
- Validate URL parameters using Path and Query

## 🛠️ Technologies Used

- Python
- FastAPI
- JSON
- Uvicorn
- VS Code
- Git & GitHub

## 📁 Project Structure

```text
FastApi/
│
├── main.py
├── student.json
├── requirements.txt
├── README.md
└── .gitignore
```

## ⚙️ Installation & Setup

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

### 2. Open the project folder

```bash
cd fastAPI-Students-record-management
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the virtual environment

Windows:

```bash
venv\Scripts\activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the application

```bash
uvicorn main:app --reload
```

## 📌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Welcome message |
| GET | `/hello` | Hello page |
| GET | `/students` | Get all students |
| GET | `/students/{student_id}` | Get student by ID |
| GET | `/filter?course=Physics` | Filter students |
| GET | `/sort?field=marks&order=asc` | Sort students |
| GET | `/paginate?page=1&limit=5` | Paginate students |

## 📖 API Documentation

After starting the server, open:

```text
http://127.0.0.1:8000/docs
```

Explore and test all API endpoints using Swagger UI.

## 🎯 Learning Objectives

This project helped me understand:

- REST API development
- FastAPI fundamentals
- Path and Query parameters
- JSON data handling
- Filtering, sorting and pagination
- HTTP error handling

## 👩‍💻 Author

**Nidhi Yadav**

BSc Computer Science Student | Aspiring AI Engineer

GitHub: https://github.com/nidhiyadavl2715-cell

---

⭐ If you find this project useful, feel free to explore it!