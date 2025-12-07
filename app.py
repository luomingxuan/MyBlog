import os
from flask import Flask, send_from_directory, abort, session
from werkzeug.utils import secure_filename
from db import db
from models import Blog, Profile
from utils import ensure_page_dirs, PAGES_DIR
from views.home import home_bp
from views.about import about_bp
from views.blog import blog_bp
from views.auth import auth_bp
from config import Config
from sqlalchemy.sql import text

# Flask 应用入口：创建应用、加载配置并初始化数据库
app = Flask(__name__)
app.config.from_object(Config)  # 从独立的配置文件加载配置项
app.secret_key = app.config.get('SECRET_KEY')
db.init_app(app)  # 将SQLAlchemy与当前应用绑定

# 模板上下文处理器：为所有模板注入站点所有者名称变量
@app.context_processor
def inject_name():
    name = app.config.get('SITE_OWNER_NAME')
    try:
        p = Profile.query.first()
        if p and p.name:
            name = p.name
    except Exception:
        pass
    return {'name': name, 'is_owner': bool(session.get('is_owner'))}


# 确保数据目录与页面内容目录存在
os.makedirs(app.config['DATA_DIR'], exist_ok=True)
ensure_page_dirs()

with app.app_context():
    # 创建所有数据库表；首次启动时写入一篇示例文章
    db.create_all()
    try:
        cols = db.session.execute(text("PRAGMA table_info(profile)")).fetchall()
        names = {c[1] for c in cols}
        if 'experience' not in names:
            db.session.execute(text("ALTER TABLE profile ADD COLUMN experience TEXT"))
        if 'awards' not in names:
            db.session.execute(text("ALTER TABLE profile ADD COLUMN awards TEXT"))
        db.session.commit()
    except Exception:
        pass
    if Blog.query.count() == 0:
        sample_path = os.path.join(PAGES_DIR, 'blog', 'posts', 'sample.md')
        if os.path.isfile(sample_path):
            with open(sample_path, 'r', encoding='utf-8') as f:
                c = f.read()
        else:
            c = '# 示例文章\n\n这是一个示例Markdown文章。'
        first = c.splitlines()[0] if c else ''
        title = first.lstrip('#').strip() if first.startswith('#') else 'sample'
        db.session.add(Blog(slug='sample', title=title, content=c))
        db.session.commit()


# 注册页面蓝图：主页、个人简介、博客模块
app.register_blueprint(home_bp)
app.register_blueprint(about_bp)
app.register_blueprint(blog_bp)
app.register_blueprint(auth_bp)


@app.route('/media/<page>/<filename>')
def media(page, filename):
    """静态媒体文件路由

    参数:
        page: 页面名称（home/about/blog），用于定位该页的fig目录
        filename: 媒体文件名

    返回:
        该媒体文件的内容，如果不存在则返回404
    """
    dir_path = os.path.join(PAGES_DIR, page, 'fig')
    file_path = os.path.join(dir_path, filename)
    if not os.path.isfile(file_path):
        abort(404)
    return send_from_directory(dir_path, filename)


@app.route('/asset/<page>/<path:filename>')
def asset(page, filename):
    dir_path = os.path.join(PAGES_DIR, page)
    file_path = os.path.join(dir_path, filename)
    if not os.path.isfile(file_path):
        abort(404)
    return send_from_directory(dir_path, filename)


 
if __name__ == '__main__':
    # 开发模式运行应用
    app.run(host='0.0.0.0', port=5000, debug=True)

