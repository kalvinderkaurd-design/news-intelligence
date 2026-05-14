import requests
import os
import json
from datetime import datetime
from app.models import db, Article, AIAnalysis

class AIService:
    def __init__(self):
        self.webhook_url = os.getenv('N8N_WEBHOOK_URL')
        self.chat_webhook_url = os.getenv('N8N_CHAT_WEBHOOK_URL') or self.webhook_url

    def analyze_article(self, article):
        existing_analysis = AIAnalysis.query.filter_by(article_id=article.id).first()
        if existing_analysis and "Error" not in existing_analysis.summary:
            return {
                'summary': existing_analysis.summary,
                'sentiment': existing_analysis.sentiment,
                'insights': existing_analysis.insights.split('\n') if existing_analysis.insights else []
            }

        if not self.webhook_url:
            return self._mock_analysis(article)

        payload = {
            "article_id": article.id,
            "title": article.title,
            "content": article.content,
            "is_chat": False
        }

        try:
            response = requests.post(self.webhook_url, json=payload, timeout=60)
            response.raise_for_status()
            if not response.text.strip(): return self._mock_analysis(article)
            
            try:
                result = response.json()
            except ValueError:
                return self._mock_analysis(article)

            if isinstance(result, list) and len(result) > 0: result = result[0]
            
            summary = result.get('summary', 'Summary unavailable.')
            sentiment = result.get('sentiment', 'neutral')
            insights_list = result.get('insights', [])
            
            if isinstance(insights_list, str):
                insights_list = [i.strip() for i in insights_list.split('\n') if i.strip()]
            
            insights_str = "\n".join(insights_list)

            AIAnalysis.query.filter_by(article_id=article.id).delete()
            new_analysis = AIAnalysis(article_id=article.id, summary=summary, sentiment=sentiment, insights=insights_str)
            db.session.add(new_analysis)
            db.session.commit()

            return {'summary': summary, 'sentiment': sentiment, 'insights': insights_list}
        except Exception:
            return self._mock_analysis(article)

    def _mock_analysis(self, article):
        return {
            'summary': "AI Analysis is currently unavailable. Please check your n8n configuration.",
            'sentiment': "neutral",
            'insights': ["Could not generate insights."]
        }

    def chat_with_news(self, user_query, related_articles):
        context = ""
        for art in related_articles:
            context += f"Title: {art.title}\nContent: {art.content[:500]}...\n---\n"

        payload = {"query": user_query, "context": context, "is_chat": True}
        if not self.chat_webhook_url: return "Chat service is not configured."

        try:
            response = requests.post(self.chat_webhook_url, json=payload, timeout=60)
            response.raise_for_status()
            if not response.text.strip(): return "The chat service returned an empty response."
            
            try:
                result = response.json()
            except ValueError: return "Invalid response format."
            
            if isinstance(result, list) and len(result) > 0: result = result[0]
            return result.get('answer', "I couldn't process your request.")
        except Exception:
            return "Sorry, I encountered an error while processing your question."

class NewsService:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('NEWSDATA_API_KEY')
        self.base_url = "https://newsdata.io/api/1/news"

    def fetch_latest_news(self, query=None, language='en'):
        if not self.api_key: return 0
        self.cleanup_articles_without_images()
        
        total_saved = 0
        categories = [None, 'technology', 'business', 'science', 'politics', 'top', 'world']
        configs = []
        if query:
            configs.append({'q': query})
        else:
            for cat in categories: configs.append({'category': cat, 'country': 'in'})
            for cat in [None, 'business', 'technology']: configs.append({'category': cat})

        for config in configs:
            next_page = None
            pages_to_fetch = 2 if config.get('country') == 'in' else 1
            if query: pages_to_fetch = 3
            
            for page_num in range(pages_to_fetch):
                params = {'apikey': self.api_key, 'language': language, 'size': 10}
                params.update(config)
                if next_page: params['page'] = next_page

                try:
                    response = requests.get(self.base_url, params=params)
                    data = response.json()
                    if data.get('status') == 'success':
                        articles = data.get('results', [])
                        count = self._save_articles(articles)
                        total_saved += count
                        next_page = data.get('nextPage')
                        if not next_page: break
                    else: break
                except Exception: break
        return total_saved

    def cleanup_articles_without_images(self):
        try:
            Article.query.filter((Article.image_url == None) | (Article.image_url == '') | (Article.image_url == 'None') | (Article.image_url == 'undefined')).delete(synchronize_session=False)
            db.session.commit()
        except Exception: db.session.rollback()

    def search_news(self, query):
        if not query: return []
        
        from sqlalchemy import and_, or_
        words = [w.strip() for w in query.split() if len(w.strip()) > 3]
        if not words: words = [query]
        
        # 1. Try Strict Match (All keywords must be present)
        strict_filters = []
        for word in words[:3]:
            strict_filters.append(or_(Article.title.ilike(f"%{word}%"), Article.content.ilike(f"%{word}%")))
        
        results = Article.query.filter(and_(*strict_filters)).order_by(Article.published_at.desc()).limit(3).all()
        
        # 2. Fallback to Broad Match if strict fails
        if not results:
            broad_filters = []
            for word in words[:5]:
                broad_filters.append(Article.title.ilike(f"%{word}%"))
                broad_filters.append(Article.content.ilike(f"%{word}%"))
            results = Article.query.filter(or_(*broad_filters)).order_by(Article.published_at.desc()).limit(3).all()
            
        return results

    def _save_articles(self, articles_data):
        saved_count = 0
        for item in articles_data:
            title, link, image_url = item.get('title', 'No Title'), item.get('link'), item.get('image_url')
            if not image_url or image_url in ['None', 'undefined']: continue
            
            if Article.query.filter((Article.article_url == link) | (Article.title == title)).first(): continue

            try:
                pub_date_str = item.get('pubDate')
                try: pub_date = datetime.strptime(pub_date_str, '%Y-%m-%d %H:%M:%S')
                except: pub_date = datetime.utcnow()

                # Auto-tagging logic for Politics
                category_list = item.get('category', [])
                category_str = ",".join(category_list) if category_list else 'general'
                
                political_keywords = ['government', 'minister', 'cabinet', 'election', 'parliament', 'mla', 'mp', 'political', 'congress', 'bjp', 'modi', 'biden']
                if any(kw in title.lower() or kw in (item.get('description') or '').lower() for kw in political_keywords):
                    if 'politics' not in category_str.lower():
                        category_str = 'politics'

                new_article = Article(
                    title=title, content=item.get('description') or item.get('content', 'No content available'),
                    source=item.get('source_id', 'Unknown'), image_url=image_url, article_url=link,
                    published_at=pub_date, category=category_str,
                    language=item.get('language', 'en')
                )
                db.session.add(new_article)
                saved_count += 1
            except Exception: db.session.rollback()
        db.session.commit()
        return saved_count
