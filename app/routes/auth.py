from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from ..utils.api_client import PaperlessAPIClient
from ..config import Config

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    if 'token' in session:
        return f"¡Sesión iniciada! Token: {session['token']}"
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    api_client = PaperlessAPIClient(Config.PAPERLESS_API_URL)

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('El nombre de usuario y la contraseña son obligatorios.', 'error')
            return redirect(url_for('auth.login'))

        token = api_client.get_token(username, password)
        if token:
            session['token'] = token
            session['username'] = username
            flash('¡Inicio de sesión exitoso!', 'success')
            return redirect(url_for('auth.index'))
        else:
            flash('Nombre de usuario o contraseña incorrectos.', 'error')

        return redirect(url_for('auth.login'))

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.pop('token', None)
    session.pop('username', None)
    flash('¡Sesión cerrada exitosamente!', 'success')
    return redirect(url_for('auth.login'))

