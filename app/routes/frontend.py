from fastapi import APIRouter
from fastapi.responses import HTMLResponse
import os

router = APIRouter(prefix="/ui", tags=["Frontend"])

# Cache HTML files
_index_html = None
_dashboard_html = None
_admin_dashboard_html = None

def load_html(filename):
    """Load HTML template file"""
    template_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "templates", filename)
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"<html><body><p>Error loading {filename}: {str(e)}</p></body></html>"


@router.get("/", response_class=HTMLResponse)
async def home():
    """Serve home page"""
    global _index_html
    if _index_html is None:
        _index_html = load_html("index.html")
    return _index_html


@router.get("/dashboard", response_class=HTMLResponse)
async def admin_dashboard():
    """Serve admin dashboard with all API commands"""
    global _dashboard_html
    if _dashboard_html is None:
        _dashboard_html = load_html("dashboard.html")
    return _dashboard_html


@router.get("/interactive", response_class=HTMLResponse)
async def interactive_dashboard():
    """Serve interactive admin dashboard for executing commands directly"""
    global _admin_dashboard_html
    if _admin_dashboard_html is None:
        _admin_dashboard_html = load_html("admin-dashboard.html")
    return _admin_dashboard_html


@router.get("/{path:path}", response_class=HTMLResponse)
async def catch_all(path: str):
    """Fallback for SPA - serves home page"""
    global _index_html
    if _index_html is None:
        _index_html = load_html("index.html")
    return _index_html


