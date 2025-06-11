from flask import Blueprint, render_template, redirect, url_for, flash, session, current_app, request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from flask_login import login_user, logout_user, login_required
from ..utils.api_client import PaperlessAPIClient
from ..config import Config
from ..models import User

auth_bp = Blueprint('auth', __name__)

class LoginForm(FlaskForm):
    username = StringField('Nombre de usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar Sesión')

@auth_bp.route('/')
def index():
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    current_app.logger.debug(f"Acceso a /login, método: {request.method}")
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        current_app.logger.debug(f"Intento de login con usuario: {username}")
        api_client = PaperlessAPIClient(Config.PAPERLESS_API_URL)
        token = api_client.get_token(username, password)
        if token:
            current_app.logger.debug(f"Token obtenido: {token}")
            session['token'] = token
            user_info = api_client.get_user_info(token, username)
            if user_info:
                current_app.logger.debug(f"Información del usuario: {user_info}")
                user = User(user_info['id'], username, user_info.get('is_superuser', False))
                session['username'] = username
                session['is_superuser'] = user_info.get('is_superuser', False)
                login_user(user)
                flash('¡Inicio de sesión exitoso!', 'success')
                if user.is_superuser:
                    current_app.logger.debug("Redirigiendo a /admin")
                    return redirect(url_for('documents.admin'))
                current_app.logger.debug("Redirigiendo a /dashboard")
                return redirect(url_for('documents.dashboard'))
            else:
                current_app.logger.error("No se pudo obtener información del usuario")
                flash('Error al obtener información del usuario.', 'error')
        else:
            current_app.logger.error("Credenciales incorrectas o error en la API")
            flash('Nombre de usuario o contraseña incorrectos.', 'error')
    else:
        if request.method == 'POST':
            current_app.logger.debug(f"Formulario no válido: {form.errors}")
            flash('Error en el formulario. Por favor, verifica los datos.', 'error')
    return render_template('login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    session.pop('token', None)
    session.pop('username', None)
    session.pop('is_superuser', None)
    logout_user()
    flash('¡Sesión cerrada exitosamente!', 'success')
    return redirect(url_for('auth.login'))