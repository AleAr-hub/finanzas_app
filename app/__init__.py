from flask import Flask
from config import Config
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Mail

app = Flask(__name__)  # en app se encuentra nuestro servidor web de Flask
app.config.from_object(Config)
bcrypt = Bcrypt(app)  # Creo una instancia de bcrypt para luego poder hashear las contraseñas del usuario
login_manager = LoginManager(app)
login_manager.login_view = 'inicio'  # Redirige a la vista 'inicio' si el usuario no está autenticado
login_manager.login_message = 'Debes iniciar para acceder a esta pagina'  # Mensaje que aparece cuando se redirige al usuario
login_manager.login_message_category = 'danger'

s = URLSafeTimedSerializer(app.config['SECRET_KEY'])

mail = Mail(app)

from app import routes
