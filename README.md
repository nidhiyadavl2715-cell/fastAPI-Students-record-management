# 🎓 Student Registry Management System

A Student Registry Management System built using **Python, FastAPI, Streamlit, and HTML/CSS/JavaScript**.

This project provides two user interfaces (Streamlit and HTML) connected to a FastAPI backend with JSON-based data storage.

## 🚀 Features

- View all student records
- Add new students
- Update existing student details
- Delete student records
- Filter students by course
- Sort students by marks
- Pagination support
- Student statistics dashboard
- REST API integration
- JSON-based data storage

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core programming |
| FastAPI | Backend and REST APIs |
| Streamlit | Interactive dashboard |
| HTML | Web structure |
| CSS | Web styling |
| JavaScript | Frontend functionality |
| JSON | Data storage |
| Pydantic | Data validation |

## 📂 Project Structure

```text
FastApi/
│
├── main.py
├── app.py
├── student.json
├── requirements.txt
│
├── web/
│   ├── index.html
│   ├── style.css
│   └── app.js
│
├── .gitignore
└── README.md
```

## ⚙️ Installation

**1. Clone the repository**

```bash
git clone YOUR_REPOSITORY_URL
cd FastApi
```

**2. Create a virtual environment**

```bash
python -m venv venv
```

**3. Activate the environment**

Windows:

```bash
venv\Scripts\activate
```

Mac/Linux:

```bash
source venv/bin/activate
```

**4. Install dependencies**

```bash
pip install fastapi uvicorn "pydantic[email]" streamlit requests
```

## ▶️ Run the Project

Open two separate terminals.

**Terminal 1 – Start FastAPI Backend**

```bash
python -m uvicorn main:app --reload
```

API Documentation:

http://127.0.0.1:8000/docs

**Terminal 2 – Start Streamlit Frontend**

```bash
python -m streamlit run app.py
```

Streamlit Dashboard:

http://localhost:8501

**HTML Frontend**

http://127.0.0.1:8000/web/

Note: Both frontends require the FastAPI backend to be running.

## 🔗 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/students` | Get all students |
| GET | `/students/{id}` | Get student by ID |
| GET | `/filter?course=Physics` | Filter by course |
| GET | `/sort?field=marks&order=dec` | Sort students |
| GET | `/paginate?page=1&limit=5` | Paginate records |
| POST | `/create` | Create a student |
| PUT | `/update/{id}` | Update student |
| DELETE | `/delete/{id}` | Delete student |

## 🎯 Learning Outcomes

- Building REST APIs with FastAPI
- Implementing CRUD operations
- Integrating frontend and backend
- Working with JSON data
- Data validation using Pydantic
- Building interactive dashboards with Streamlit

## 👩‍💻 Developer

**Nidhi Yadav**

Aspiring AI Engineer | Python Developer

---

⭐ If you find this project useful, feel free to explore the repository!


## 📸 Project Screenshots

### Student Dashboard
![Dashboard](screenshots/dashboard.png)
