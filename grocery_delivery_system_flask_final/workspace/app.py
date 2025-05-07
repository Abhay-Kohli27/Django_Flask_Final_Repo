from flask import Flask ,render_template ,redirect ,url_for ,request ,flash , abort
from flask_sqlalchemy import SQLAlchemy
import os
from flask_bcrypt import Bcrypt
from flask_login import LoginManager,UserMixin,login_required, login_user, logout_user, current_user
from functools import wraps
from datetime import datetime
from flask_restful import Api, Resource
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_restful import Api
from flask import jsonify

jwt = JWTManager()

app = Flask(__name__, static_folder="static")
jwt.init_app(app)
api = Api(app)

app.config["JWT_SECRET_KEY"] = "super-secret"

basedir=os.path.abspath(os.path.dirname(__file__))

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir,"app.db")

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config['SECRET_KEY'] = 'projectbangayaapna'

bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = "login"

db = SQLAlchemy(app)



class User(db.Model, UserMixin):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key = True)
    userName = db.Column(db.String(200))
    email = db.Column(db.String(150), nullable = False)
    password_hash = db.Column(db.String(256), nullable = False)
    mobile = db.Column(db.String(50), nullable = False)
    role = db.Column(db.String(50), nullable = False, default = "user")
    latitude = db.Column(db.Float, nullable = True)  
    longitude = db.Column(db.Float, nullable = True) 
    location = db.Column(db.String(1000), nullable = True)
    birth_date = db.Column(db.String(100))

    store = db.relationship('Store', backref='owner', uselist = False)

    def as_dict(self):
        if self.store:
            return {
                "id": self.id,
                "userName": self.userName,
                "email": self.email,
                "mobile": self.mobile,
                "role": self.role,
                "latitude": self.latitude,
                "longitude": self.longitude,
                "location": self.location,
                "store":self.store.as_dict() 
            }
        else:
             return {
                "id": self.id,
                "userName": self.userName,
                "email": self.email,
                "mobile": self.mobile,
                "role": self.role,
                "latitude": self.latitude,
                "longitude": self.longitude,
                "location": self.location
            }


    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password)

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)


class Store(db.Model):
    __tablename__ = "store"

    id = db.Column(db.Integer, primary_key = True)
    storeName = db.Column(db.String(100), unique = True)
    category = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    deals = db.Column(db.String(200), nullable=True)
    contactEmail = db.Column(db.String(200), nullable = False)
    location = db.Column(db.String(300))
    isapproved = db.Column(db.Boolean, default=False) 
    ownerid = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    storeKey = db.Column(db.Integer, nullable=False)
    ownerName = db.Column(db.String(50), nullable=False)

    products = db.relationship('Product', backref='store', lazy="select")

    def as_dict(self):
        return {
            "id": self.id,
            "storeName": self.storeName,
            "category": self.category,
            "deals": self.deals,
            "contactEmail": self.contactEmail,
            "location": self.location,
            "isapproved": self.isapproved,
            "ownerid": self.ownerid,
            "storeKey": self.storeKey,
            "ownerName": self.ownerName,
        }

    def __repr__(self):
        return f"storeID: {self.id}, Store name: {self.storeName}, Category: {self.category}, Deals: {self.deals}"



class Product(db.Model):
    __tablename__ = "product"

    id = db.Column(db.Integer, primary_key = True)
    productName = db.Column(db.String(100), nullable = True)
    category = db.Column(db.String(100))
    price = db.Column(db.Float, nullable = False)
    image = db.Column(db.String(1000), nullable=True)
    quantity = db.Column(db.Integer)
    storeid = db.Column(db.Integer, db.ForeignKey('store.id'), nullable=False)
    created_at = db.Column(db.DateTime, default = datetime.utcnow)
    description = db.Column(db.String(500), default = "this is a good product")
    featuredProduct = db.Column(db.Boolean, default=False)
    stock_threshold = db.Column(db.Integer, default=1)

    def as_dict(self):
        return {
            "id": self.id,
            "productName": self.productName,
            "category": self.category,
            "price": self.price,
            "quantity": self.quantity,
            "storeid": self.storeid,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "description": self.description,
            "featured_product":self.featuredProduct,
            "stock_threshold":self.stock_threshold
        }



    def __repr__(self):
        return f"productID: {self.id}, Product name: {self.productName}, Category: {self.category}, Price: {self.price}, Image: {self.image}, Quantity: {self.quantity}"


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    business_id = db.Column(db.Integer, db.ForeignKey('store.id'), nullable=True)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default="Pending")
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    user = db.relationship('User', backref='orders', lazy=True)
    business = db.relationship('Store', backref='orders')



