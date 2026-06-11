import os
import secrets
from flask import (Flask, render_template, request, redirect,
                   url_for, flash, session, jsonify)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy import or_, desc
from functools import wraps
from datetime import datetime

from models import db, User, Post, Comment, Like, Message, Block, Notification

# ─────────────────────────────────────────────────────────────────────────────
# App Setup
# ─────────────────────────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'gminsta_super_secret_2026_key')

# Database — update credentials as needed
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASS = os.environ.get('DB_PASS', 'root')
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_NAME = os.environ.get('DB_NAME', 'gminsta')

# Always include password field (even if empty) so MySQL auth works
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f'mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}'
)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Upload config
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
AVATARS_DIR = os.path.join(BASE_DIR, 'static', 'uploads', 'avatars')
POSTS_DIR   = os.path.join(BASE_DIR, 'static', 'uploads', 'posts')
app.config['UPLOAD_FOLDER_AVATARS'] = AVATARS_DIR
app.config['UPLOAD_FOLDER_POSTS']   = POSTS_DIR
app.config['MAX_CONTENT_LENGTH']    = 16 * 1024 * 1024  # 16 MB

# Ensure upload dirs exist
os.makedirs(AVATARS_DIR, exist_ok=True)
os.makedirs(POSTS_DIR,   exist_ok=True)

db.init_app(app)

# Create tables on first run
with app.app_context():
    db.create_all()

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'danger')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated


def save_upload(file_storage, folder):
    """Save uploaded file, return unique filename."""
    fname = secure_filename(file_storage.filename)
    hex_name = secrets.token_hex(8) + '_' + fname
    file_storage.save(os.path.join(folder, hex_name))
    return hex_name


def push_notification(recipient_id, actor_id, notif_type, post_id=None):
    """Create a notification if actor != recipient."""
    if recipient_id == actor_id:
        return
    n = Notification(
        recipient_id=recipient_id,
        actor_id=actor_id,
        notif_type=notif_type,
        post_id=post_id
    )
    db.session.add(n)


# ─────────────────────────────────────────────────────────────────────────────
# Context Processor – inject current_user & dark mode into every template
# ─────────────────────────────────────────────────────────────────────────────
@app.context_processor
def inject_user():
    user = None
    dark_mode = False
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            dark_mode = user.dark_mode
    return dict(current_user=user, dark_mode=dark_mode)


# ─────────────────────────────────────────────────────────────────────────────
# Auth Routes
# ─────────────────────────────────────────────────────────────────────────────
@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('feed'))
    if request.method == 'POST':
        username = request.form['username'].strip()
        email    = request.form['email'].strip()
        password = request.form['password']
        if not username or not email or not password:
            flash('All fields are required.', 'danger')
            return redirect(url_for('register'))
        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return redirect(url_for('register'))
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return redirect(url_for('register'))
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('register'))
        new_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('feed'))
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            flash(f'Welcome back, {user.username}! 👋', 'success')
            return redirect(request.args.get('next') or url_for('feed'))
        flash('Invalid username or password.', 'danger')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


# ─────────────────────────────────────────────────────────────────────────────
# Feed
# ─────────────────────────────────────────────────────────────────────────────
@app.route('/')
@login_required
def feed():
    me = User.query.get(session['user_id'])

    following_ids  = [u.id for u in me.followed]
    following_ids.append(me.id)

    blocked_by_me  = [b.blocked_id  for b in Block.query.filter_by(blocker_id=me.id).all()]
    blocked_me     = [b.blocker_id  for b in Block.query.filter_by(blocked_id=me.id).all()]
    blacklist      = set(blocked_by_me + blocked_me)

    valid_ids = [uid for uid in following_ids if uid not in blacklist]
    posts = (Post.query
             .filter(Post.user_id.in_(valid_ids))
             .order_by(Post.created_at.desc())
             .limit(50)
             .all())
    return render_template('feed.html', posts=posts)


