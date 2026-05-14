from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    db_dir = os.path.join(os.path.dirname(__file__), 'database')
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    
    port = int(os.environ.get('PORT', 8080))  
    app.run(debug=False, host='0.0.0.0', port=port)  