class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False) 

    order = db.relationship('Order', backref=db.backref('items', lazy=True))
    product = db.relationship('Product', backref=db.backref('order_items', lazy=True))



class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    user = db.relationship('User', backref='cart_items')
    product = db.relationship('Product', backref='cart_entries')




@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))



class UserRegisterResource(Resource):
    def post(self):
        data = request.get_json()

        username = data.get("username")
        email = data.get("email")
        mobile = data.get("mobile")
        password = data.get("password")
        role = data.get("role", "user")
        address = data.get("address")
        birth_date = data.get("birth_date")

        if User.query.filter_by(email=email).first():
            return {"message": "Email already exists."}, 400
        new_user = User(
            userName = username, 
            email = email, 
            mobile = mobile, 
            role = role,
            location = address,
            birth_date = birth_date
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        return {"message": "User registered successfully."}, 201


class UserLoginResource(Resource):
    def post(self):
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            access_token = create_access_token(identity=user.email)
            return {"access_token": access_token}, 200

        return {"message": "Invalid credentials."}, 401
    

class UserLogoutResource(Resource):
    @jwt_required()
    def get(self):
        logout_user()
        return {"message": "User logged out successfuly"}, 200


class UserResource(Resource):
    @jwt_required()
    def get(self):
        identity = get_jwt_identity()

        user = User.query.filter_by(email=identity).first()

        if user:
            return {"current_user": user.as_dict()}
        else:
            return {"message": "User not found or session expired"}, 404

class ProductResource(Resource):

    @jwt_required()
    def get(self, id):
        product = db.session.get(Product, id)

        if not product:
            return {"message": "Product not found"}, 404
        return {"product":product.as_dict()}
    

    @jwt_required()
    def post(self):
        data = request.get_json()
        current_user = User.query.filter_by(email = get_jwt_identity()).first()

        store = Store.query.filter(Store.owner.has(id=current_user.id)).first()
        if (not store):
            return {"message": "You must own an approved store to add products"}, 403
        elif not store.isapproved:
            return {"message": "your store has not been approved!!"}, 403

        name = data.get("name")
        category = data.get("category")
        price = data.get("price")
        quantity = data.get("quantity")
        featured_product = data.get('featured_product')
        storeid = store.id

        if not all([name, price, quantity, category]):
            return {"message": "All fields (name, price, quantity, category) are required."}, 400

        new_product = Product(
            productName=name, 
            category=category,
            price=price,
            quantity=quantity, 
            storeid = storeid,
            featuredProduct = featured_product
        )
        db.session.add(new_product)
        db.session.commit()
        return {"message": "Product Added Successfully", "product": new_product.as_dict()}, 201

    @jwt_required()
    def put(self, id):

        current_user = User.query.filter_by(email = get_jwt_identity()).first()


        store = Store.query.filter(Store.owner.has(id=current_user.id)).first()
        if (not store):
            return {"message": "You must own an approved store to update products"}, 403
        elif not store.isapproved:
            return {"message": "your store has not been approved!!"}, 403


        product = db.session.get(Product, id)
        if product:
            data = request.get_json()
            product.productName = data.get("name", product.productName)
            product.category = data.get("category", product.category)
            product.price = data.get("price", product.price)
            product.quantity = data.get("quantity", product.quantity)

            db.session.add(product)
            db.session.commit()
            return {"message": "Product Updated Successfully", "product": product.as_dict()}, 200
        else:
            return {"message": "Product Not Found!"}, 404


    @jwt_required()
    def delete(self, id):
        identity = get_jwt_identity()
        user = User.query.filter_by(email=identity).first()
        store = Store.query.filter(Store.owner.has(id=user.id)).first()

        product = db.session.get(Product, id)
        if product:
            db.session.delete(product)
            db.session.commit()
            return {"message": "Product deleted successfully"}
        return {"message": "Product Not Found!"}, 404



class ProductsResource(Resource):
    @jwt_required()
    def get(self):
        allproducts = Product.query.all()

        products = []
        for product in allproducts:
            products.append(product.as_dict())

        if products:
            return {"products": products}
        else:
            return {"message": "No Products Available!"}



class StoreProductsResource(Resource):
    def get(self, store_id):
        products = Product.query.filter_by(storeid=store_id).all()
        if not products:
            return {"message": "No products found for this store."}, 404

        product_list = []
        for product in products:
            product_list.append({
                "id": product.id,
                "name": product.productName,
                "price": product.price,
                "description": product.description,
                "stock": product.quantity,
                "image": product.image,
                "category": product.category,
            })

        return {"products": product_list}, 200


class ProductCategory(Resource):
    @jwt_required()
    def get(self, category):

        allproducts = Product.query.filter_by(
            category=category).all()

        products = []
        for product in allproducts:
            products.append(product.as_dict())

        if products:
            return {"products": products}
        else:
            return {"message": "No products found in this category"}, 404


class storesResource(Resource):
    @jwt_required()
    def get(self):

        all_stores = Store.query.all()

        stores = []
        for store in all_stores:
            stores.append(store.as_dict())

        if stores:
            return {"stores": stores}
        else:
            return {"message": "No Products Available!"}


class storeResource(Resource):
    @jwt_required()
    def get(self, id):
        
        store = db.session.get(Store, id)

        if store:
            return {"store":store.as_dict()}
        else:
            return {"message":"No store found"}, 404
        
    @jwt_required()
    def post(self):
        data = request.get_json()

        name = data.get("name")
        category = data.get("category")
        email = data.get("email")
        location = data.get("location")
        store_key = data.get("store_key")
        owner_name = data.get("owner_name")

        if not all([name, category, email, category, location, store_key, owner_name]):
            return {"message": "All fields ([name, category, email, category, location, store_key, owner_name]) are required."}, 400

        identity = get_jwt_identity()
        user = User.query.filter_by(email=identity).first()

        new_store = Store(
            storeName=name, 
            category=category,
            contactEmail = email,
            location = location,
            ownerid = user.id, 
            storeKey = store_key,
            ownerName = owner_name
        )
        db.session.add(new_store)
        db.session.commit()
        return {"message": "Application to open a store submitted successfully", "store": new_store.as_dict()}, 201

    @jwt_required()
    def put(self, id):

        store = db.session.get(Store, id)

        if not current_user.store:
            return {"Message" : "You need to be a store owner to update a store's profile"}
        elif current_user.id != store.ownerid:
            return {"Message": "Store owner only"}, 401
        
        data = request.get_json()

        store.storeName = data.get("name", store.storeName)
        store.category = data.get("category", store.category)
        store.deals = data.get("deals", store.deals)
        store.contactEmail = data.get("email", store.contactEmail)
        store.location = data.get("location", store.location)
        store.ownerName = data.get("owner_name", store.ownerName)

        db.session.add(store)
        db.session.commit()
        return {"message": "store profile updated successfully", "store" : store.as_dict()}
        


class storeApproveResource(Resource):
    @jwt_required()
    def put(self, id):
        identity = get_jwt_identity()
        user = User.query.filter_by(email=identity).first()
        if user.role != "admin":
            return {"message": "Not allowed: Admins only"}, 401
        
        store = db.session.get(Store, id)
         
        if not store:
            return {"message": "store not found"}
        
        store.isapproved = True
        db.session.add(store)
        db.session.commit()
        return {"message": "Store Approved successfully!", "store":store.as_dict()}, 200
        
        
    
with app.app_context():
    db.create_all()
    if not User.query.filter_by(role="admin").first():
        admin_user = User(id=0,userName="Admin", email="admin@gmail.com", mobile="1234567890", role="admin")
        admin_user.set_password("admin123") 
        db.session.add(admin_user)
        db.session.commit()
        print("Admin user created with email: admin@gmail.com and password: admin123")



def role_required(role):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role == role:
                return fn(*args, **kwargs)
        return decorated_view
    return wrapper



def store_owner_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        store = Store.query.filter_by(ownerid=current_user.id, isapproved=True).first()
        if not store:
            flash("You must own an approved store to access this page.", "danger")
            return redirect(url_for("home"))
        return f(*args, **kwargs)
    return decorated_function



@app.route("/")
# yeh route mere landing page k liye hai 
def index():
    return render_template("index.html")


@app.route("/home") 
# yeh hamara home page jiske liye login required hai 
@login_required
def home():
    stores = Store.query.filter_by(isapproved=True).all()
    return render_template("home.html", stores=stores)



@app.route("/register", methods=["POST", "GET"])
# register vaala page
def register():

    if request.method =="POST":

        first_name = request.form.get("firstName")
        last_name = request.form.get("lastName")
        email = request.form.get("email")
        password = request.form.get("password")
        print(password)
        confirm_password = request.form.get("confirm_password")
        phone_number = request.form.get("phone")
        
        longitude = request.form.get("longitude")
        latitude = request.form.get("latitude")
        
        address = request.form.get("address")

        if User.query.filter_by(email=email).first():
            flash("User already exists. Try logging in instead!", "danger")
            return redirect(url_for("register"))
        
        if password != confirm_password:
            flash("Passwords don't match", "Danger")
            redirect(url_for("register"))


        new_user = User(
                userName = (first_name + " " + last_name), 
                email = email, mobile = phone_number, 
                location = address, 
                longitude = longitude, 
                latitude = latitude
            )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash("Registeration Successfull! Please login.", "success")
        return redirect(url_for("login"))
    
    return render_template("register.html")



@app.route("/login", methods=["POST", "GET"])
# yeh login vaale page ka route
def login():

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        role = request.form.get("role")


        user = User.query.filter_by(email = email, role = role).first()
        if user and user.check_password(password):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for('home'))
        else:
            flash("Invalid credentials!", "danger")
            return redirect(url_for("register"))

    return render_template("login.html")



