import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PAGES_DIR = os.path.join(BASE_DIR, 'pages')

ALLOWED_MD_EXT = {'.md'}
ALLOWED_IMG_EXT = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}


def ensure_page_dirs():
    os.makedirs(PAGES_DIR, exist_ok=True)
    os.makedirs(os.path.join(PAGES_DIR, 'home', 'fig'), exist_ok=True)
    os.makedirs(os.path.join(PAGES_DIR, 'about', 'fig'), exist_ok=True)
    os.makedirs(os.path.join(PAGES_DIR, 'about', 'resume'), exist_ok=True)
    os.makedirs(os.path.join(PAGES_DIR, 'blog', 'fig'), exist_ok=True)
    os.makedirs(os.path.join(PAGES_DIR, 'blog', 'posts'), exist_ok=True)
    os.makedirs(os.path.join(PAGES_DIR, 'blog', 'resume'), exist_ok=True)


def read_text_file(paths):
    for p in paths:
        if os.path.isfile(p):
            with open(p, 'r', encoding='utf-8') as f:
                return f.read()
    return ''


def list_images(dir_path):
    if not os.path.isdir(dir_path):
        return []
    items = []
    for fn in os.listdir(dir_path):
        ext = os.path.splitext(fn)[1].lower()
        if ext in ALLOWED_IMG_EXT:
            items.append(fn)
    return sorted(items)