# Explore – all public posts (optional discovery page)
@app.route('/explore')
@login_required
def explore():
    me = User.query.get(session['user_id'])
    blocked_by_me = [b.blocked_id for b in Block.query.filter_by(blocker_id=me.id).all()]
    blocked_me    = [b.blocker_id  for b in Block.query.filter_by(blocked_id=me.id).all()]
    blacklist     = set(blocked_by_me + blocked_me)

    posts = (Post.query
             .filter(~Post.user_id.in_(blacklist))
             .order_by(Post.created_at.desc())
             .limit(60)
             .all())
    return render_template('explore.html', posts=posts)


# ─────────────────────────────────────────────────────────────────────────────
# Posts
# ─────────────────────────────────────────────────────────────────────────────
@app.route('/post/create', methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == 'POST':
        caption = request.form.get('caption', '').strip()
        if 'image' not in request.files or request.files['image'].filename == '':
            flash('Please select an image file.', 'danger')
            return redirect(request.url)
        file = request.files['image']
        if not allowed_file(file.filename):
            flash('Allowed image types: PNG, JPG, JPEG, GIF, WEBP', 'danger')
            return redirect(request.url)
        filename = save_upload(file, app.config['UPLOAD_FOLDER_POSTS'])
        new_post = Post(user_id=session['user_id'], image=filename, caption=caption)
        db.session.add(new_post)
        db.session.commit()
        flash('Post shared! 🎉', 'success')
        return redirect(url_for('feed'))
    return render_template('create_post.html')


@app.route('/post/delete/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.user_id != session['user_id']:
        flash('You cannot delete someone else\'s post.', 'danger')
        return redirect(url_for('feed'))
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted.', 'info')
    return redirect(url_for('profile', username=User.query.get(session['user_id']).username))


@app.route('/post/like/<int:post_id>', methods=['POST'])
@login_required
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    me_id = session['user_id']
    existing = Like.query.filter_by(user_id=me_id, post_id=post_id).first()
    if existing:
        db.session.delete(existing)
    else:
        db.session.add(Like(user_id=me_id, post_id=post_id))
        push_notification(post.user_id, me_id, 'like', post_id)
    db.session.commit()
    return redirect(request.referrer or url_for('feed'))


@app.route('/post/comment/<int:post_id>', methods=['POST'])
@login_required
def comment_post(post_id):
    text = request.form.get('text', '').strip()
    if text:
        post = Post.query.get_or_404(post_id)
        c = Comment(user_id=session['user_id'], post_id=post_id, text=text)
        db.session.add(c)
        push_notification(post.user_id, session['user_id'], 'comment', post_id)
        db.session.commit()
    return redirect(request.referrer or url_for('feed'))


# ─────────────────────────────────────────────────────────────────────────────
# Profile & Follow
# ─────────────────────────────────────────────────────────────────────────────
@app.route('/profile/<username>')
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    me   = User.query.get(session['user_id'])

    is_blocked_by_me   = Block.query.filter_by(blocker_id=me.id,   blocked_id=user.id).first() is not None
    is_blocked_by_them = Block.query.filter_by(blocker_id=user.id, blocked_id=me.id).first()  is not None

    if is_blocked_by_them:
        flash('User not found.', 'danger')
        return redirect(url_for('feed'))

    posts = Post.query.filter_by(user_id=user.id).order_by(Post.created_at.desc()).all()
    return render_template('profile.html', user=user, posts=posts, is_blocked=is_blocked_by_me)


@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        user.bio        = request.form.get('bio', '').strip()
        user.is_private = 'is_private' in request.form

        file = request.files.get('profile_pic')
        if file and file.filename and allowed_file(file.filename):
            user.profile_pic = save_upload(file, app.config['UPLOAD_FOLDER_AVATARS'])

        db.session.commit()
        flash('Profile updated. ✅', 'success')
        return redirect(url_for('profile', username=user.username))
    return render_template('edit_profile.html', user=user)


@app.route('/settings/darkmode', methods=['POST'])
@login_required
def toggle_dark_mode():
    user = User.query.get(session['user_id'])
    user.dark_mode = not user.dark_mode
    db.session.commit()
    return redirect(request.referrer or url_for('feed'))


@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    target = User.query.filter_by(username=username).first_or_404()
    me     = User.query.get(session['user_id'])
    if me.id == target.id:
        flash('You cannot follow yourself.', 'warning')
        return redirect(url_for('profile', username=username))
    if me.is_following(target):
        me.unfollow(target)
        flash(f'Unfollowed {username}', 'info')
    else:
        me.follow(target)
        push_notification(target.id, me.id, 'follow')
        flash(f'Now following {username} 🎉', 'success')
    db.session.commit()
    return redirect(url_for('profile', username=username))


@app.route('/block/<username>', methods=['POST'])
@login_required
def block_user(username):
    target = User.query.filter_by(username=username).first_or_404()
    me     = User.query.get(session['user_id'])
    existing = Block.query.filter_by(blocker_id=me.id, blocked_id=target.id).first()
    if existing:
        db.session.delete(existing)
        flash(f'Unblocked {username}', 'success')
    else:
        db.session.add(Block(blocker_id=me.id, blocked_id=target.id))
        me.unfollow(target)
        target.unfollow(me)
        flash(f'Blocked {username}', 'warning')
    db.session.commit()
    return redirect(url_for('profile', username=username))


# ─────────────────────────────────────────────────────────────────────────────
# Search
# ─────────────────────────────────────────────────────────────────────────────
@app.route('/search')
@login_required
def search():
    q     = request.args.get('q', '').strip()
    users = []
    if q:
        users = (User.query
                 .filter(User.username.ilike(f'%{q}%'),
                         User.id != session['user_id'])
                 .limit(20).all())
    return render_template('search.html', users=users, query=q)


# ─────────────────────────────────────────────────────────────────────────────
# Chat / Messaging
# ─────────────────────────────────────────────────────────────────────────────
@app.route('/chat')
@login_required
def chat_index():
    me = User.query.get(session['user_id'])
    # Recent conversations: unique users I chatted with
    sent_to     = db.session.query(Message.receiver_id).filter_by(sender_id=me.id)
    received_from = db.session.query(Message.sender_id).filter_by(receiver_id=me.id)
    partner_ids = {r[0] for r in sent_to.union(received_from).all()}
    partners    = User.query.filter(User.id.in_(partner_ids)).all()
    return render_template('chat_index.html', partners=partners)


@app.route('/chat/<username>', methods=['GET', 'POST'])
@login_required
def chat(username):
    target = User.query.filter_by(username=username).first_or_404()
    me_id  = session['user_id']

    if request.method == 'POST':
        text = request.form.get('message', '').strip()
        if text:
            msg = Message(sender_id=me_id, receiver_id=target.id, message=text)
            db.session.add(msg)
            push_notification(target.id, me_id, 'message')
            db.session.commit()
        return redirect(url_for('chat', username=username))

    # Mark received messages as read
    Message.query.filter_by(sender_id=target.id, receiver_id=me_id, is_read=False).update({'is_read': True})
    db.session.commit()

    messages = (Message.query
                .filter(or_(
                    (Message.sender_id == me_id)   & (Message.receiver_id == target.id),
                    (Message.sender_id == target.id) & (Message.receiver_id == me_id)
                ))
                .order_by(Message.timestamp.asc())
                .all())
    return render_template('chat.html', target=target, messages=messages)


# ─────────────────────────────────────────────────────────────────────────────
# Notifications
# ─────────────────────────────────────────────────────────────────────────────
@app.route('/notifications')
@login_required
def notifications():
    me    = User.query.get(session['user_id'])
    notifs = (Notification.query
              .filter_by(recipient_id=me.id)
              .order_by(Notification.created_at.desc())
              .limit(50)
              .all())
    # Mark all read
    Notification.query.filter_by(recipient_id=me.id, is_read=False).update({'is_read': True})
    db.session.commit()
    return render_template('notifications.html', notifications=notifs)


@app.route('/notifications/count')
@login_required
def notification_count():
    count = Notification.query.filter_by(
        recipient_id=session['user_id'], is_read=False
    ).count()
    return jsonify({'count': count})


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=True)
