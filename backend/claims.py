import hmac
import os

from flask import Blueprint, jsonify, request

from db import get_db

claims = Blueprint("claims", __name__)


@claims.post("/items/<item_id>/claims")
def submit_claim(item_id):
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be valid JSON."}), 400

    required = ("claimant_name", "claimant_email", "message")
    values = {key: str(data.get(key, "")).strip() for key in required}
    missing = [key for key, value in values.items() if not value]
    if missing:
        return jsonify({"error": f"Required fields: {', '.join(missing)}"}), 400

    item = (
        get_db()
        .table("items")
        .select("id")
        .eq("id", item_id)
        .limit(1)
        .execute()
    )
    if not item.data:
        return jsonify({"error": "Item not found"}), 404

    result = (
        get_db()
        .table("claims")
        .insert({**values, "item_id": item_id, "status": "pending"})
        .execute()
    )
    if not result.data:
        return jsonify({"error": "The claim could not be submitted."}), 502
    return jsonify(result.data[0]), 201


@claims.post("/claims/<claim_id>/approve")
def approve_claim(claim_id):
    admin_token = os.environ.get("ADMIN_TOKEN")
    supplied_token = request.headers.get("X-Admin-Token", "")
    if not admin_token:
        return jsonify({"error": "Claim approval is not configured."}), 503
    if not supplied_token or not hmac.compare_digest(supplied_token, admin_token):
        return jsonify({"error": "Admin authorization required."}), 401

    result = (
        get_db()
        .table("claims")
        .update({"status": "approved"})
        .eq("id", claim_id)
        .eq("status", "pending")
        .execute()
    )
    if not result.data:
        return jsonify({"error": "Pending claim not found."}), 404
    return jsonify(result.data[0])