@app.route("/logout")
# logout ka button
@login_required
def logout():
    logout_user()
    flash("Logged out successfully!", "info")
    return redirect(url_for("index"))



@app.route("/admin/dashboard")
@role_required("admin")
def admin_dashboard():
    pending_store_count = Store.query.filter(Store.isapproved == False).count()
    total_stores = Store.query.count()
    total_users = User.query.count()
    pending_store_approvals = Store.query.filter_by(isapproved=False).all()
    return render_template("admin_dashboard.html", pending_store_approvals=pending_store_approvals, pending_store_count=pending_store_count, total_stores=total_stores, total_users=total_users)



@app.route("/admin/approve_store/<int:store_id>")
@role_required("admin")
def approve_store(store_id):
    store = Store.query.get_or_404(store_id)
    store.isapproved = True
    db.session.commit()
    flash("Store approved!", "success")
    return redirect(url_for("admin_dashboard"))



@app.route("/admin/reject_store/<int:store_id>")
@role_required("admin")
def reject_store(store_id):
    store = Store.query.get_or_404(store_id)
    db.session.delete(store)
    db.session.commit()
    flash("Store rejected!", "danger")
    return redirect(url_for("admin_dashboard"))



@app.route("/apply_store", methods=["POST", "GET"])
@login_required
def apply_store():
    if request.method == "POST":
        store_name = request.form.get("store_name")
        category = request.form.get("category")
        owner_name = request.form.get("owner_name")
        contact_email = request.form.get("contact")
        address = request.form.get("address")
        storeKey = request.form.get("store_key")

        if Store.query.filter_by(storeName=store_name).first():
            flash("Store already exists", "danger")
            return redirect(url_for("register"))
        
        new_store = Store(
            storeName=store_name,
            category=category,
            ownerid=current_user.id, 
            contactEmail=contact_email,
            location=address,
            isapproved=False,
            storeKey=storeKey,
            ownerName=owner_name
        )

        db.session.add(new_store)
        db.session.commit()
        flash("Your application has been sent successfully", "success")
        return redirect(url_for("home"))

    return render_template("apply_store_form.html")



