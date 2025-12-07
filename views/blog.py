import os
from flask import Blueprint, render_template, url_for, request, redirect, abort, current_app, jsonify
from werkzeug.utils import secure_filename
from models import Blog, BlogMeta
from sqlalchemy import or_
from views.auth import owner_required
from db import db
from utils import PAGES_DIR, list_images, ALLOWED_MD_EXT

blog_bp = Blueprint('blog_bp', __name__)


def is_allowed_md(filename):
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_MD_EXT


@blog_bp.route('/blog')
def blog_list():
    items = Blog.query.order_by(Blog.created_at.desc()).all()
    posts = []
    for p in items:
        logo = None
        if p.meta and p.meta.logo:
            logo = url_for('asset', page='blog', filename=p.meta.logo)
        else:
            default_path = os.path.join(PAGES_DIR, 'blog', 'logos', f"{p.slug}.png")
            if os.path.isfile(default_path):
                logo = url_for('asset', page='blog', filename=f"logos/{p.slug}.png")
        posts.append({'slug': p.slug, 'title': p.title, 'logo_url': logo})
    return render_template('blog_list.html', posts=posts, nav_active='blog')


@blog_bp.route('/blog/media/<filename>')
def blog_media(filename):
    dir_path = os.path.join(PAGES_DIR, 'blog', 'fig')
    file_path = os.path.join(dir_path, filename)
    if not os.path.isfile(file_path):
        abort(404)
    from flask import send_from_directory
    return send_from_directory(dir_path, filename)


@blog_bp.route('/blog/<slug>')
def blog_view(slug):
    p = Blog.query.filter_by(slug=slug).first()
    if not p:
        abort(404)
    logo = None
    if p.meta and p.meta.logo:
        logo = url_for('asset', page='blog', filename=p.meta.logo)
    else:
        default_path = os.path.join(PAGES_DIR, 'blog', 'logos', f"{p.slug}.png")
        if os.path.isfile(default_path):
            logo = url_for('asset', page='blog', filename=f"logos/{p.slug}.png")
    resume_dir = os.path.join(PAGES_DIR, 'blog', 'resume')
    resume_exist = None
    resume_url = None
    resume_ext = None
    abs_resume_url = None
    if os.path.isdir(resume_dir):
        candidates = [f"{slug}.pdf", f"{slug}.docx", f"{slug}.doc"]
        for fn in candidates:
            fp = os.path.join(resume_dir, fn)
            if os.path.isfile(fp):
                resume_exist = True
                resume_url = url_for('asset', page='blog', filename=f"resume/{fn}")
                resume_ext = os.path.splitext(fn)[1].lower()
                abs_resume_url = (request.url_root.rstrip('/') + resume_url) if resume_url else None
                break
    return render_template('blog_view.html', title=p.title or slug, summary=p.content or '', slug=slug, nav_active='blog', logo_url=logo, resume_exist=resume_exist, resume_url=resume_url, resume_ext=resume_ext, abs_resume_url=abs_resume_url)


@blog_bp.route('/blog/edit/<slug>', methods=['GET', 'POST'])
@owner_required
def blog_edit(slug):
    p = Blog.query.filter_by(slug=slug).first()
    if request.method == 'POST':
        new_slug = request.form.get('slug', '').strip() or slug
        new_slug = secure_filename(new_slug)
        summary = request.form.get('summary', '')
        title = request.form.get('title', '').strip()
        if not title:
            title = p.title if p else new_slug
        file = request.files.get('resume')
        if p:
            # handle slug change if unique
            if new_slug != slug:
                exists = Blog.query.filter_by(slug=new_slug).first()
                if not exists:
                    p.slug = new_slug
            p.title = title
            p.content = summary
        else:
            p = Blog(slug=new_slug, title=title, content=summary)
            db.session.add(p)
        if file and file.filename:
            ext = os.path.splitext(file.filename)[1].lower()
            if ext in {'.pdf', '.doc', '.docx'}:
                resume_dir = os.path.join(PAGES_DIR, 'blog', 'resume')
                os.makedirs(resume_dir, exist_ok=True)
                for old_ext in ['.pdf', '.doc', '.docx']:
                    old_path = os.path.join(resume_dir, secure_filename(f"{new_slug}{old_ext}"))
                    if os.path.isfile(old_path):
                        try:
                            os.remove(old_path)
                        except Exception:
                            pass
                filename = secure_filename(f"{new_slug}{ext}")
                path = os.path.join(resume_dir, filename)
                file.save(path)
        db.session.commit()
        # attach default logo mapping if missing
        if not p.meta:
            default_path = os.path.join(PAGES_DIR, 'blog', 'logos', f"{p.slug}.png")
            if os.path.isfile(default_path):
                db.session.add(BlogMeta(blog_id=p.id, logo=f"logos/{p.slug}.png"))
                db.session.commit()
        return redirect(url_for('blog_bp.blog_view', slug=p.slug))
    content = p.content if p else ''
    title = p.title if p else ''
    resume_dir = os.path.join(PAGES_DIR, 'blog', 'resume')
    resume_url = None
    if os.path.isdir(resume_dir):
        for fn in [f"{slug}.pdf", f"{slug}.docx", f"{slug}.doc"]:
            if os.path.isfile(os.path.join(resume_dir, fn)):
                resume_url = url_for('asset', page='blog', filename=f"resume/{fn}")
                break
    return render_template('editor.html', slug=slug, content=content, title=title, resume_url=resume_url, nav_active='blog')


