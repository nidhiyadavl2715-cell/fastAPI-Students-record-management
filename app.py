# app.py -> STREAMLIT UI (Student Registry).
# This file never touches the database directly. It sends HTTP requests to the FastAPI backend (main.py):
#   Streamlit (app.py)  --requests-->  FastAPI (main.py)  -->  student.json
# Run: python -m streamlit run app.py     (FastAPI must already be running: python -m uvicorn main:app --reload)

import math                # used to calculate the total number of pages

import requests            # sends HTTP requests to FastAPI
import streamlit as st     # builds the UI

API_URL = "http://127.0.0.1:8000"   # address of the FastAPI server. Change it if you use another port.

# Basic page settings (this must be the FIRST Streamlit command)
st.set_page_config(page_title="Student Registry", page_icon="🎓", layout="wide")


def call_api(method: str, endpoint: str, **kwargs):
    """Send a request to FastAPI. Returns (True, data) or (False, error_message)."""
    try:
        # requests.request("GET", "http://127.0.0.1:8000/students", params=..., json=...)
        response = requests.request(method, f"{API_URL}{endpoint}", timeout=10, **kwargs)
    except requests.exceptions.ConnectionError:
        return False, "Could not connect to the FastAPI server. Start the backend first: python -m uvicorn main:app --reload"
    except requests.exceptions.Timeout:
        return False, "The server did not respond in time."

    if response.ok:                                   # status code 200-299 = success
        return True, response.json()                  # convert the JSON text into a Python object

    # If we get here, the API returned an error (400/404/422...). Extract its message.
    try:
        detail = response.json().get("detail", response.text)
    except ValueError:
        detail = response.text
    if isinstance(detail, list):                      # for 422 errors "detail" is a list, make it readable
        detail = "; ".join(f"{'.'.join(str(x) for x in d['loc'][1:])}: {d['msg']}" for d in detail)
    return False, detail


def grade_for(marks) -> str:
    """Work out the grade from marks (your API does not send a grade in /students, so the UI calculates it)."""
    marks = float(marks or 0)
    if marks >= 90:
        return "A"
    elif marks >= 80:
        return "B"
    elif marks >= 70:
        return "C"
    elif marks >= 60:
        return "D"
    return "F"


def to_list(data: dict) -> list:
    """Convert the API's dict {"s001": {...}, "s002": {...}} into a list [{"id": "s001", ...}]."""
    students = []
    for student_id, info in data.items():
        record = {key.lower(): value for key, value in info.items()}   # "Course" -> "course"
        record["id"] = student_id
        record["grade"] = grade_for(record.get("marks", 0))
        students.append(record)
    return students


def get_students(endpoint: str, **kwargs):
    """Fetch students from the API and return them as a list: (ok, list or error message)."""
    ok, result = call_api("GET", endpoint, **kwargs)
    return (True, to_list(result)) if ok else (False, result)


def flash(kind: str, message: str):
    """Save a message so it still shows after st.rerun()."""
    st.session_state["flash"] = (kind, message)


def cell(value) -> str:
    """Make the text for one table cell (a | or a new line would break a markdown table, so clean them)."""
    if value is None or value == "":
        return "-"
    return str(value).replace("|", "\\|").replace("\n", " ")


def show_table(students: list):
    """Show the list of students as a markdown table.
    pandas / st.dataframe are not used on purpose: pandas loads a numpy file that Windows
    (Smart App Control) may block on some machines."""
    if not students:
        st.info("No students found.")
        return
    columns = ["id", "name", "age", "course", "marks", "grade", "email"]
    header = "| " + " | ".join(c.capitalize() for c in columns) + " |"
    divider = "|" + " --- |" * len(columns)
    rows = ["| " + " | ".join(cell(s.get(c)) for c in columns) + " |" for s in students]
    st.markdown("\n".join([header, divider] + rows))


def clean_email(text: str):
    """Turn an empty email into None (email is optional in the API)."""
    text = text.strip()
    return text if text else None


# ---------------------------------------------------------------- Top of the page
st.title("🎓 Student Registry")
st.caption("Streamlit UI → FastAPI backend → student.json")

if "flash" in st.session_state:                       # show the message from the previous action (only once)
    kind, message = st.session_state.pop("flash")    # flash() saved (kind, message)
    st.success(message)

# Load all students once (used for the metrics and the edit/delete dropdowns)
ok, students = get_students("/students")
if not ok:
    st.error(students)                                # here "students" holds the error message
    st.stop()                                         # do not run the rest of the page

col1, col2, col3 = st.columns(3)                      # 3 equal columns
col1.metric("Total students", len(students))
average = sum(float(s.get("marks", 0) or 0) for s in students) / len(students) if students else 0
col2.metric("Average marks", f"{average:.1f}")
col3.metric("Courses", len({s.get("course") for s in students}))   # a set removes duplicates

tab_view, tab_add, tab_edit, tab_delete = st.tabs(["📋 View", "➕ Add", "✏️ Edit", "🗑️ Delete"])

