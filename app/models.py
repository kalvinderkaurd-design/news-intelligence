from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    oauth_provider = db.Column(db.String(50), default='google')
    oauth_id = db.Column(db.String(200), unique=True)
    profile_pic = db.Column(db.String(500), nullable=True)
    
    saved_articles = db.relationship('SavedArticle', backref='user', lazy=True)
    chat_history = db.relationship('ChatMessage', backref='user', lazy=True)

class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False) # 'user' or 'assistant'
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Article(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    content = db.Column(db.Text, nullable=True)
    source = db.Column(db.String(200), nullable=True)
    image_url = db.Column(db.String(1000), nullable=True)
    article_url = db.Column(db.String(1000), unique=True, nullable=False)
    published_at = db.Column(db.DateTime, default=datetime.utcnow)
    category = db.Column(db.String(100), nullable=True)
    language = db.Column(db.String(50), default='en')
    
    analysis = db.relationship('AIAnalysis', backref='article', uselist=False, lazy=True)
    saved_by = db.relationship('SavedArticle', backref='article', lazy=True)

class AIAnalysis(db.Model):
    __tablename__ = 'ai_analysis'
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'), nullable=False)
    summary = db.Column(db.Text, nullable=True)
    sentiment = db.Column(db.String(50), nullable=True) # Positive, Neutral, Negative
    insights = db.Column(db.Text, nullable=True) # JSON or newline separated
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)

class SavedArticle(db.Model):
    __tablename__ = 'saved_articles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'), nullable=False)
    saved_at = db.Column(db.DateTime, default=datetime.utcnow)
