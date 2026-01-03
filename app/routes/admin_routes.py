"""Admin routes blueprint"""
from flask import Blueprint, jsonify

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin', methods=['GET'])
def admin_dashboard():
    return jsonify({'message': 'Admin dashboard'}), 200
