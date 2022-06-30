from ast import arg
from flask import Flask, request, jsonify
import threading
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

url = "http://10.10.10.123:8069"
dbo = "CRF_EL_MORDJANE_DEMO_2"
username = "admin"
password = "odoo1234"
models = xmlrpclib.ServerProxy("{}/xmlrpc/2/object".format(url))
common = xmlrpclib.ServerProxy("{}/xmlrpc/2/common".format(url))
uid = common.authenticate(dbo, username, password, {})


# Bring inventories that are open
@app.route("/test")
def get_inventaire_odoo14():

    asset_image = models.execute_kw(
                dbo,
                uid,
                password,
                "ir.attachment",
                 "search_read",
                [[["res_id","=",2],
                ["res_field","!=",False],
                "|",["res_field","=","image"],["res_field","=","image2"],
                ["res_model","=","account.asset.asset"]]], {"fields": ["name"]},
                
            )

    return jsonify(asset_image=asset_image)


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
        "account.asset.asset.affectation",
        "search_read",
        [[["id", "=", affectation_id]]],
        {"fields": ["name"]},
    )
    
    return location[0]["name"]


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


def safe_open_w(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return open(path, 'wb')


def decode_image(image,folder_path,image_name,champ,code):
    with safe_open_w(f"images/{folder_path}/{code}/{image_name}{champ}.jpg") as f:
        f.write(base64.decodebytes(bytes(image,encoding='utf8')))
    

def save_image(id,code_asset):
    url_save_image = "http://10.10.10.123:8069"
    db_save_image = "CRF_EL_MORDJANE_DEMO_2"
    username_save_image = "admin"
    password_save_image = "odoo1234"
    models_save_image = xmlrpclib.ServerProxy("{}/xmlrpc/2/object".format(url_save_image))
    common_save_image = xmlrpclib.ServerProxy("{}/xmlrpc/2/common".format(url_save_image))
    uid_save_image = common_save_image.authenticate(db_save_image, username_save_image, password_save_image, {})


    
    
    
    asset_image = models_save_image.execute_kw(
                db_save_image,
                uid_save_image,
                password_save_image,
                "ir.attachment",
                 "search_read",
                [[["res_id","=",id],
                ["res_field","!=",False],
                "|",["res_field","=","image"],["res_field","=","image2"],
                ["res_model","=","account.asset.asset"]]], {"fields": ["datas"]},
            )

    
    
    image_name =str(id)
    code = code_asset.replace("/","")
    if(len(asset_image)>0):
        for i in range(0,len(asset_image)):
             decode_image(asset_image[i]["datas"],'image_produit',image_name,"image"+str(i+1),code)
       

def get_asset_detail(id,qr_code=None):
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
                    "serial",
                    "quantity",
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
                    "serial",
                    "quantity",
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
        
        
        try:
            asset[0]["location"] =  get_location(asset[0]["affectation_id"][0])
        except:
            asset[0]["location"] = ""



        if id is not None:
            c = threading.Thread(target=save_image,args=(id,asset[0]["code"]))
            c.start()
        else:
            c = threading.Thread(target=save_image,args=(asset[0]["id"],asset[0]["code"]))
            c.start()
        
    
        return asset[0]
    else:
        return "Nothing Found"


def get_resource(resource_id):
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


def save_affectation_data(data,idl):
    url_save_affectation = "http://10.10.10.123:8069"
    db_save_affectation = "CRF_EL_MORDJANE_DEMO_2"
    username_save_affectation = "admin"
    password_save_affectation = "odoo1234"
    models_save_affectation = xmlrpclib.ServerProxy("{}/xmlrpc/2/object".format(url_save_affectation))
    common_save_affectation = xmlrpclib.ServerProxy("{}/xmlrpc/2/common".format(url_save_affectation))
    uid_save_affectation = common_save_affectation.authenticate(db_save_affectation, username_save_affectation, password_save_affectation, {})
    if(idl is not None):
        for i in range(0, len(data)):
            models_save_affectation.execute_kw(
                db_save_affectation,
                uid_save_affectation,
                password_save_affectation,
                "account.asset.inventory.line.checklist",
                "create",
                [
                    {
                        "inventory_line_id":idl,
                        "checked": data[i]["checked"],
                        "comment": data[i]["comment"],
                        "name": data[i]["text"],
                    },
                ],
            )

    else:
        for i in range(0, len(data)):
            models_save_affectation.execute_kw(
                db_save_affectation,
                uid_save_affectation,
                password_save_affectation,
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

   
    if(len(inventory_line)>0):
        for i in range(0, len(inventory_line)):
            inventory_line[i]["data"] = get_asset_detail(
                inventory_line[i]["asset_id"][0],None
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
    print("date ",data["date"])
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
        x = threading.Thread(target=image_importe,args=(data['image1'],data["name"],data["id"],data['asset_id'],))
        x.start()
        x_image_saving = threading.Thread(target=decode_image,args=(data['image1'],
                                                                    'image_inventory',
                                                                    data["asset_id"],
                                                                    "image1",
                                                                    data["code"].replace("/",""),))
        x_image_saving.start()

    if data['image2']!=None and data['image2']!='':
        y = threading.Thread(target=image_importe,args=(data['image2'],data["name"],data["id"],data['asset_id'],))
        y.start()
        x_image2_saving = threading.Thread(target=decode_image,args=(data['image2'],
                                                                    'image_inventory',
                                                                    data["asset_id"],
                                                                    "image2",
                                                                    data["code"].replace("/",""),))
        x_image2_saving.start()
        
    if data['image3']!=None and data['image3']!='':
        # print(data['image3'])
        z = threading.Thread(target=image_importe,args=(data['image3'],data["name"],data["id"],data['asset_id'],))
        z.start()
        x_image3_saving = threading.Thread(target=decode_image,args=(data['image3'],
                                                                    'image_inventory',
                                                                    data["asset_id"],
                                                                    "image3",
                                                                    data["code"].replace("/",""),))
        x_image3_saving.start()


    if(len(data["data"])>0):
        a = threading.Thread(target=save_affectation_data,args=(data["data"],None,))
        a.start()
        

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
                "quality": data["quality"],
                "asset_id": int(data["asset_id"]),
                "state": "done",
                "inventory_id": int(data["inventory_id"]),
                "date": data["date"],
            }
        ],
    )

    if data['image1']!=None and data['image1']!='': 
        x = threading.Thread(target=image_importe,args=(data['image1'],data["name"],id,data['asset_id'],))
        x.start()
        x_image_saving = threading.Thread(target=decode_image,args=(data['image1'],
                                                                    'image_inventory',
                                                                    data["asset_id"],
                                                                    "image1",
                                                                    data["code"].replace("/",""),))
        x_image_saving.start()
       
    if data['image2']!=None and data['image2']!='':
        y = threading.Thread(target=image_importe,args=(data['image2'],data["name"],id,data['asset_id'],))
        y.start()
        x_image2_saving = threading.Thread(target=decode_image,args=(data['image2'],
                                                                    'image_inventory',
                                                                    data["asset_id"],
                                                                    "image2",
                                                                    data["code"].replace("/",""),))
        x_image2_saving.start()

    if data['image3']!=None and data['image3']!='':
       
        z = threading.Thread(target=image_importe,args=(data['image3'],data["name"],id,data['asset_id'],))
        z.start()
        x_image3_saving = threading.Thread(target=decode_image,args=(data['image3'],
                                                                    'image_inventory',
                                                                    data["asset_id"],
                                                                    "image3",
                                                                    data["code"].replace("/",""),))
        x_image3_saving.start()

    if(len(data["data"])>0):
        a = threading.Thread(target=save_affectation_data,args=(data["data"],id,))
        a.start()


    return jsonify(message=id)


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


