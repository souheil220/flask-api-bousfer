# odoo
from email import message
from flask import Flask, request, jsonify
import os
from flask_pymongo import PyMongo
from flask_odoo import Odoo

from xmlrpc import client as xmlrpclib


from xmlrpc import client
#Kadour boubou
# from ldap3 import Server, Connection
# import base64

# WELCOMe ACHRAF
# pipi
app = Flask(__name__)

# Souhil kteb


# app.config["MONGO_URI"] = (
#     "mongodb://"
#     + os.environ.get("MONGODB_USERNAME")
#     + ":"
#     + os.environ.get("MONGODB_PASSWORD")
#     + "@"
#     + os.environ.get("MONGODB_HOSTNAME")
#     + ":27017/"
#     + os.environ.get("MONGODB_DATABASE")
#     + "?authSource=admin"
# )

url = "http://10.20.10.42:8069"
dbo = "hasnaoui"
username = "admin"
password = "4g$1040"

# url = "http://10.10.10.122:8069"
# dbo = "MORDJANE"
# username = "mordjane"
# password = "123456"

# url = os.environ.get("ODOO_URL")
# dbo = os.environ.get("ODOO_DB")
# username = os.environ.get("ODOO_USERNAME")
# password = os.environ.get("ODOO_PASSWORD")

# app.config["ODOO_URL"] = url
# app.config["ODOO_DB"] = dbo
# app.config["ODOO_USERNAME"] = username
# app.config["ODOO_PASSWORD"] = password

# odoo = Odoo(app)

# mongo = PyMongo(app)

# db = mongo.db

srv = url
# # # srv = 'http://10.20.10.42:8069'
models = xmlrpclib.ServerProxy("{}/xmlrpc/2/object".format(url))
common = xmlrpclib.ServerProxy("{}/xmlrpc/2/common".format(url))
uid = common.authenticate(dbo, username, password, {})


# Bring inventories that are open
@app.route("/test")
def get_inventaire_odoo14():
    url = "http://10.1.12.205:8069"
    dbo = "MORDJANE"
    username = "admin"
    password = "odoo"
    models = xmlrpclib.ServerProxy("{}/xmlrpc/2/object".format(url))

    common = xmlrpclib.ServerProxy("{}/xmlrpc/2/common".format(url))
    uid = common.authenticate(dbo, username, password, {})
    # "id","=","104" should be replaced with "state","=","open"
    inventaire = models.execute_kw(
        dbo,
        uid,
        password,
        "account.asset",
        "search_read",
        [[["id", "=", 1]]],
    )

    return jsonify(inventaire=inventaire)


def get_location(centre_de_cout):
    location = models.execute_kw(
        dbo,
        uid,
        password,
        "asset.center.cout",
        "search_read",
        [[["id", "=", centre_de_cout]]],
        {"fields": ["name"]},
    )
    return location


def get_category(category_id):
    category = models.execute_kw(
        dbo,
        uid,
        password,
        "account.asset.category",
        "search_read",
        [[["id", "=", category_id]]],
        {"fields": ["name"]},
    )
    return category[0]["name"]


def get_asset_detail(id, qr_code=None):
    if qr_code is None:
        asset = models.execute_kw(
            dbo,
            uid,
            password,
            "account.asset.asset",
            "search_read",
            [[["id", "=", id]]],
            {
                "fields": [
                    "code",
                    "name",
                    "num_serie",
                    "quantite",
                    "center_cout_id",
                    "category_id",
                    "employee_affected_id",
                ]
            },
        )

    else:
        asset = models.execute_kw(
            dbo,
            uid,
            password,
            "account.asset.asset",
            "search_read",
            [[["code", "=", qr_code]]],
            {
                "fields": [
                    "code",
                    "name",
                    "num_serie",
                    "quantite",
                    "center_cout_id",
                    "category_id",
                    "employee_affected_id",
                ]
            },
        )
    asset[0]["location"] = get_location(asset[0]["center_cout_id"][0])[0]["name"]
    return asset[0]


def get_resource(resource_id):
    args = request.args
    print(args)
    inventaire = models.execute_kw(
        dbo,
        uid,
        password,
        "resource.resource",
        "search_read",
        [[["id", "=", resource_id]]],
        {"fields": ["company_id"]},
    )

    return inventaire[0]["company_id"][1]


# Bring inventories that are open
@app.route("/get_inventaire")
def get_inventaire():
    # "id","=","104" should be replaced with "state","=","open"
    inventaire = models.execute_kw(
        dbo,
        uid,
        password,
        "account.asset.inventory",
        "search_read",
        [[["id", "=", 104]]],
        {"fields": ["id", "name", "date_start", "state"]},
    )

    return jsonify(inventaire=inventaire)


# get assets that belongs to that inventory
@app.route("/get_inventaire_ligne")
def get_inventaire_asset():
    args = request.args
    inventory_line = models.execute_kw(
        dbo,
        uid,
        password,
        "account.asset.inventory.line",
        "search_read",
        [
            [
                ["inventory_id", "=", int(args["inv_id"])],
                # ------------hadi zyada------------------
                ["asset_id", "=", 26165],
            ]
        ],
        # ----------------------------------------
        {
            "fields": ["id", "comment", "asset_id", "quality", "state", "date"],
            "limit": 10,
        },
    )

    for i in range(0, len(inventory_line)):
        inventory_line[i]["data"] = get_asset_detail(
            inventory_line[i]["asset_id"][0], None
        )

    return jsonify(inv_line=inventory_line)


def get_asset_image(id):
    asset = models.execute_kw(
        dbo,
        uid,
        password,
        "account.asset.asset",
        "search_read",
        [[["id", "=", id]]],
        {"fields": ["code", "name", "num_serie", "quantite", "center_cout_id"]},
    )
    asset[0]["location"] = get_location(asset[0]["center_cout_id"][0])[0]["name"]
    return asset[0]


@app.route("/get_asset_qr_code")
def get_asset_qr_code():
    args = request.args
    asset = get_asset_detail(None, args["qr_code"])
    return jsonify(asset=asset)


@app.route("/get_user_affectated_to")
def get_user_affected_to():
    employee_id = request.args
    print("-----------------", employee_id)
    affected_to = models.execute_kw(
        dbo,
        uid,
        password,
        "hr.employee",
        "search_read",
        [[["id", "=", int(employee_id["employee_affected_to"])]]],
        {"fields": ["name_related", "matricule", "firstname", "resource_id"]},
    )
    affected_to[0]["societe"] = get_resource(affected_to[0]["resource_id"][0])
    return jsonify(affected_to=affected_to)


# @app.route("/todo")
# def todo():
#     _todos = db.todo.find()

#     item = {}
#     data = []
#     for todo in _todos:
#         item = {"id": str(todo["_id"]), "todo": todo["todo"]}
#         data.append(item)

#     return jsonify(status=True, data=data)


# @app.route("/todo", methods=["POST"])
# def createTodo():
#     data = request.get_json(force=True)
#     item = {"todo": data["todo"]}
#     db.todo.insert_one(item)

#     return jsonify(status=True, message="To-do saved successfully!"), 201


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
