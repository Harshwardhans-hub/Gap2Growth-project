"""Student routes blueprint"""
from flask import Blueprint, jsonify

student_bp = Blueprint('student', __name__)

@student_bp.route('/students', methods=['GET'])
def list_students():
    return jsonify({'students': []}), 200
