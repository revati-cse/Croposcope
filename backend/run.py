from app import create_app, db
import os

app = create_app()

@app.before_first_request
def create_tables():
    """Create database tables on first request"""
    db.create_all()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    app.run(
        host=os.getenv('HOST', '0.0.0.0'),
        port=int(os.getenv('PORT', 5000)),
        debug=os.getenv('FLASK_ENV') == 'development'
    )