
from flask import Blueprint, request, jsonify
from app.services.auth_service import verify_token

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["POST"])
def login():
    id_token = request.json.get("idToken")

    try:
        decoded = verify_token(id_token)
        return jsonify({
            "uid": decoded["uid"],
            "email": decoded["email"]
        })
    except Exception:
        return jsonify({"error": "Invalid Token"}), 401
