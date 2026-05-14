from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app.models import db, User, Article, SavedArticle, AIAnalysis, ChatMessage
from app.services import AIService, NewsService
from sqlalchemy import or_
import os

main_bp = Blueprint('main', __name__)
auth_bp = Blueprint('auth', __name__)
api_bp = Blueprint('api', __name__)

ai_service = AIService()
news_service = NewsService()

# --- Main Routes ---
@main_bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search')
    query = Article.query.filter(Article.image_url != None, Article.image_url != '', Article.image_url != 'None', Article.image_url != 'undefined')
    if search:
        query = query.filter(or_(Article.title.like(f"%{search}%"), Article.content.like(f"%{search}%")))
    
    pagination = query.order_by(Article.published_at.desc()).paginate(page=page, per_page=25, error_out=False)
    return render_template('index.html', articles=pagination.items, pagination=pagination)

@main_bp.route('/saved')
@login_required
def saved_articles():
    saved = SavedArticle.query.filter_by(user_id=current_user.id).all()
    return render_template('saved.html', articles=[s.article for s in saved])

@main_bp.route('/ask-ai')
@login_required
def ask_ai():
    history = ChatMessage.query.filter_by(user_id=current_user.id).order_by(ChatMessage.timestamp.asc()).all()
    return render_template('ask_ai.html', history=history)

@main_bp.route('/article/<int:article_id>')
@login_required
def article_detail(article_id):
    return render_template('article.html', article=Article.query.get_or_404(article_id))

# --- Auth Routes ---
@auth_bp.route('/login')
def login():
    if current_user.is_authenticated: return redirect(url_for('main.index'))
    return render_template('login.html')

@auth_bp.route('/terms')
def terms():
    return render_template('terms.html')

@auth_bp.route('/login/google')
def login_google():
    google = current_app.extensions['google_oauth']
    redirect_uri = url_for('auth.callback', _external=True, _scheme='https')
    return google.authorize_redirect(redirect_uri)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/callback')
def callback():
    try:
        google = current_app.extensions['google_oauth']
        token = google.authorize_access_token()
        # Use the absolute OpenID Connect userinfo endpoint
        user_info = google.get('https://openidconnect.googleapis.com/v1/userinfo').json()

        
        email, name, google_id = user_info.get('email'), user_info.get('name'), user_info.get('sub') or user_info.get('id')


        user = User.query.filter_by(email=email).first()
        picture = user_info.get('picture')
        
        if not user:
            user = User(username=name or email.split('@')[0], email=email, oauth_provider='google', oauth_id=google_id, profile_pic=picture)
            db.session.add(user)
        else:
            user.profile_pic = picture
        
        db.session.commit()
        login_user(user)
        return redirect(url_for('main.index'))
    
    except Exception as e:
        current_app.logger.error(f"OAuth callback failed: {str(e)}")
        flash('Login failed. Please try again.', 'error')
        return redirect(url_for('auth.login'))




# --- API Routes ---
@api_bp.route('/analyze/<int:article_id>', methods=['POST'])
@login_required
def analyze(article_id):
    return jsonify(ai_service.analyze_article(Article.query.get_or_404(article_id)))

@api_bp.route('/chat', methods=['POST'])
@login_required
def chat():
    user_query = request.json.get('query')
    
    # Save user message
    user_msg = ChatMessage(user_id=current_user.id, role='user', content=user_query)
    db.session.add(user_msg)
    
    related = news_service.search_news(user_query)
    ai_response = ai_service.chat_with_news(user_query, related)
    
    # Save assistant response
    ai_msg = ChatMessage(user_id=current_user.id, role='assistant', content=ai_response)
    db.session.add(ai_msg)
    db.session.commit()
    
    sources = [{'id': a.id, 'title': a.title} for a in related]
    return jsonify({
        'answer': ai_response,
        'sources': sources
    })

@api_bp.route('/save/<int:article_id>', methods=['POST'])
@login_required
def save_article(article_id):
    existing = SavedArticle.query.filter_by(user_id=current_user.id, article_id=article_id).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        return jsonify({'status': 'unsaved'})
    db.session.add(SavedArticle(user_id=current_user.id, article_id=article_id))
    db.session.commit()
    return jsonify({'status': 'saved'})

@api_bp.route('/refresh-news', methods=['POST'])
@login_required
def refresh_news():
    return jsonify({'count': news_service.fetch_latest_news()})

@api_bp.route('/clear-chat', methods=['POST'])
@login_required
def clear_chat():
    ChatMessage.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    return jsonify({'status': 'success'})
