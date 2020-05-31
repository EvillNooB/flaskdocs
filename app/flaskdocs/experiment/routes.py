import arrow
from flask import Blueprint, render_template, url_for, flash, redirect, current_app, make_response, Flask, abort, request, send_file
from flaskdocs.experiment.forms import AddProductForm
from flaskdocs.models import Products
import uuid
from flaskdocs import db
import qrcode
from io import BytesIO
from flaskdocs.experiment.utils import generate_qr

experiment = Blueprint("experiment", __name__)

@experiment.route("/products/add", methods=['POST', 'GET'])
def create_product():
    form = AddProductForm()
    if form.validate_on_submit():
        
        product = Products(product_name=form.product_name.data,
                           vendor=form.vendor.data)
        product.manufactured_date = arrow.get(form.manufactured_date.data, 'DD.MM.YYYY')
        product.product_id = uuid.uuid1().hex
        db.session.add(product)
        db.session.commit()
        db.session.close()
        flash(f"Метка сохранена с id - {product.product_id}", "success")
        return redirect(url_for("experiment.products_list"))
    return render_template("experiment.add_product.html", form=form)

@experiment.route("/products/list", methods=['POST', 'GET'])
def products_list():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 5, type=int)
    products = Products.query.order_by(Products.id.asc()).paginate(per_page=per_page, page=page)
    db.session.close()
    return render_template("experiment.products_list.html", products=products, per_page=per_page)

@experiment.route("/products/check/<string:id1>", methods=['POST', 'GET'])
def check_product(id1):
    product = Products.query.filter_by(product_id=id1).first()
    if not product:
        abort(404)
    firstcheck = False
    if not product.already_checked:
        product.first_checked = arrow.utcnow()
        product.already_checked = True
        db.session.commit()
        firstcheck = True
    db.session.close()
    return render_template("experiment.product_check.html", product=product, firstcheck=firstcheck)

@experiment.route("/products/qr/<string:id1>", methods=['POST', 'GET'])
def get_qr(id1):
    img_buf = BytesIO()
    img = generate_qr(url=url_for('experiment.check_product', id1=id1, _external=True))
    img.save(img_buf)
    img_buf.seek(0)
    return send_file(img_buf, mimetype='image/png')
    #return send_file(img, as_attachment=True, attachment_filename="qr.png", mimetype='image/png')
