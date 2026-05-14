from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    # Ensure database directory exists
    db_dir = os.path.join(os.path.dirname(__file__), 'database')
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
        
    app.run(debug=True, port=5001)
