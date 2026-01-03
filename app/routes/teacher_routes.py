"""Teacher routes blueprint"""
from flask import Blueprint, jsonify

teacher_bp = Blueprint('teacher', __name__)

@teacher_bp.route('/teachers', methods=['GET'])
def list_teachers():
    return jsonify({'teachers': []}), 200
