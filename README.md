
# Student Registry (FastAPI + Streamlit + HTML)

A FastAPI backend, a `student.json` database, and two UIs: Streamlit and plain HTML/CSS/JS.

## Files
| File | Purpose |
|------|---------|
| `main.py` | FastAPI backend (routes, validation, JSON read/write) |
| `app.py` | Streamlit UI |
| `student.json` | Database (JSON file) |
| `web/index.html`, `web/style.css`, `web/app.js` | HTML UI |
| `.gitignore` | Files Git should not track |

## Setup
```bash
python -m venv venv
venv\Scripts\activate             # Mac/Linux: source venv/bin/activate
pip install fastapi uvicorn "pydantic[email]" streamlit requests
```

## Run (from the project folder, in 2 separate terminals)
```bash
python -m uvicorn main:app --reload   # Terminal 1 -> API docs: http://127.0.0.1:8000/docs
python -m streamlit run app.py        # Terminal 2 -> Streamlit UI: http://localhost:8501
```
The HTML UI is served by FastAPI itself: http://127.0.0.1:8000/web/

Both UIs only work while the FastAPI server (Terminal 1) is running.

## API endpoints
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/students` | All students |
| GET | `/students/{id}` | One student |
| GET | `/filter?course=Physics` | Filter by course |
| GET | `/sort?field=marks&order=dec` | Sort (order: asc or dec) |
| GET | `/paginate?page=1&limit=5` | Pagination |
| POST | `/create` | Create a student |
| PUT | `/update/{id}` | Update a student |
| DELETE | `/delete/{id}` | Delete a student |