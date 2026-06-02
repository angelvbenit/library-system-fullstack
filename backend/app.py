from flask import Flask
from flask_cors import CORS
from routes.books import books_bp
from routes.members import members_bp
from routes.loans import loans_bp
from routes.fines import fines_bp
from routes.reservations import reservations_bp

app = Flask(__name__)
CORS(app)

# Register blueprints
app.register_blueprint(books_bp, url_prefix='/api/books')
app.register_blueprint(members_bp, url_prefix='/api/members')
app.register_blueprint(loans_bp, url_prefix='/api/loans')
app.register_blueprint(fines_bp, url_prefix='/api/fines')
app.register_blueprint(reservations_bp, url_prefix='/api/reservations')

@app.route('/api/health')
def health():
    return {'status': 'ok', 'message': 'Library API is running'}

if __name__ == '__main__':
    app.run(debug=True, port=5000)