@app.route("/user_profile")
@login_required
def user_profile():
    return render_template("your_profile.html")



@app.route("/admin/allstores")
@role_required('admin')
def allstores():
    pending_store_count = Store.query.filter(Store.isapproved == False).count()
    total_stores = Store.query.count()
    total_users = User.query.count()
    pending_store_approvals = Store.query.filter_by(isapproved=False).all()
    all_stores = Store.query.all()
    return render_template("allstores.html", all_stores=all_stores, pending_store_approvals=pending_store_approvals, pending_store_count=pending_store_count, total_stores=total_stores, total_users=total_users)



@app.route("/store/add_product", methods=["GET","POST"])
@login_required
@store_owner_required
def add_product():
    store = Store.query.filter(Store.owner.has(id=current_user.id)).first()
    if not store:
        flash("You must own an approved store to add products!", "danger")
        return redirect(url_for("dashboard"))
     
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        price = request.form.get("price")
        quantity = request.form.get("stock")
        category = request.form.get("category")
        image = request.form.get("image_url")

        new_product = Product(
            storeid = store.id,
            productName=name,
            description=description,
            price=float(price),
            quantity=quantity,
            category=category,
            image=image
        )

        db.session.add(new_product)
        db.session.commit()

        flash("Product added succesfully", "success")
        return redirect(url_for("manage_products"))

    return render_template("manage_products.html")





@app.route("/store/manage_products")
@login_required
@store_owner_required
def manage_products():
    store = Store.query.filter(Store.owner.has(id=current_user.id)).first()
    if not store:
        flash("You donot have an approved store!", "danger")
        return redirect(url_for("dashboard"))
    
    products = Product.query.filter_by(storeid=store.id).all()
    return render_template("manage_products.html", products=products, storename=store.storeName)



