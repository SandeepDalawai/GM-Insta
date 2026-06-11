from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# ─── Many-to-many: followers ────────────────────────────────────────────────
followers = db.Table(
    'followers',
    db.Column('follower_id',  db.Integer, db.ForeignKey('users.id')),
    db.Column('following_id', db.Integer, db.ForeignKey('users.id'))
)


class User(db.Model):
    __tablename__ = 'users'
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(50),  unique=True, nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    profile_pic   = db.Column(db.String(200), default='default.jpg')
    bio           = db.Column(db.String(500), default='')
    is_private    = db.Column(db.Boolean, default=False)
    dark_mode     = db.Column(db.Boolean, default=False)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    posts    = db.relationship('Post',    backref='author', lazy=True,
                               cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', lazy=True,
                               cascade='all, delete-orphan')
    likes    = db.relationship('Like',    backref='user',   lazy=True,
                               cascade='all, delete-orphan')

    # Self-referential follower/following
    followed = db.relationship(
        'User',
        secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.following_id == id),
        backref=db.backref('followers_list', lazy='dynamic'),
        lazy='dynamic'
    )

    # Notifications (received)
    notifications = db.relationship('Notification', foreign_keys='Notification.recipient_id',
                                    backref='recipient', lazy=True,
                                    cascade='all, delete-orphan')

    def is_following(self, user):
        return self.followed.filter(followers.c.following_id == user.id).count() > 0

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def followers_count(self):
        return self.followers_list.count()

    def following_count(self):
        return self.followed.count()

    def unread_notifications(self):
        return Notification.query.filter_by(
            recipient_id=self.id, is_read=False
        ).count()


class Post(db.Model):
    __tablename__ = 'posts'
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    image      = db.Column(db.String(200), nullable=False)
    caption    = db.Column(db.String(2000), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    comments = db.relationship('Comment', backref='post', lazy=True,
                               cascade='all, delete-orphan')
    likes    = db.relationship('Like',    backref='post', lazy=True,
                               cascade='all, delete-orphan')

    def is_liked_by(self, user_id):
        return Like.query.filter_by(user_id=user_id, post_id=self.id).first() is not None

    def like_count(self):
        return Like.query.filter_by(post_id=self.id).count()


class Comment(db.Model):
    __tablename__ = 'comments'
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id    = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    text       = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Like(db.Model):
    __tablename__ = 'likes'
    id      = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)


class Message(db.Model):
    __tablename__ = 'messages'
    id          = db.Column(db.Integer, primary_key=True)
    sender_id   = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message     = db.Column(db.String(2000), nullable=False)
    timestamp   = db.Column(db.DateTime, default=datetime.utcnow)
    is_read     = db.Column(db.Boolean, default=False)

    sender   = db.relationship('User', foreign_keys=[sender_id],   backref='sent_messages')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages')


class Block(db.Model):
    __tablename__ = 'blocks'
    id         = db.Column(db.Integer, primary_key=True)
    blocker_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    blocked_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)


class Notification(db.Model):
    """In-app notification system."""
    __tablename__ = 'notifications'
    id           = db.Column(db.Integer, primary_key=True)
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    actor_id     = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    notif_type   = db.Column(db.String(20), nullable=False)  # 'like','comment','follow','message'
    post_id      = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=True)
    is_read      = db.Column(db.Boolean, default=False)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)

    actor = db.relationship('User', foreign_keys=[actor_id])
    post  = db.relationship('Post', foreign_keys=[post_id])
