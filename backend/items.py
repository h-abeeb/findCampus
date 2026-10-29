import uuid

from flask import Blueprint, jsonify, request, g

from db import current_user, get_db, require_user
from matching import find_matches

items = Blueprint("items", __name__)
ALLOWED = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}


@items.get("/items")
def list_items():
    search = request.args.get("search", "").strip().casefold()
    result = get_db().table("items").select(
        "*").order("created_at", desc=True).limit(100).execute()
    rows = result.data or []
    if search:
        fields = ("title", "description", "category", "location")
        rows = [r for r in rows if any(search in str(
            r.get(f, "")).casefold() for f in fields)]
    for r in rows:
        r.pop("contact", None)
        r.pop("phone", None)
    return jsonify(rows)


@items.get("/items/<item_id>")
def get_item(item_id):
    result = get_db().table("items").select(
        "*").eq("id", item_id).limit(1).execute()
    if not result.data:
        return jsonify({"error": "Item not found"}), 404
    item = result.data[0]
    user = current_user()
    owner = bool(user and item.get("user_id") == user.id)
    approved = False
    if user and not owner:
        ok = (get_db().table("claims").select("id").eq("item_id", item_id)
              .eq("claimant_id", user.id).eq("status", "approved").limit(1).execute())
        approved = bool(ok.data)
    if item["type"] == "found" and not (owner or approved):
        item.pop("contact", None)
        item.pop("phone", None)
    return jsonify(item)


@items.get("/items/<item_id>/matches")
def get_matches(item_id):
    db = get_db()
    result = db.table("items").select(
        "id,title,description,category,location,type"
    ).eq("id", item_id).limit(1).execute()
    if not result.data:
        return jsonify({"error": "Item not found"}), 404

    item = result.data[0]
    opposite_type = "lost" if item["type"] == "found" else "found"
    rows = db.table("items").select(
        "id,title,description,category,location,type,status"
    ).eq("type", opposite_type).eq("status", "open").limit(200).execute()
    return jsonify(find_matches(item, rows.data or []))


@items.post("/items")
@require_user
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
    question = str(data.get("verification_question", "")).strip()[:200]
    if values["type"] == "found" and not question:
        return jsonify({"error": "Add a verification question for found items."}), 400

    result = (
        get_db().table("items")
        .insert({
            **values,
            "image_url": str(data.get("image_url", "")).strip() or None,
            "phone": str(data.get("phone", "")).strip()[:15] or None,
            "verification_question": question or None,
            "user_id": g.user.id,
            "status": "open",
        })
        .execute()
    )
    if not result.data:
        return jsonify({"error": "The item report could not be saved."}), 502
    return jsonify(result.data[0]), 201


@items.post("/upload")
@require_user
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


@items.delete("/items/<item_id>")
@require_user
def delete_item(item_id):
    db = get_db()
    result = db.table("items").select("user_id,image_url").eq(
        "id", item_id).limit(1).execute()
    if not result.data:
        return jsonify({"error": "Item not found"}), 404
    item = result.data[0]
    if item.get("user_id") != g.user.id:
        return jsonify({"error": "You can only delete your own reports."}), 403
    db.table("items").delete().eq("id", item_id).execute()
    if item.get("image_url"):
        try:
            db.storage.from_(
                "item-images").remove([item["image_url"].split("?")[0].rsplit("/", 1)[-1]])
        except Exception:
            pass
    return jsonify({"deleted": True})


@items.get("/my/items")
@require_user
def my_items():
    rows = get_db().table("items").select("*").eq(
        "user_id", g.user.id).order("created_at", desc=True).execute()
    return jsonify(rows.data or [])
