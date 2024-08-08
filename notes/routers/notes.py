import sys
sys.path.append("..")

from starlette import status
from starlette.responses import RedirectResponse
from fastapi import Depends, APIRouter, Request, Form
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from .auth import get_current_user
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


router = APIRouter(
    prefix="/notes",
    tags=["notes"],
    responses={404: {"description": "Not found"}}
)

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@router.get("/", response_class=HTMLResponse)
async def read_all_by_user(request: Request, db: Session = Depends(get_db)):

    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    notes = db.query(models.Notes).filter(models.Notes.owner_id == user.get("id")).all()

    return templates.TemplateResponse("home.html", {"request": request, "notes": notes, "user": user})


@router.get("/add-note", response_class=HTMLResponse)
async def add_new_note(request: Request):

    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("add-note.html", {"request": request, "user": user})


@router.post("/add-note", response_class=HTMLResponse)
async def create_note(request: Request, title: str = Form(...), description: str = Form(...),
                      priority: int = Form(...), db: Session = Depends(get_db)):

    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    note_model = models.Notes()
    note_model.title = title
    note_model.description = description
    note_model.priority = priority
    note_model.complete = False
    note_model.owner_id = user.get("id")

    db.add(note_model)
    db.commit()

    return RedirectResponse(url="/notes", status_code=status.HTTP_302_FOUND)


@router.get("/edit-note/{note_id}", response_class=HTMLResponse)
async def edit_note(request: Request, note_id: int, db: Session = Depends(get_db)):

    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    note = db.query(models.Notes).filter(models.Notes.id == note_id).first()

    return templates.TemplateResponse("edit-note.html", {"request": request, "note": note, "user": user})


@router.post("/edit-note/{note_id}", response_class=HTMLResponse)
async def edit_note_commit(request: Request, note_id: int, title: str = Form(...),
                           description: str = Form(...), priority: int = Form(...),
                           db: Session = Depends(get_db)):

    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    note_model = db.query(models.Notes).filter(models.Notes.id == note_id).first()

    note_model.title = title
    note_model.description = description
    note_model.priority = priority

    db.add(note_model)
    db.commit()

    return RedirectResponse(url="/notes", status_code=status.HTTP_302_FOUND)


@router.get("/delete/{note_id}")
async def delete_note(request: Request, note_id: int, db: Session = Depends(get_db)):

    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    note_model = db.query(models.Notes).filter(models.Notes.id == note_id)\
        .filter(models.Notes.owner_id == user.get("id")).first()

    if note_model is None:
        return RedirectResponse(url="/notes", status_code=status.HTTP_404_NOT_FOUND)

    db.query(models.Notes).filter(models.Notes.id == note_id).delete()

    db.commit()

    return RedirectResponse(url="/notes", status_code=status.HTTP_302_FOUND)


@router.get("/complete/{note_id}", response_class=HTMLResponse)
async def complete_note(request: Request, note_id: int, db: Session = Depends(get_db)):

    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    note = db.query(models.Notes).filter(models.Notes.id == note_id).first()

    note.complete = not note.complete

    db.add(note)
    db.commit()

    return RedirectResponse(url="/notes", status_code=status.HTTP_302_FOUND)
