from flask import Blueprint, render_template, redirect, url_for, flash, session, request, current_app
from flask_login import login_required, current_user
from functools import wraps
from ..utils.api_client import PaperlessAPIClient
from ..config import Config
import requests
import datetime
from dateutil.parser import parse as parse_date

documents_bp = Blueprint('documents', __name__)

def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_superuser:
            flash('Acceso denegado. Se requiere ser administrador.', 'error')
            return redirect(url_for('documents.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# Cache para nombres de usuarios
user_cache = {}

def get_username(api_client, user_id, token):
    """Obtiene el nombre de usuario a partir del ID, usando cache."""
    if user_id in user_cache:
        return user_cache[user_id]
    try:
        headers = {'Authorization': f'Token {token}'}
        response = requests.get(f"{Config.PAPERLESS_API_URL}/users/{user_id}/", headers=headers, timeout=5)
        if response.status_code == 200:
            username = response.json().get('username', 'Desconocido')
            user_cache[user_id] = username
            return username
        else:
            current_app.logger.error(f"Error al obtener usuario {user_id}: {response.status_code}")
            return 'Desconocido'
    except requests.RequestException as e:
        current_app.logger.error(f"Error al conectar con la API para usuario {user_id}: {str(e)}")
        return 'Desconocido'

@documents_bp.route('/dashboard')
@login_required
def dashboard():
    api_client = PaperlessAPIClient(Config.PAPERLESS_API_URL)
    try:
        headers = {'Authorization': f'Token {session.get("token")}'}
        response = requests.get(f"{Config.PAPERLESS_API_URL}/documents/", headers=headers, timeout=5)
        tags_response = requests.get(f"{Config.PAPERLESS_API_URL}/tags/", headers=headers, timeout=5)
        if response.status_code == 200 and tags_response.status_code == 200:
            documents = response.json().get('results', [])
            tags = tags_response.json().get('results', [])
            # Crear un diccionario para mapear IDs de etiquetas a nombres
            tag_map = {tag['id']: tag['name'] for tag in tags}
            formatted_documents = []
            for doc in documents:
                try:
                    created_str = doc['created']
                    current_app.logger.debug(f"Fecha cruda de documento {doc['id']}: {created_str}")
                    try:
                        created = datetime.datetime.strptime(created_str, '%Y-%m-%dT%H:%M:%S%z')
                    except ValueError:
                        created = datetime.datetime.strptime(created_str, '%Y-%m-%d')
                    owner_id = doc.get('owner')
                    owner = get_username(api_client, owner_id, session.get('token')) if owner_id else 'Administrador'
                    # Mapear IDs de etiquetas a nombres
                    tag_ids = doc.get('tags', [])
                    current_app.logger.debug(f"Etiquetas crudas de documento {doc['id']}: {tag_ids}")
                    tag_names = [tag_map.get(tag_id, 'Desconocida') for tag_id in tag_ids]
                    formatted_documents.append({
                        'id': doc['id'],
                        'title': doc['title'],
                        'created': created.strftime('%d %b %Y'),
                        'tags': tag_names
                    })
                except (ValueError, KeyError) as e:
                    current_app.logger.error(f"Error al procesar documento {doc.get('id', 'desconocido')}: {str(e)}")
                    continue
            return render_template('dashboard.html', documents=formatted_documents, user=current_user)
        else:
            flash('Error al cargar documentos.', 'error')
    except requests.RequestException as e:
        flash(f'Error al conectar con la API: {str(e)}', 'error')
    return redirect(url_for('auth.login'))

@documents_bp.route('/admin')
@admin_required
def admin():
    api_client = PaperlessAPIClient(Config.PAPERLESS_API_URL)
    try:
        headers = {'Authorization': f'Token {session.get("token")}'}
        tag_id = request.args.get('tag')
        search_query = request.args.get('search')
        documents_url = f"{Config.PAPERLESS_API_URL}/documents/"
        if tag_id:
            documents_url += f"?tags__id={tag_id}"
        if search_query:
            documents_url += f"{'&' if tag_id else '?'}search={search_query}"
        response = requests.get(documents_url, headers=headers, timeout=5)
        tags_response = requests.get(f"{Config.PAPERLESS_API_URL}/tags/", headers=headers, timeout=5)
        if response.status_code == 200 and tags_response.status_code == 200:
            documents = response.json().get('results', [])
            tags = tags_response.json().get('results', [])
            # Crear un diccionario para mapear IDs de etiquetas a nombres
            tag_map = {tag['id']: tag['name'] for tag in tags}
            formatted_documents = []
            for doc in documents:
                try:
                    created_str = doc['created']
                    current_app.logger.debug(f"Fecha cruda de documento {doc['id']}: {created_str}")
                    try:
                        created = datetime.datetime.strptime(created_str, '%Y-%m-%dT%H:%M:%S%z')
                    except ValueError:
                        created = datetime.datetime.strptime(created_str, '%Y-%m-%d')
                    owner_id = doc.get('owner')
                    owner = get_username(api_client, owner_id, session.get('token')) if owner_id else 'Administrador'
                    # Mapear IDs de etiquetas a nombres
                    tag_ids = doc.get('tags', [])
                    current_app.logger.debug(f"Etiquetas crudas de documento {doc['id']}: {tag_ids}")
                    tag_names = [tag_map.get(tag_id, 'Desconocida') for tag_id in tag_ids]
                    formatted_documents.append({
                        'id': doc['id'],
                        'title': doc['title'],
                        'created': created.strftime('%d %b %Y'),
                        'pages': doc.get('page_count', 1),
                        'version': '1.0',  # Placeholder
                        'procedure': doc.get('notes', 'Sin procedimiento'),
                        'owner': owner,
                        'tags': tag_names
                    })
                except (ValueError, KeyError) as e:
                    current_app.logger.error(f"Error al procesar documento {doc.get('id', 'desconocido')}: {str(e)}")
                    continue
            return render_template('admin.html', documents=formatted_documents, tags=tags, user=current_user)
        else:
            flash('Error al cargar datos.', 'error')
    except requests.RequestException as e:
        flash(f'Error al conectar con la API: {str(e)}', 'error')
    return redirect(url_for('auth.login'))