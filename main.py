from flask import Flask
from models import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///bancodedados.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "DSAF945JU43KJNFD0FI"

# Configurações importantes para a sessão
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hora
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = False  # True se usar HTTPS

db.init_app(app)

# Importar rotas DEPOIS de criar o app
from route import *

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)