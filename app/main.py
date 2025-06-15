from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from app.database import get_candidates, add_candidate

from app.database import add_candidate, get_candidates, update_stage, read_template, update_template
from app.emailer import send_next_email

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

@app.get("/")
def dashboard(request: Request):
    candidates = get_candidates()
    return templates.TemplateResponse("dashboard.html", {"request": request, "candidates": candidates})

@app.post("/add_candidate")
def create_candidate(name: str = Form(...), email: str = Form(...)):
    add_candidate(name, email)
    return RedirectResponse("/", status_code=303)

@app.post("/send/{candidate_id}")
def send_email_route(candidate_id: int):
    candidates = get_candidates()
    candidate = next((c for c in candidates if c[0] == candidate_id), None)
    if candidate:
        cid, name, email, stage = candidate
        if send_next_email(cid, name, email, stage):
            update_stage(cid, stage + 1)
    return RedirectResponse("/", status_code=303)

@app.get("/template/{stage}")
def edit_template(request: Request, stage: int):
    content = read_template(stage)
    return templates.TemplateResponse("edit_template.html", {"request": request, "stage": stage, "content": content})

@app.post("/template/{stage}")
def save_template(stage: int, content: str = Form(...)):
    update_template(stage, content)
    return RedirectResponse("/", status_code=303)