"""
Jorge Mario Camargo Pérez
alver alberto diaz orejarena
"""

import json
import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash

# Configuración de logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Constantes
INVENTORY_FILE = "inventario.json"
SECRET_KEY = "inventario-secreto"

# Inicialización Flask
app = Flask(__name__)
app.secret_key = SECRET_KEY


class InventoryManager:
    def __init__(self, file_path=INVENTORY_FILE):
        self.file_path = file_path
        self.inventory = self.load()

    def load(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                logging.warning("Archivo dañado o no encontrado. Iniciando inventario vacío.")
        return []

    def save(self):
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self.inventory, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Error al guardar inventario: {e}")

    def add_product(self, product_id: str, name: str, price: float, stock: int):
        # Validaciones
        if any(p["id"] == product_id for p in self.inventory):
            raise ValueError("Ya existe un producto con ese ID.")
        elif any(p["nombre"].lower() == name.lower() for p in self.inventory):
            raise ValueError("Ya existe un producto con ese nombre en el inventario.")
        elif not name.strip():
            raise ValueError("El nombre del producto no puede estar vacío.")
        elif price < 0:
            raise ValueError("El precio no puede ser negativo.")
        elif stock < 0:
            raise ValueError("El stock no puede ser negativo.")

        # Si todo pasa, se guarda
        product = {"id": product_id, "nombre": name, "precio": price, "stock": stock}
        self.inventory.append(product)
        self.save()

    def delete_product(self, product_id: str):
        self.inventory = [p for p in self.inventory if p["id"] != product_id]
        self.save()

    def update_stock(self, product_id: str, new_stock: int):
        for product in self.inventory:
            if product["id"] == product_id:
                product["stock"] = new_stock
                self.save()
                return
        raise KeyError("Producto no encontrado.")



inventory_manager = InventoryManager()


@app.route("/")
def index():
    return render_template("index.html", inventory=inventory_manager.inventory)


@app.route("/add", methods=["POST"])
def add_product():
    product_id = request.form["id"].strip()
    name = request.form["nombre"].strip()

    try:
        # Validamos primero como string
        price_str = request.form["precio"].strip()
        if not price_str:
            raise ValueError("El precio del producto no puede estar vacío")
        price = float(price_str)

        stock_str = request.form["stock"].strip()
        if not stock_str:
            raise ValueError("El stock no puede estar vacío")
        stock = int(stock_str)

        inventory_manager.add_product(product_id, name, price, stock)
        flash(" Producto agregado con éxito.")
    except ValueError as e:
        flash(f"⚠ {e}")

    return redirect(url_for("index"))


@app.route("/delete/<product_id>")
def delete_product(product_id):
    inventory_manager.delete_product(product_id)
    flash(" Producto eliminado con éxito.")
    return redirect(url_for("index"))


@app.route("/update/<product_id>", methods=["POST"])
def update_stock(product_id):
    try:
        new_stock = int(request.form["stock"])
        inventory_manager.update_stock(product_id, new_stock)
        flash(" Stock actualizado con éxito.")
    except ValueError:
        flash("⚠ El stock debe ser un número entero.")
    except KeyError as e:
        flash(f"⚠ {e}")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