def create_ir_attachement(image,asset_name,res_id):
    url_create_ir_attachement = "http://10.10.10.123:8069"
    db_create_ir_attachement = "CRF_EL_MORDJANE_DEMO_2"
    username_ir_attachement = "admin"
    password_ir_attachement = "odoo1234"
    models_ir_attachement = xmlrpclib.ServerProxy("{}/xmlrpc/2/object".format(url_create_ir_attachement))
    common_ir_attachement = xmlrpclib.ServerProxy("{}/xmlrpc/2/common".format(url_create_ir_attachement))
    uid_ir_attachement = common_ir_attachement.authenticate(db_create_ir_attachement, username_ir_attachement, password_ir_attachement, {})
    file_name = asset_name
    id = models_ir_attachement.execute_kw(
        db_create_ir_attachement,
        uid_ir_attachement,
        password_ir_attachement,
        "ir.attachment",
        "create",
        [
            {
                "name": file_name,
                "type": "binary",
                "datas": image,
                "res_id":res_id,
                "store_fname": file_name,
                "res_field":"image",
                "res_model": "account.asset.inventory.line.image",
                "mimetype":"image/jpeg", 
            }
        ],
    )
    return id


def create_inventory_line_image(image,id_ire_attachement,inventory_line_id):
    url_create_inventory_line_image = "http://10.10.10.123:8069"
    db_create_inventory_line_image = "CRF_EL_MORDJANE_DEMO_2"
    username_create_inventory_line_image = "admin"
    password_create_inventory_line_image = "odoo1234"
    models_create_inventory_line_image = xmlrpclib.ServerProxy("{}/xmlrpc/2/object".format(url_create_inventory_line_image))
    common_create_inventory_line_image = xmlrpclib.ServerProxy("{}/xmlrpc/2/common".format(url_create_inventory_line_image))
    uid_create_inventory_line_image = common_create_inventory_line_image.authenticate(db_create_inventory_line_image, 
                                                                                    username_create_inventory_line_image,
                                                                                    password_create_inventory_line_image, {})
    id = models_create_inventory_line_image.execute_kw(
        db_create_inventory_line_image,
        uid_create_inventory_line_image,
        password_create_inventory_line_image,
        "account.asset.inventory.line.image",
        "create",
        [
            {
                "image_filename": str(id_ire_attachement)+".jpg",
                "inventory_line_id": inventory_line_id,
                "image_download":image,
                "image_128":image,
                "image":image,
                "has_image":True
            }
        ],
    )
    return id


