from turtle import update

from fastapi import FastAPI,HTTPException,Path,Query
import json
import os

from pydantic import BaseModel, EmailStr, Field, computed_field, field_validator
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
def save_data(data):
    with open("student.json", "w") as file:
        return json.dump(data, file, indent=4)
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
                    limit:int=Query(...,description="number of students per page")
):
    data=load_data()
    student=[]
    for student_id,info in data.items():
        info['id']=student_id
        student.append({"id":student_id,**info})
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
class Student(BaseModel):
    id:str=Field(...,examples=["s001"])
    name:str=Field(...,min_length=1,max_length=50,examples=["John Doe"])
    age:int=Field(...,ge=0,le=100,examples=[20])
    course:str=Field(...,max_length=50,examples=["Physics"])
    marks:float=Field(...,ge=0.0,le=100.0,examples=[85.5])
    email:EmailStr | None=None
    @field_validator("name")
    @classmethod
    def check_name(cls, value):
        if not value.replace(" ", "").isalpha():
            raise ValueError("Name must contain only alphabetic characters and spaces")
        return value.title()
    @computed_field
    @property
    def grade(self) -> str:
        if self.marks >= 90:
            return "A"
        elif self.marks >= 80:
            return "B"
        elif self.marks >= 70:
            return "C"
        elif self.marks >= 60:
            return "D"
        else:
            return "F"
s=Student(id="s001",
          name="John Doe",
          age=20,
          course="Physics",
          marks=85.5,
          email="john.doe@example.com")

print(s.id)
print(s.name)
print(s.age)
print(s.course)
print(s.marks)
print(s.email)
print(s.grade)
data =s.model_dump()
print(data)
import json
with open("student.json", "r") as file:
    raw_data = json.load(file)
for student_id, info in raw_data.items():
    student = Student(id=student_id, **info)
    print(student.id)
    print(student.name)
    print(student.age)
    print(student.course)
    print(student.marks)
    print(student.email)
    print(student.grade)
    data = student.model_dump()
    print(data)
@app.post("/create",status_code=201)
def create_student(student: Student):
    data = load_data()
    if student.id in data:
        raise HTTPException(status_code=400, detail="Student with this ID already exists")
    data[student.id] = student.model_dump(exclude={"id","grade"})
    save_data(data)
    return {"message": "Student created successfully", "student": student}
class UpdateStudent(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=50, examples=["John Doe"])
    age: int | None = Field(None, ge=0, le=100, examples=[20])
    course: str | None = Field(None, max_length=50, examples=["Physics"])
    marks: float | None = Field(None, ge=0.0, le=100.0, examples=[85.5])
    email: EmailStr | None = None
@app.put("/update/{student_id}")
def update_student(student_id: str, student: UpdateStudent):
    data = load_data()
    if student_id not in data:
        raise HTTPException(status_code=404, detail="Student not found")
    updated_data = student.model_dump(exclude_unset=True)
    data[student_id].update(updated_data)
    save_data(data)
    return {"message": "Student updated successfully", "student": data[student_id]}
    existing =data[student_id]
    update=update_student.model_dump(exclude_unset=True)
    for key, value in update.items(): 
        existing[key]=value
    student = Student(id=student_id, **existing)
    data[student_id] = student.model_dump(exclude={"id","grade"})
    save_data(data)
    return{"message": "Student updated successfully","student": student}
@app.delete('delete/{student_id}')
def delete_student(student_id:str=Path(...,description="the id of the student ",examples=["s001"])):
    data=load_data()
    if student_id not in data:
        raise HTTPException(status_code=404,detail=f"student with id'{student_id}'not found")
    del data[student_id]
    save_data(data)
    return{"message":f"student'{student_id}'deleted successfully"}
    

