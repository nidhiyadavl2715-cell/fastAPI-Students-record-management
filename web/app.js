// app.js -> logic of the HTML page: talks to FastAPI and drives the table and the form.

const API = "http://127.0.0.1:8000";   // address of the FastAPI server (change it if you use another port)

// Grab the HTML elements once (no need to look them up again and again)
const form = document.getElementById("student-form");
const formTitle = document.getElementById("form-title");
const submitBtn = document.getElementById("submit-btn");
const cancelBtn = document.getElementById("cancel-btn");
const tbody = document.getElementById("students-body");
const messageBox = document.getElementById("message");
const fields = {
  id: document.getElementById("f-id"),
  name: document.getElementById("f-name"),
  age: document.getElementById("f-age"),
  course: document.getElementById("f-course"),
  marks: document.getElementById("f-marks"),
  email: document.getElementById("f-email"),
};

let editingId = null;   // null = add mode, otherwise the id of the student being edited

// ---------------------------------------------------------------- API helper
// Every request goes through here. Returns the JSON data on success, throws an Error on failure.
async function api(method, path, body) {
  const options = { method, headers: {} };
  if (body !== undefined) {
    options.headers["Content-Type"] = "application/json";   // tell the server the body is JSON
    options.body = JSON.stringify(body);                     // JS object -> JSON text
  }

  let response;
  try {
    response = await fetch(API + path, options);             // the real request is sent here
  } catch (err) {
    throw new Error("Could not connect to the FastAPI server. Start it first: python -m uvicorn main:app --reload");
  }

  const data = await response.json().catch(() => null);      // read the response body (null if there is none)
  if (!response.ok) {                                        // 400 / 404 / 422 ...
    let detail = data && data.detail ? data.detail : "Something went wrong";
    if (Array.isArray(detail)) {                             // for 422 errors "detail" is a list
      detail = detail.map((d) => `${d.loc.slice(1).join(".")}: ${d.msg}`).join("; ");
    }
    throw new Error(detail);
  }
  return data;
}

// ---------------------------------------------------------------- Data helpers
// Your API sends students as a dict ({"s001": {...}}) and does not send a grade.
// The helpers below turn that into a list and calculate the grade, so the table is easy to build.
// NOTE: ids should be text like "s001". Purely numeric ids (1, 2, 3) get re-ordered automatically in a JS object.
function gradeFor(marks) {
  const m = Number(marks) || 0;
  if (m >= 90) return "A";
  if (m >= 80) return "B";
  if (m >= 70) return "C";
  if (m >= 60) return "D";
  return "F";
}

function normalize(info) {
  const out = {};
  for (const [key, value] of Object.entries(info)) out[key.toLowerCase()] = value;   // "Course" -> "course"
  return out;
}

function toList(obj) {
  return Object.entries(obj).map(([id, info]) => {
    const student = normalize(info);
    student.id = id;
    student.grade = gradeFor(student.marks);
    return student;
  });
}

// ---------------------------------------------------------------- UI helpers
function showMessage(text, type) {
  messageBox.textContent = text;                 // textContent is safe (it cannot inject HTML)
  messageBox.className = "message " + type;      // "ok" (green) or "err" (red)
  messageBox.hidden = false;
  setTimeout(() => (messageBox.hidden = true), 4000);   // hide it after 4 seconds
}

function escapeHtml(value) {
  // Make user text safe before putting it into the table (protects against XSS)
  return String(value ?? "").replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  }[c]));
}

function renderTable(students) {
  if (students.length === 0) {
    tbody.innerHTML = '<tr><td colspan="8" class="empty">No students found.</td></tr>';
    return;
  }
  tbody.innerHTML = students.map((s) => `
    <tr>
      <td>${escapeHtml(s.id)}</td>
      <td>${escapeHtml(s.name)}</td>
      <td>${escapeHtml(s.age)}</td>
      <td>${escapeHtml(s.course)}</td>
      <td>${escapeHtml(s.marks)}</td>
      <td><span class="badge">${escapeHtml(s.grade)}</span></td>
      <td>${escapeHtml(s.email || "-")}</td>
      <td class="row-actions">
        <button class="small" data-action="edit" data-id="${escapeHtml(s.id)}">Edit</button>
        <button class="small danger" data-action="delete" data-id="${escapeHtml(s.id)}">Delete</button>
      </td>
    </tr>`).join("");
}

