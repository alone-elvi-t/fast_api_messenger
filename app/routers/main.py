from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from app.utils.utils import templates

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def get_main_page(request: Request):
    """
    Главная страница приложения.
    """
    return templates.TemplateResponse("main.html", {"request": request})
