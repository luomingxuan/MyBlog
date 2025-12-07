from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, current_app


auth_bp = Blueprint('auth_bp', __name__)


def owner_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get('is_owner'):
            return redirect(url_for('auth_bp.login', next=request.path))
        return fn(*args, **kwargs)
    return wrapper


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    error = ''
    if request.method == 'POST':
        password = request.form.get('password', '')
        if password == current_app.config.get('OWNER_PASSWORD'):
            session['is_owner'] = True
            nxt = request.args.get('next') or url_for('home_bp.index')
            return redirect(nxt)
        error = '密码错误'
    return render_template('login.html', error=error)


@auth_bp.route('/logout')
def logout():
    session.pop('is_owner', None)
    return redirect(url_for('home_bp.index'))

