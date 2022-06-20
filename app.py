from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from xmlrpc import client as xmlrpclib
import base64


from xmlrpc import client

# Kadour boubou
# from ldap3 import Server, Connection
# import base64

# WELCOMe ACHRAF
# pipi
app = Flask(__name__,static_folder='./images',)

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

# url = "http://10.20.10.42:8069"
# dbo = "hasnaoui"
# username = "admin"
# password = "4g$1040"

url = "http://10.10.10.26:4550"
dbo = "hasnaoui"
username = "SOUHEIL.HADJHABIB@GROUPE-HASNAOUI.COM"
password = "Machen220-714"

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

coco = 0

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


def get_centre_de_cout(centre_de_cout_id):

    centre_de_cout = models.execute_kw(
        dbo,
        uid,
        password,
        "asset.center.cout",
        "search_read",
        [[["id", "=", centre_de_cout_id]]],
        {"fields": ["name"]},
    )
    return centre_de_cout


def get_location(affectation_id):
    location = models.execute_kw(
        dbo,
        uid,
        password,
        "account.asset.affectation",
        "search_read",
        [[["id", "=", affectation_id]]],
        {"fields": ["name"]},
    )
    location[0]["name"]


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



def save_image(id):
    asset_image = models.execute_kw(
            dbo,
            uid,
            password,
            "account.asset.asset",
            "search_read",
            [[["id", "=", id]]],
            {
                "fields": [
                    "num_serie",
                    "image_small"
                ]
            },
        )
    image_name = asset_image[0]["num_serie"]
    if asset_image[0]["image_small"]!=False:
        open(f"images/{image_name}.jpg",
                    "wb").write(base64.decodebytes(bytes(asset_image[0]["image_small"],encoding='utf8')))
        return image_name
    else:
        return ""


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
                    "affectation_id",
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
                    "quality",
                    "quantite",
                    "center_cout_id",
                    "affectation_id",
                    "category_id",
                    "employee_affected_id",
                ]
            },
        )
    if(len(asset)>0):

        if asset[0]["employee_affected_id"] == False:
            asset[0]["employee_affected_id"] = []
        if asset[0]["affectation_id"] == False:
            asset[0]["affectation_id"] = []
        if asset[0]["center_cout_id"] == False:
            asset[0]["center_cout_id"] = []
        else:
            asset[0]["centre_de_cout"] = get_centre_de_cout(asset[0]["center_cout_id"][0])[
                0
            ]["name"]


        try:
            asset[0]["location"] = get_location(asset[0]["affectation_id"][0])[0]["name"]
        except:
            asset[0]["location"] = ""

    
   
    # asset[0]["image"] = save_image(id) +".jpg"
    
        return asset[0]
    else:
        return "Nothing Found"


def get_resource(resource_id):
    args = request.args
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


def save_affectation_data(data):
    for i in range(0, len(data)):
        models.execute_kw(
            dbo,
            uid,
            password,
            "account.asset.inventory.line.checklist",
            "write",
            [
                data[i]["id"],
                {
                    "checked": data[i]["checked"],
                    "comment": data[i]["comment"],
                    "name": data[i]["text"],
                },
            ],
        )


# Bring inventories that are open
@app.route("/get_inventaire")
def get_inventaire():
    inventaire = models.execute_kw(
        dbo,
        uid,
        password,
        "account.asset.inventory",
        "search_read",
        [[["state", "=", "open"]]],
        {"fields": ["id", "name", "date_start", "state"]},
    )

    return jsonify(inventaire=inventaire)


# get assets that belongs to that inventory
@app.route("/get_inventaire_ligne")
def get_inventaire_line():
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
            ]
        ],
        {
            "fields": ["id", "comment", "asset_id", "quality", "state", "date"],
        },
    )

    print(inventory_line)
    if(len(inventory_line)>0):
        for i in range(0, len(inventory_line)):
            inventory_line[i]["data"] = get_asset_detail(
                inventory_line[i]["asset_id"][0], None
            )

    return jsonify(inv_line=inventory_line)


@app.route("/get_asset_qr_code")
def get_asset_qr_code():
    args = request.args
    asset = []
    asset.append(get_asset_detail(None, args["qr_code"]))
    return jsonify(asset=asset)