# ---------------------------------------------------------------- Tab 1: View
with tab_view:
    mode = st.radio(
        "How do you want to view the students?",
        ["All students", "Filter by course", "Sort", "Paginate"],
        horizontal=True,
    )

    if mode == "All students":
        show_table(students)                          # the data was already loaded above

    elif mode == "Filter by course":
        course = st.text_input("Course name", placeholder="Physics")
        if course.strip():
            ok, result = get_students("/filter", params={"course": course})   # /filter?course=Physics
            if ok:
                show_table(result)
            else:
                st.error(result)

    elif mode == "Sort":
        left, right = st.columns(2)
        field = left.selectbox("Field", ["marks", "age", "name"])
        order = right.selectbox("Order", ["asc", "dec"])           # your API expects "dec" (not "desc")
        ok, result = get_students("/sort", params={"field": field, "order": order})
        if ok:
            show_table(result)
        else:
            st.error(result)

    else:                                             # Paginate
        if not students:
            st.info("There are no students yet.")     # your /paginate endpoint crashes on empty data
        else:
            left, right = st.columns(2)
            page = left.number_input("Page", min_value=1, value=1, step=1)
            limit = right.number_input("Students per page", min_value=1, max_value=100, value=5, step=1)
            ok, result = call_api("GET", "/paginate", params={"page": int(page), "limit": int(limit)})
            if ok:
                # result["students"] is a list and every item already contains its "id"
                page_students = to_list({s["id"]: {k: v for k, v in s.items() if k != "id"} for s in result["students"]})
                show_table(page_students)
                total_pages = max(1, math.ceil(result["total_students"] / result["limit"]))
                st.caption(f"Page {result['page']} / {total_pages}  |  Total: {result['total_students']}")
            else:
                st.error(result)

# ---------------------------------------------------------------- Tab 2: Add
with tab_add:
    version = st.session_state.get("add_version", 0)  # trick to reset the form after a successful add
    with st.form("add_form"):                         # a form only reruns the page when you press submit
        new_id = st.text_input("Student ID", placeholder="s004", key=f"add_id_{version}")
        new_name = st.text_input("Name", key=f"add_name_{version}")
        new_age = st.number_input("Age", min_value=0, max_value=100, value=18, step=1, key=f"add_age_{version}")
        new_course = st.text_input("Course", key=f"add_course_{version}")
        new_marks = st.number_input("Marks", min_value=0.0, max_value=100.0, value=0.0, step=0.5, key=f"add_marks_{version}")
        new_email = st.text_input("Email (optional)", key=f"add_email_{version}")
        submitted = st.form_submit_button("Add student")

    if submitted:
        payload = {                                   # this dict must match your Student model
            "id": new_id.strip(),
            "name": new_name.strip(),
            "age": int(new_age),
            "course": new_course.strip(),
            "marks": float(new_marks),
            "email": clean_email(new_email),
        }
        ok, result = call_api("POST", "/create", json=payload)
        if ok:
            st.session_state["add_version"] = version + 1   # the widget keys change -> the form becomes empty
            flash("success", result["message"])
            st.rerun()                                # rerun the page so the table and metrics update
        else:
            st.error(result)                          # on error the data the user typed is kept

# ---------------------------------------------------------------- Tab 3: Edit
with tab_edit:
    if not students:
        st.info("Add a student first, then you can edit it.")
    else:
        edit_id = st.selectbox("Which student do you want to edit?", [s["id"] for s in students], key="edit_select")
        current = next(s for s in students if s["id"] == edit_id)   # data of the selected student

        with st.form("edit_form"):
            # the key contains edit_id, so the fields refill with the new student's data when you switch student
            e_name = st.text_input("Name", value=current.get("name", ""), key=f"edit_name_{edit_id}")
            e_age = st.number_input("Age", min_value=0, max_value=100, value=int(current.get("age", 0)), step=1, key=f"edit_age_{edit_id}")
            e_course = st.text_input("Course", value=current.get("course", ""), key=f"edit_course_{edit_id}")
            e_marks = st.number_input("Marks", min_value=0.0, max_value=100.0, value=float(current.get("marks", 0.0)), step=0.5, key=f"edit_marks_{edit_id}")
            e_email = st.text_input("Email (optional)", value=current.get("email") or "", key=f"edit_email_{edit_id}")
            update_clicked = st.form_submit_button("Update student")

        if update_clicked:
            payload = {
                "name": e_name.strip(),
                "age": int(e_age),
                "course": e_course.strip(),
                "marks": float(e_marks),
                "email": clean_email(e_email),
            }
            ok, result = call_api("PUT", f"/update/{edit_id}", json=payload)
            if ok:
                flash("success", result["message"])
                st.rerun()
            else:
                st.error(result)

# ---------------------------------------------------------------- Tab 4: Delete
with tab_delete:
    if not students:
        st.info("There are no students to delete.")
    else:
        del_id = st.selectbox("Which student do you want to delete?", [s["id"] for s in students], key="delete_select")
        sure = st.checkbox("Yes, I want to delete this student")        # prevents accidental deletes
        if st.button("Delete student", type="primary", disabled=not sure):   # disabled until the box is ticked
            ok, result = call_api("DELETE", f"/delete/{del_id}")
            if ok:
                flash("success", result["message"])
                st.rerun()
            else:
                st.error(result)