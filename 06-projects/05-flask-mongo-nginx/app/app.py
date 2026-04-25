import os
from bson import ObjectId
from flask import Flask, jsonify, request, abort
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

app = Flask(__name__)

MONGO_URI = os.environ["MONGO_URI"]
client = MongoClient(MONGO_URI)
db = client.get_default_database()
books = db["books"]


def book_to_dict(doc):
    return {
        "id": str(doc["_id"]),
        "title": doc["title"],
        "author": doc["author"],
        "year": doc.get("year"),
    }


# ── Health ────────────────────────────────────────────────────────────────────

@app.route("/api/health")
def health():
    try:
        client.admin.command("ping")
        return jsonify({"status": "ok", "mongo": "connected"})
    except ConnectionFailure:
        return jsonify({"status": "error", "mongo": "unreachable"}), 503


# ── Books CRUD ────────────────────────────────────────────────────────────────

@app.route("/api/books")
def list_books():
    return jsonify([book_to_dict(b) for b in books.find()])


@app.route("/api/books/<book_id>")
def get_book(book_id):
    try:
        doc = books.find_one({"_id": ObjectId(book_id)})
    except Exception:
        abort(400, description="Invalid ID format")
    if not doc:
        abort(404, description="Book not found")
    return jsonify(book_to_dict(doc))


@app.route("/api/books", methods=["POST"])
def create_book():
    data = request.get_json(silent=True) or {}
    if not data.get("title") or not data.get("author"):
        abort(400, description="title and author are required")
    doc = {
        "title": data["title"],
        "author": data["author"],
        "year": data.get("year"),
    }
    result = books.insert_one(doc)
    doc["_id"] = result.inserted_id
    return jsonify(book_to_dict(doc)), 201


@app.route("/api/books/<book_id>", methods=["DELETE"])
def delete_book(book_id):
    try:
        result = books.delete_one({"_id": ObjectId(book_id)})
    except Exception:
        abort(400, description="Invalid ID format")
    if result.deleted_count == 0:
        abort(404, description="Book not found")
    return jsonify({"deleted": book_id})


# ── Error handlers ────────────────────────────────────────────────────────────

@app.errorhandler(400)
@app.errorhandler(404)
@app.errorhandler(503)
def handle_error(e):
    return jsonify({"error": str(e.description)}), e.code


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