@app.route("/store/view_orders")
@login_required
@store_owner_required
def view_orders():
    store = Store.query.filter(Store.owner.has(id=current_user.id)).first()
    orders_for_store=Order.query.filter_by(business_id=store.id).all()

    order_user_pairs = []
    
    for order in orders_for_store:
        user = User.query.get(order.user_id)  
        order_user_pairs.append((order, user))
    
    return render_template('manage_store.html', order_user_pairs=order_user_pairs)



@app.route("/store/edit_product/<int:product_id>", methods=["GET", "POST"])
@store_owner_required
def edit_product(product_id):
    product = db.session.get(Product, product_id)
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        price = request.form.get("price")
        quantity = request.form.get("stock")
        category = request.form.get("category")
        image = request.form.get("image_url")

        product.productName = name
        product.description = description
        product.price = price
        product.quantity = quantity
        product.category = category
        product.image = image

        db.session.add(product)
        db.session.commit()
        return redirect(url_for("manage_products"))
    
    return render_template("edit_product.html", product=product)

@app.route("/store/delete_product/<int:product_id>")
@store_owner_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash("Product deleted!", "danger")
    return redirect(url_for("home"))



@app.route("/product/<int:product_id>")
@login_required
def product(product_id):
    product = db.session.get(Product, product_id)
    return render_template("product.html", product=product)


@app.route("/cart/add/<int:product_id>" , methods=["POST","GET"])
@login_required
def add_to_cart(product_id):

    if request.method == "POST":
        quantity = request.form.get('quantity')
        product = db.session.get(Product, product_id)
        cart_item = Cart.query.filter_by(user_id = current_user.id, product_id = product.id).first()

        # if cart_item:
        #     cart_item.quantity += int(quantity)
        # else:
        cart_item = Cart(
            user_id = current_user.id,
            product_id = product.id,
            quantity = quantity
        )
        
        db.session.add(cart_item)
        db.session.commit()
        flash("Product added to cart!", "success")
    return redirect(url_for("home"))

@app.route("/cart")
@login_required
def view_cart():
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    return render_template("cart.html", cart_items=cart_items)


@app.route("/cart/remove/<int:product_id>")
@login_required
def remove_from_cart(product_id):
    cart_item = Cart.query.get_or_404(product_id)
    db.session.delete(cart_item)
    db.session.commit()
    flash("Item removed from cart!", "danger")
    return redirect(url_for("view_cart"))



@app.route("/home/search", methods=["GET"])
@login_required
def search():
        query = request.args.get('search_input', '').strip()
        if not query:
            return redirect(url_for('home'))  

        results = Product.query.filter(
            (Product.productName.ilike(f"%{query}%")) |
            (Product.description.ilike(f"%{query}%")) |
            (Product.category.ilike(f"%{query}%"))
        ).all()

        return render_template('home.html', results=results, query=query)



@app.route("/checkout")
@login_required
def checkout():
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    return render_template("checkout.html" , cart_items=cart_items)

@app.route("/checkout/placeorder", methods=["POST","GET"])
@login_required
def placeorder(): 

    cart = Cart.query.filter_by(user_id=current_user.id).all()

    total_sum = 6
    business_id=0

    for item in cart:
        product_id=item.product_id
        product=Product.query.filter_by(id=product_id).first()
        total_sum += product.price * item.quantity
        business_id=product.storeid
    
    

    new_order=Order(
        user_id=current_user.id,
        total_price=total_sum,
        status="pending",
        business_id=business_id
    )

    db.session.add(new_order)
    db.session.commit()


    for item in cart:
        db.session.delete(item)
        db.session.commit()


    flash("Your Order was places successfully!", "success")
    return redirect(url_for("home"))



api.add_resource(UserRegisterResource, "/api/register")
api.add_resource(UserLoginResource, "/api/login")
api.add_resource(UserLogoutResource, "/api/logout")
api.add_resource(UserResource, "/api/user")
api.add_resource(ProductResource, "/api/product", "/api/product/<int:id>")
api.add_resource(ProductsResource, "/api/products")
api.add_resource(ProductCategory, "/api/products/category/<string:category>")
api.add_resource(storesResource, "/api/stores")
api.add_resource(storeResource, "/api/store" , "/api/store/<int:id>")
api.add_resource(storeApproveResource, "/api/store/approve/<int:id>")
api.add_resource(StoreProductsResource, '/api/store/<int:store_id>/products')


if __name__ == "__main__":
    app.run(debug=True)