function renderStats(students) {
  const total = students.length;
  const sum = students.reduce((acc, s) => acc + (Number(s.marks) || 0), 0);
  document.getElementById("stat-total").textContent = total;
  document.getElementById("stat-avg").textContent = total ? (sum / total).toFixed(1) : "0";
  document.getElementById("stat-courses").textContent = new Set(students.map((s) => s.course)).size;
}

// ---------------------------------------------------------------- Load data
// The stats always use ALL students; the table follows the current filter / sort.
async function loadStudents() {
  try {
    const all = toList(await api("GET", "/students"));   // dict -> list
    renderStats(all);

    const course = document.getElementById("filter-course").value.trim();
    const sortField = document.getElementById("sort-field").value;
    const sortOrder = document.getElementById("sort-order").value;

    let shown = all;
    if (sortField) {
      shown = toList(await api("GET", `/sort?field=${sortField}&order=${sortOrder}`));   // /sort endpoint
    }
    if (course) {
      // encodeURIComponent makes spaces / special characters safe inside a URL
      const filtered = toList(await api("GET", `/filter?course=${encodeURIComponent(course)}`));   // /filter endpoint
      const ids = new Set(filtered.map((s) => s.id));
      shown = shown.filter((s) => ids.has(s.id));      // so filter and sort work together
    }
    renderTable(shown);
  } catch (err) {
    tbody.innerHTML = "";
    showMessage(err.message, "err");
  }
}

// ---------------------------------------------------------------- Form: add / edit
function resetForm() {
  form.reset();                         // clear all fields
  fields.age.value = 18;
  fields.marks.value = 0;
  fields.id.disabled = false;           // in add mode the id can be typed
  editingId = null;
  formTitle.textContent = "Add a new student";
  submitBtn.textContent = "Add student";
  cancelBtn.hidden = true;
}

function startEdit(student) {
  editingId = student.id;
  fields.id.value = student.id;
  fields.id.disabled = true;            // the id cannot be changed
  fields.name.value = student.name;
  fields.age.value = student.age;
  fields.course.value = student.course;
  fields.marks.value = student.marks;
  fields.email.value = student.email || "";
  formTitle.textContent = `Edit: ${student.id}`;
  submitBtn.textContent = "Update student";
  cancelBtn.hidden = false;
  form.scrollIntoView({ behavior: "smooth" });
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();               // do not reload the page
  const payload = {
    name: fields.name.value.trim(),
    age: Number(fields.age.value),
    course: fields.course.value.trim(),
    marks: Number(fields.marks.value),
    email: fields.email.value.trim() || null,   // empty email -> null
  };

  try {
    let result;
    if (editingId) {
      result = await api("PUT", `/update/${encodeURIComponent(editingId)}`, payload);          // update
    } else {
      result = await api("POST", "/create", { id: fields.id.value.trim(), ...payload });       // create
    }
    showMessage(result.message, "ok");
    resetForm();
    await loadStudents();               // refresh the table
  } catch (err) {
    showMessage(err.message, "err");    // on error the form keeps what the user typed
  }
});

cancelBtn.addEventListener("click", resetForm);

// ---------------------------------------------------------------- Table buttons (Edit / Delete)
// Rows are rebuilt again and again, so the listener is attached once to tbody (event delegation)
tbody.addEventListener("click", async (event) => {
  const button = event.target.closest("button[data-action]");
  if (!button) return;
  const id = button.dataset.id;

  try {
    if (button.dataset.action === "edit") {
      const info = await api("GET", `/students/${encodeURIComponent(id)}`);   // only the data comes back, not the id
      startEdit({ id, ...normalize(info) });
    } else if (button.dataset.action === "delete") {
      if (!confirm(`Delete student '${id}'?`)) return;                       // prevents accidental deletes
      const result = await api("DELETE", `/delete/${encodeURIComponent(id)}`);
      showMessage(result.message, "ok");
      if (editingId === id) resetForm();
      await loadStudents();
    }
  } catch (err) {
    showMessage(err.message, "err");
  }
});

// ---------------------------------------------------------------- Search / sort controls
document.getElementById("filter-btn").addEventListener("click", loadStudents);
document.getElementById("filter-course").addEventListener("keydown", (e) => {
  if (e.key === "Enter") loadStudents();
});
document.getElementById("sort-field").addEventListener("change", loadStudents);
document.getElementById("sort-order").addEventListener("change", loadStudents);
document.getElementById("reset-btn").addEventListener("click", () => {
  document.getElementById("filter-course").value = "";
  document.getElementById("sort-field").value = "";
  document.getElementById("sort-order").value = "asc";
  loadStudents();
});

// Load the students as soon as the page opens
loadStudents();