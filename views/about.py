import os
from flask import Blueprint, render_template, url_for, request, redirect, send_from_directory, abort
from utils import PAGES_DIR, read_text_file, list_images
from models import Profile
from views.auth import owner_required
from config import Config
from werkzeug.utils import secure_filename
about_bp = Blueprint('about_bp', __name__)


@about_bp.route('/about')
def about():
    page_dir = PAGES_DIR + '/about'
    p = Profile.query.first()
    name = p.name if p and p.name else Config.SITE_OWNER_NAME
    direction = p.direction if p and p.direction else None
    message = p.message if p and p.message else None
    experience = p.experience if p and getattr(p, 'experience', None) else None
    awards = p.awards if p and getattr(p, 'awards', None) else None
    resume_dir = os.path.join(PAGES_DIR, 'about', 'resume')
    resume_url = None
    if os.path.isdir(resume_dir):
        items = []
        for fn in os.listdir(resume_dir):
            ext = os.path.splitext(fn)[1].lower()
            if ext in {'.pdf', '.doc', '.docx'}:
                items.append(fn)
        items.sort()
        if items:
            resume_url = url_for('asset', page='about', filename=f"resume/{items[-1]}")
    return render_template('about.html', title='个人简介', name=name, direction=direction, message=message, experience=experience, awards=awards, resume_url=resume_url, nav_active='about')


@about_bp.route('/about/edit', methods=['GET', 'POST'])
@owner_required
def about_edit():
    p = Profile.query.first()
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        direction = request.form.get('direction', '').strip()
        message = request.form.get('message', '').strip()
        experience = request.form.get('experience', '').strip()
        awards = request.form.get('awards', '').strip()
        file = request.files.get('resume')
        saved = None
        if file and file.filename:
            ext = os.path.splitext(file.filename)[1].lower()
            if ext in {'.pdf', '.doc', '.docx'}:
                resume_dir = os.path.join(PAGES_DIR, 'about', 'resume')
                os.makedirs(resume_dir, exist_ok=True)
                filename = 'resume' + ext
                path = os.path.join(resume_dir, secure_filename(filename))
                file.save(path)
                saved = filename
        if p:
            p.name = name
            p.direction = direction
            p.message = message
            p.experience = experience
            p.awards = awards
        else:
            p = Profile(name=name, direction=direction, message=message, experience=experience, awards=awards)
            from db import db
            db.session.add(p)
        from db import db
        db.session.commit()
        return redirect(url_for('about_bp.about'))
    name = p.name if p and p.name else ''
    direction = p.direction if p and p.direction else ''
    message = p.message if p and p.message else ''
    experience = p.experience if p and getattr(p, 'experience', None) else ''
    awards = p.awards if p and getattr(p, 'awards', None) else ''
    resume_dir = os.path.join(PAGES_DIR, 'about', 'resume')
    resume_url = None
    if os.path.isdir(resume_dir):
        items = []
        for fn in os.listdir(resume_dir):
            ext = os.path.splitext(fn)[1].lower()
            if ext in {'.pdf', '.doc', '.docx'}:
                items.append(fn)
        items.sort()
        if items:
            resume_url = url_for('asset', page='about', filename=f"resume/{items[-1]}")
    return render_template('about_edit.html', name=name, direction=direction, message=message, experience=experience, awards=awards, resume_url=resume_url, nav_active='about')


@about_bp.route('/about/resume/download')
def resume_download():
    resume_dir = os.path.join(PAGES_DIR, 'about', 'resume')
    if not os.path.isdir(resume_dir):
        abort(404)
    items = []
    for fn in os.listdir(resume_dir):
        ext = os.path.splitext(fn)[1].lower()
        if ext in {'.pdf', '.doc', '.docx'}:
            items.append(fn)
    items.sort()
    if not items:
        abort(404)
    filename = items[-1]
    return send_from_directory(resume_dir, filename, as_attachment=True)
