from fastapi import FastAPI,HTTPException,Path,Query
import json
import os
app = FastAPI()
@app.get("/")
def greet():
    return {"message": "Hello, World!"}
@app.get("/hello")
def hello():
    return{"this is hello page"}

def load_data():
    with open("student.json", "r") as file:
        return json.load(file)
@app.get("/students")
def students():
    return load_data()  
@app.get("/students/{student_id}")
def get_student(student_id: str=Path(...,description="the id of student of the student ",
    example=["s001"])):
    data = load_data()
    if student_id not in data:
        raise HTTPException(status_code=404, detail="Student not found")
    return data[student_id]

@app.get("/filter")
def filter_students(
    course: str = Query(
        None,
        description="Show only students of a particular course",
        example="Physics"
    )
):
    data = load_data()

    if course is None:
        return data

    filtered = {}

    for student_id, info in data.items():
        student_course = info.get("Course") or info.get("course")

        if student_course and student_course.lower() == course.lower():
            filtered[student_id] = info

    return filtered
SORT_FIELDS=["marks","age","name"]
SORT_ORDER=["asc","dec"]
@app.get("/sort")
def sort_students(
    field: str = Query(..., description="Field to sort by", example="marks"),
    order: str = Query(..., description="Sort order (asc or dec)", example="asc")
):
    if field not in SORT_FIELDS:
        raise HTTPException(status_code=400, detail=f"Invalid field. Must be one of {SORT_FIELDS}")
    if order not in SORT_ORDER:
        raise HTTPException(status_code=400, detail=f"Invalid order. Must be one of {SORT_ORDER}")

    data = load_data()
    sorted_students = sorted(data.items(), key=lambda x: x[1].get(field), reverse=(order == "dec"))
    return dict(sorted_students)
@app.get("/paginate")
def paginate_student(page:int=Query(...,description="which page you want to see(start from 1)"),
                    limit:int=Query(...,description="number of students per page")):
    data=load_data()
    student=[]
    for student_id,info in data.items():
        info['id']=student_id
        student.append(info)
        start=(page - 1) * limit
        end=start + limit
        page_student=student[start:end]
        total_students=len(student)
    return{
        "page":page,
        "limit":limit,
        "total_students":total_students,
        "students":page_student
    }
