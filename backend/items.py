from flask import Blueprint, jsonify, request
import uuid
from db import get_db

items = Blueprint("items", __name__)
ALLOWED = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}


@items.get("/items")
def list_items():
    search = request.args.get("search", "").strip().casefold()
    result = (
        get_db()
        .table("items")
        .select("*")
        .order("created_at", desc=True)
        .limit(100)
        .execute()
    )
    rows = result.data or []
    if search:
        fields = ("title", "description", "category", "location")
        rows = [
            row
            for row in rows
            if any(search in str(row.get(field, "")).casefold() for field in fields)
        ]
    return jsonify(rows)


@items.get("/items/<item_id>")
def get_item(item_id):
    result = (
        get_db()
        .table("items")
        .select("*")
        .eq("id", item_id)
        .limit(1)
        .execute()
    )
    if not result.data:
        return jsonify({"error": "Item not found"}), 404
    return jsonify(result.data[0])


@items.post("/items")
def report_item():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be valid JSON."}), 400

    required = ("title", "description", "category",
                "location", "type", "contact")
    values = {key: str(data.get(key, "")).strip() for key in required}
    missing = [key for key, value in values.items() if not value]
    if missing:
        return jsonify({"error": f"Required fields: {', '.join(missing)}"}), 400
    if values["type"] not in ("lost", "found"):
        return jsonify({"error": "Type must be 'lost' or 'found'."}), 400

    result = (
        get_db()
        .table("items")
        .insert(
            {
                **values,
                "image_url": str(data.get("image_url", "")).strip() or None,
                "phone": str(data.get("phone", "")).strip()[:15] or None,
                "status": "open",
            }
        )
        .execute()
    )
    if not result.data:
        return jsonify({"error": "The item report could not be saved."}), 502
    return jsonify(result.data[0]), 201


@items.post("/upload")
def upload_image():
    file = request.files.get("image")
    if not file or file.mimetype not in ALLOWED:
        return jsonify({"error": "Upload a JPG, PNG or WebP image."}), 400
    data = file.read()
    if len(data) > 5 * 1024 * 1024:
        return jsonify({"error": "Image must be under 5 MB."}), 400
    path = f"{uuid.uuid4().hex}.{ALLOWED[file.mimetype]}"
    db = get_db()
    db.storage.from_("item-images").upload(path, data,
                                           {"content-type": file.mimetype})
    return jsonify({"url": db.storage.from_("item-images").get_public_url(path)}), 201
