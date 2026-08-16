import os
import sys
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware

BACKEND_DIR = os.path.abspath(os.path.dirname(__file__))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from routes.routes import router
from middleware.timer import timer_middleware
from db.migrations import ensure_schema
from db.session import SessionLocal, engine
from models import AuthSession
from security import session_has_expired

ROOT_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = ROOT_DIR / "frontend"

app = FastAPI()
ensure_schema(engine)
app.middleware("http")(timer_middleware)
app.include_router(router)

app.mount("/assets", StaticFiles(directory=FRONTEND_DIR / "assets"), name="assets")
app.mount("/Doc", StaticFiles(directory=FRONTEND_DIR / "Doc"), name="doc")

@app.get("/")
async def serve_index():
    return FileResponse(FRONTEND_DIR / "index.html")

@app.get("/{page_name}.html")
async def serve_html_page(page_name: str, request: Request):
    if page_name == "header":
        return await serve_header(request)
    page_path = FRONTEND_DIR / f"{page_name}.html"
    if page_path.exists():
        return FileResponse(page_path)
    raise HTTPException(status_code=404, detail="Page not found")

@app.get("/header.html")
async def serve_header(request: Request):
    """Render the shared header with the correct account link for the current session."""
    header = (FRONTEND_DIR / "header.html").read_text(encoding="utf-8")
    token = request.cookies.get("skill_link_session")
    is_logged_in = False
    if token:
        from security import hash_session_token

        db = SessionLocal()
        try:
            session = db.query(AuthSession).filter(AuthSession.token_hash == hash_session_token(token)).first()
            is_logged_in = session is not None and not session_has_expired(session.expires_at)
        finally:
            db.close()

    account_link = (
        '<li class="login"><a href="user_profile.html"><i class="ti-user"></i> My Profile</a></li>'
        if is_logged_in
        else '<li class="login"><a href="login.html"><i class="ti-user"></i> Sign in or Register</a></li>'
    )
    return HTMLResponse(header.replace("<!-- AUTH_NAV -->", account_link))

@app.get("/footer.html")
async def serve_footer():
    return FileResponse(FRONTEND_DIR / "footer.html")

app.add_middleware(
    CORSMiddleware,
    # The frontend may be served by FastAPI (port 8000) or a local static
    # server such as VS Code Live Server. Cookies require an explicit origin;
    # a wildcard origin cannot be used with credentials.
    # Allow localhost, loopback, and common private LAN IP ranges for phone testing.
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}|172\.(1[6-9]|2\d|3[0-1])\.\d{1,3}\.\d{1,3})(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

