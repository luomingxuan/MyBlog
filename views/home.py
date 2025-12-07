import os
from flask import Blueprint, render_template, url_for
from utils import PAGES_DIR, read_text_file, list_images
from models import Blog

home_bp = Blueprint('home_bp', __name__)


@home_bp.route('/')
def index():
    page_dir = PAGES_DIR + '/home'
    logo_path = page_dir + '/logo.png'
    bg_path = page_dir + '/background.png'
    logo_url = url_for('asset', page='home', filename='logo.png') if os.path.isfile(logo_path) else None
    background_url = url_for('asset', page='home', filename='background.png') if os.path.isfile(bg_path) else None
    latest_items = Blog.query.order_by(Blog.created_at.desc()).limit(5).all()
    latest_posts = []
    for p in latest_items:
        logo = None
        if getattr(p, 'meta', None) and p.meta.logo:
            logo = url_for('asset', page='blog', filename=p.meta.logo)
        else:
            default_path = os.path.join(PAGES_DIR, 'blog', 'logos', f"{p.slug}.png")
            if os.path.isfile(default_path):
                logo = url_for('asset', page='blog', filename=f"logos/{p.slug}.png")
        latest_posts.append({'slug': p.slug, 'title': p.title, 'logo_url': logo})
    return render_template(
        'home.html',
        title='主页',
        logo_url=logo_url,
        background_url=background_url,
        latest_posts=latest_posts,
        nav_active='home',
    )

