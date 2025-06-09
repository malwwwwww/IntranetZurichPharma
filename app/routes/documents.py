from flask import Blueprint, render_template, session, redirect, url_for

documents_bp = Blueprint('documents', __name__)

@documents_bp.route('/documents')
def list_documents():
    if 'token' not in session:
        return redirect(url_for('auth.login'))
    return "Lista de documentos (funcionalidad por implementar)"