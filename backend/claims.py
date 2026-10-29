from flask import Blueprint, g, jsonify, request

from db import get_db, require_user

claims = Blueprint("claims", __name__)


@claims.post("/items/<item_id>/claims")
@require_user
def submit_claim(item_id):
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be valid JSON."}), 400
    name = str(data.get("claimant_name", "")).strip()
    message = str(data.get("message", "")).strip()[:1000]
    if not name or not message:
        return jsonify({"error": "Name and answer are required."}), 400

    db = get_db()
    found = db.table("items").select("id,user_id,type,status").eq(
        "id", item_id).limit(1).execute()
    if not found.data:
        return jsonify({"error": "Item not found"}), 404
    item = found.data[0]
    if item["type"] != "found":
        return jsonify({"error": "Only found items can be claimed."}), 400
    if item["status"] != "open":
        return jsonify({"error": "This item is no longer open."}), 400
    if item.get("user_id") == g.user.id:
        return jsonify({"error": "You can't claim your own report."}), 400
    dup = db.table("claims").select("id").eq("item_id", item_id).eq(
        "claimant_id", g.user.id).limit(1).execute()
    if dup.data:
        return jsonify({"error": "You already claimed this item."}), 409

    result = db.table("claims").insert({
        "item_id": item_id, "claimant_id": g.user.id, "claimant_name": name,
        "claimant_email": g.user.email, "message": message, "status": "pending",
    }).execute()
    if not result.data:
        return jsonify({"error": "The claim could not be submitted."}), 502
    return jsonify(result.data[0]), 201


@claims.get("/items/<item_id>/claims")
@require_user
def list_claims(item_id):
    db = get_db()
    item = db.table("items").select("user_id").eq(
        "id", item_id).limit(1).execute()
    if not item.data:
        return jsonify({"error": "Item not found"}), 404
    if item.data[0].get("user_id") != g.user.id:
        return jsonify({"error": "Not your report."}), 403
    rows = db.table("claims").select("*").eq("item_id",
                                             item_id).order("created_at", desc=True).execute()
    return jsonify(rows.data or [])


@claims.post("/claims/<claim_id>/<action>")
@require_user
def decide_claim(claim_id, action):
    if action not in ("approve", "reject"):
        return jsonify({"error": "Not found"}), 404
    db = get_db()
    found = db.table("claims").select("id,item_id,status").eq(
        "id", claim_id).limit(1).execute()
    if not found.data:
        return jsonify({"error": "Claim not found"}), 404
    claim = found.data[0]
    item = db.table("items").select("user_id").eq(
        "id", claim["item_id"]).limit(1).execute()
    if not item.data or item.data[0].get("user_id") != g.user.id:
        return jsonify({"error": "Not your report."}), 403
    if claim["status"] != "pending":
        return jsonify({"error": "This claim was already decided."}), 409

    status = "approved" if action == "approve" else "rejected"
    db.table("claims").update({"status": status}).eq("id", claim_id).execute()
    if action == "approve":
        db.table("items").update({"status": "claimed"}).eq(
            "id", claim["item_id"]).execute()
    return jsonify({"status": status})