def update_ir_attachment(id_ire_attachement,res_id):
    url_update_ir_attachment = "http://10.10.10.123:8069"
    db_update_ir_attachment = "CRF_EL_MORDJANE_DEMO_2"
    username_update_ir_attachment = "admin"
    password_update_ir_attachment = "odoo1234"
    models_update_ir_attachment = xmlrpclib.ServerProxy("{}/xmlrpc/2/object".format(url_update_ir_attachment))
    common_update_ir_attachment = xmlrpclib.ServerProxy("{}/xmlrpc/2/common".format(url_update_ir_attachment))
    uid_update_ir_attachment = common_update_ir_attachment.authenticate(db_update_ir_attachment, 
                                                                        username_update_ir_attachment, 
                                                                        password_update_ir_attachment, {})
    id = models_update_ir_attachment.execute_kw(
        db_update_ir_attachment,
        uid_update_ir_attachment,
        password_update_ir_attachment,
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
def image_importe(image,asset_name,inventory_line_id,res_id):
    id_ire_attachement = create_ir_attachement(image,asset_name,res_id)
    id_inv_line_image = create_inventory_line_image(image,id_ire_attachement,inventory_line_id)
    # update_ir_attachment(id_ire_attachement,id_inv_line_image)

@app.route("/get_ir")
def get_ir_attachement():
    attachment = models.execute_kw(dbo, uid, password,
    'ir.attachment', 'search_read',
    [[['id', '=', 441143], ]],
    {'limit': 5})
    return jsonify(attachment)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