@app.route("/get_user_affectated_to")
def get_user_affected_to():
    employee_id = request.args
    affected_to = models.execute_kw(
        dbo,
        uid,
        password,
        "hr.employee",
        "search_read",
        [[["id", "=", int(employee_id["employee_affected_to"])]]],
        {"fields": ["name_related", "matricule", "firstname", "resource_id"]},
    )
    if len(affected_to) > 0:
        affected_to[0]["societe"] = get_resource(affected_to[0]["resource_id"][0])
    return jsonify(affected_to=affected_to)


@app.route("/save_asset_asset_line", methods=["GET", "POST"])
def save_asset_inventory_line():
    data = request.get_json(force=True)
   
    id = models.execute_kw(
        dbo,
        uid,
        password,
        "account.asset.inventory.line",
        "write",
        [
            data["id"],
            {
                "comment": data["comment"],
                "quality": data["quality"],
                "state": "done",
                "date": data["date"],
            }
        ],
    )
    
    if data['image1']!=None and data['image1']!='': 
        image_importe(data['image1'],data["name"],data["id"])
    if data['image2']!=None and data['image2']!='':
        print(data['image2'])
        image_importe(data['image2'],data["name"],data["id"])
    if data['image3']!=None and data['image3']!='':
        print(data['image3'])
        image_importe(data['image3'],data["name"],data["id"])
    

    if(len(data["data"])>0):
        save_affectation_data(data["data"])

    return jsonify(message="id")

@app.route("/save_asset_asset_line_exist_not", methods=["GET", "POST"])
def save_asset_inventory_line_exist_not():
    data = request.get_json(force=True)
    id = models.execute_kw(
        dbo,
        uid,
        password,
        "account.asset.inventory.line",
        "create",
        [
            {
                "comment": data["comment"],
                "quality": "new",
                "asset_id": int(data["asset_id"]),
                "state": "done",
                "inventory_id": int(data["inventory_id"]),
                "date": data["date"],
            }
        ],
    )

    if data['image1']!=None and data['image1']!='': 
        image_importe(data['image1'],data["name"],data["id"])
    if data['image2']!=None and data['image2']!='':
        print(data['image2'])
        image_importe(data['image2'],data["name"],data["id"])
    if data['image3']!=None and data['image3']!='':
        print(data['image3'])
        image_importe(data['image3'],data["name"],data["id"])

    if(len(data["data"])>0):
        save_affectation_data(data["data"])

    return jsonify(message="id")



@app.route("/check_list")
def check_list():
    inventory_line_id = request.args
    check_list_detail = models.execute_kw(
        dbo,
        uid,
        password,
        "account.asset.inventory.line.checklist",
        "search_read",
        [[["inventory_line_id", "=", int(inventory_line_id["inventory_line_id"])]]],
        {"fields": ["name", "checked", "comment"]},
    )
    return jsonify(response=check_list_detail)

def create_ir_attachement(image,asset_name):
    file_name = asset_name
    id = models.execute_kw(
        dbo,
        uid,
        password,
        "ir.attachment",
        "create",
        [
            {
                "name": file_name,
                "type": "binary",
                "datas": image,
                "datas_fname": file_name + ".jpeg",
                "store_fname": file_name,
                "res_model": "account.asset.inventory.line.image",
                "mimetype":"image/jpeg", 
            }
        ],
    )
    return id

def create_inventory_line_image(id_ire_attachement,inventory_line_id):
    print('create_inventory_line_image ',id_ire_attachement)
    id = models.execute_kw(
        dbo,
        uid,
        password,
        "account.asset.inventory.line.image",
        "create",
        [
            {
                "attachment_id": id_ire_attachement,
                "inventory_line_id": inventory_line_id,
            }
        ],
    )
    return id

def update_ir_attachment(id_ire_attachement,res_id):
    print("update_ir_attachment" ,id_ire_attachement," ", res_id)
    id = models.execute_kw(
        dbo,
        uid,
        password,
        "ir.attachment",
        "write",
        [
            [id_ire_attachement],

            {
                "res_id": res_id,
            }
        ],
    )
    return id


# @app.route("/add_image", methods=["POST"])
def image_importe(image,asset_name,inventory_line_id):
    id_ire_attachement = create_ir_attachement(image,asset_name)
    id_inv_line_image = create_inventory_line_image(id_ire_attachement,inventory_line_id)
    id = update_ir_attachment(id_ire_attachement,id_inv_line_image)
    
    
    # return jsonify(id)
    return jsonify(id)

@app.route("/get_ir")
def get_ir_attachement():
    attachment = models.execute_kw(dbo, uid, password,
    'ir.attachment', 'search_read',
    [[['id', '=', 441143], ]],
    {'limit': 5})
    return jsonify(attachment)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
