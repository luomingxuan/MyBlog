import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, abort
from werkzeug.utils import secure_filename

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PAGES_DIR = os.path.join(BASE_DIR, 'pages')

ALLOWED_MD_EXT = {'.md'}
ALLOWED_IMG_EXT = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}


def ensure_dirs():
    os.makedirs(PAGES_DIR, exist_ok=True)
    os.makedirs(os.path.join(PAGES_DIR, 'home', 'fig'), exist_ok=True)
    os.makedirs(os.path.join(PAGES_DIR, 'about', 'fig'), exist_ok=True)
    os.makedirs(os.path.join(PAGES_DIR, 'blog', 'fig'), exist_ok=True)
    os.makedirs(os.path.join(PAGES_DIR, 'blog', 'posts'), exist_ok=True)


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


ensure_dirs()


@app.route('/')
def index():
    page_dir = os.path.join(PAGES_DIR, 'home')
    content = read_text_file([
        os.path.join(page_dir, 'index.md'),
        os.path.join(page_dir, 'index.txt'),
    ])
    figs = list_images(os.path.join(page_dir, 'fig'))
    image_urls = [url_for('media', page='home', filename=fn) for fn in figs]
    return render_template('page.html', title='主页', content=content, image_urls=image_urls, nav_active='home', name='骆明轩LMX')


@app.route('/about')
def about():
    page_dir = os.path.join(PAGES_DIR, 'about')
    content = read_text_file([
        os.path.join(page_dir, 'index.md'),
        os.path.join(page_dir, 'index.txt'),
    ])
    figs = list_images(os.path.join(page_dir, 'fig'))
    image_urls = [url_for('media', page='about', filename=fn) for fn in figs]
    return render_template('page.html', title='个人简介', content=content, image_urls=image_urls, nav_active='about', name='骆明轩LMX')


@app.route('/media/<page>/<filename>')
def media(page, filename):
    dir_path = os.path.join(PAGES_DIR, page, 'fig')
    file_path = os.path.join(dir_path, filename)
    if not os.path.isfile(file_path):
        abort(404)
    return send_from_directory(dir_path, filename)


def get_posts():
    posts_dir = os.path.join(PAGES_DIR, 'blog', 'posts')
    posts = []
    for fn in sorted(os.listdir(posts_dir)):
        if fn.lower().endswith('.md'):
            slug = os.path.splitext(fn)[0]
            path = os.path.join(posts_dir, fn)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            first = content.splitlines()[0] if content else ''
            if first.startswith('#'):
                title = first.lstrip('#').strip()
            else:
                title = slug
            posts.append({'slug': slug, 'title': title})
    return posts


@app.route('/blog')
def blog_list():
    posts = get_posts()
    return render_template('blog_list.html', posts=posts, nav_active='blog', name='骆明轩LMX')


@app.route('/blog/media/<filename>')
def blog_media(filename):
    dir_path = os.path.join(PAGES_DIR, 'blog', 'fig')
    file_path = os.path.join(dir_path, filename)
    if not os.path.isfile(file_path):
        abort(404)
    return send_from_directory(dir_path, filename)


@app.route('/blog/<slug>')
def blog_view(slug):
    path = os.path.join(PAGES_DIR, 'blog', 'posts', slug + '.md')
    if not os.path.isfile(path):
        abort(404)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    figs = list_images(os.path.join(PAGES_DIR, 'blog', 'fig'))
    image_urls = [url_for('blog_media', filename=fn) for fn in figs]
    return render_template('blog_view.html', title=slug, content=content, image_urls=image_urls, slug=slug, nav_active='blog', name='骆明轩LMX')


@app.route('/blog/edit/<slug>', methods=['GET', 'POST'])
def blog_edit(slug):
    posts_dir = os.path.join(PAGES_DIR, 'blog', 'posts')
    os.makedirs(posts_dir, exist_ok=True)
    path = os.path.join(posts_dir, slug + '.md')
    if request.method == 'POST':
        content = request.form.get('content', '')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return redirect(url_for('blog_view', slug=slug))
    content = ''
    if os.path.isfile(path):
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
    return render_template('editor.html', slug=slug, content=content, nav_active='blog', name='骆明轩LMX')


def is_allowed_md(filename):
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_MD_EXT


@app.route('/blog/upload', methods=['GET', 'POST'])
def blog_upload():
    posts_dir = os.path.join(PAGES_DIR, 'blog', 'posts')
    os.makedirs(posts_dir, exist_ok=True)
    if request.method == 'POST':
        file = request.files.get('file')
        name = request.form.get('name', '').strip()
        if not file or file.filename == '':
            return redirect(url_for('blog_upload'))
        filename = secure_filename(file.filename)
        if not is_allowed_md(filename):
            return redirect(url_for('blog_upload'))
        if name:
            slug = secure_filename(name)
            if not slug.lower().endswith('.md'):
                filename = slug + '.md'
            else:
                filename = slug
        save_path = os.path.join(posts_dir, filename)
        file.save(save_path)
        slug = os.path.splitext(filename)[0]
        return redirect(url_for('blog_view', slug=slug))
    return render_template('upload.html', nav_active='blog', name='骆明轩LMX')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