@blog_bp.route('/blog/upload', methods=['GET', 'POST'])
@owner_required
def blog_upload():
    if request.method == 'POST':
        file = request.files.get('file')
        name = request.form.get('name', '').strip()
        if not file or file.filename == '':
            return redirect(url_for('blog_bp.blog_upload'))
        filename = secure_filename(file.filename)
        if not is_allowed_md(filename):
            return redirect(url_for('blog_bp.blog_upload'))
        if name:
            slug = secure_filename(name)
        else:
            slug = os.path.splitext(filename)[0]
        data = file.read()
        try:
            content = data.decode('utf-8')
        except Exception:
            content = data.decode('utf-8', errors='ignore')
        first = content.splitlines()[0] if content else ''
        title = first.lstrip('#').strip() if first.startswith('#') else slug
        p = Blog.query.filter_by(slug=slug).first()
        if p:
            p.content = content
            p.title = title
        else:
            p = Blog(slug=slug, title=title, content=content)
            db.session.add(p)
        db.session.commit()
        if not p.meta:
            default_path = os.path.join(PAGES_DIR, 'blog', 'logos', f"{slug}.png")
            if os.path.isfile(default_path):
                db.session.add(BlogMeta(blog_id=p.id, logo=f"logos/{slug}.png"))
                db.session.commit()
        return redirect(url_for('blog_bp.blog_view', slug=slug))
    return render_template('upload.html', nav_active='blog')


@blog_bp.route('/blog/delete/<slug>', methods=['POST'])
@owner_required
def blog_delete(slug):
    p = Blog.query.filter_by(slug=slug).first()
    if not p:
        return redirect(url_for('blog_bp.blog_list'))
    if p.meta:
        db.session.delete(p.meta)
    db.session.delete(p)
    db.session.commit()
    return redirect(url_for('blog_bp.blog_list'))


@blog_bp.route('/blog/resume/<slug>/download')
def blog_resume_download(slug):
    resume_dir = os.path.join(PAGES_DIR, 'blog', 'resume')
    if not os.path.isdir(resume_dir):
        abort(404)
    for fn in [f"{slug}.pdf", f"{slug}.docx", f"{slug}.doc"]:
        path = os.path.join(resume_dir, fn)
        if os.path.isfile(path):
            from flask import send_from_directory
            return send_from_directory(resume_dir, fn, as_attachment=True)
    abort(404)


# image upload no longer supported per requirements


@blog_bp.route('/blog/search')
def blog_search():
    q = request.args.get('q', '').strip()
    if not q:
        return redirect(url_for('blog_bp.blog_list'))
    items = Blog.query.filter(or_
        (Blog.title.ilike(f"%{q}%"), Blog.slug.ilike(f"%{q}%")).self_group()).order_by(Blog.created_at.desc()).all()
    posts = []
    for p in items:
        logo = None
        if p.meta and p.meta.logo:
            logo = url_for('asset', page='blog', filename=p.meta.logo)
        else:
            default_path = os.path.join(PAGES_DIR, 'blog', 'logos', f"{p.slug}.png")
            if os.path.isfile(default_path):
                logo = url_for('asset', page='blog', filename=f"logos/{p.slug}.png")
        posts.append({'slug': p.slug, 'title': p.title, 'logo_url': logo})
    return render_template('blog_search.html', posts=posts, query=q, nav_active='blog')

