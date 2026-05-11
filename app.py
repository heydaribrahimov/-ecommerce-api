from flask import Flask, request, jsonify
import json, os

app = Flask(__name__)

# ──────────────────────────────────────────
# "База данных" — просто JSON-файл
# ──────────────────────────────────────────
DATA_FILE = "data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"products": [], "orders": []}
    with open(DATA_FILE) as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# Стартовые данные при первом запуске
if not os.path.exists(DATA_FILE):
    save_data({
        "products": [
            {"id": 1, "name": "Laptop", "price": 999.99, "stock": 10},
            {"id": 2, "name": "Mouse",  "price": 29.99,  "stock": 50}
        ],
        "orders": []
    })

# ──────────────────────────────────────────
# ENDPOINTS
# ──────────────────────────────────────────

# 1. GET /products — список всех товаров
@app.route("/products", methods=["GET"])
def get_products():
    data = load_data()
    return jsonify(data["products"]), 200

# 2. GET /products/<id> — один товар
@app.route("/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    data = load_data()
    product = next((p for p in data["products"] if p["id"] == product_id), None)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(product), 200

# 3. POST /products — добавить товар
@app.route("/products", methods=["POST"])
def add_product():
    data = load_data()
    body = request.get_json()
    new_id = max((p["id"] for p in data["products"]), default=0) + 1
    product = {
        "id": new_id,
        "name": body["name"],
        "price": body["price"],
        "stock": body.get("stock", 0)
    }
    data["products"].append(product)
    save_data(data)
    return jsonify(product), 201

# 4. POST /orders — создать заказ
@app.route("/orders", methods=["POST"])
def create_order():
    data = load_data()
    body = request.get_json()
    product = next((p for p in data["products"] if p["id"] == body["product_id"]), None)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    new_id = max((o["id"] for o in data["orders"]), default=0) + 1
    order = {
        "id": new_id,
        "product_id": body["product_id"],
        "product_name": product["name"],
        "quantity": body["quantity"],
        "total": product["price"] * body["quantity"],
        "status": "confirmed"
    }
    data["orders"].append(order)
    save_data(data)
    return jsonify(order), 201

# 5. GET /orders — список заказов
@app.route("/orders", methods=["GET"])
def get_orders():
    data = load_data()
    return jsonify(data["orders"]), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
