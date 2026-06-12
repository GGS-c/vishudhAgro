from flask import Flask, render_template, request, redirect, flash, session, abort
from dotenv import load_dotenv

import os
import smtplib

import psycopg2
import psycopg2.extras

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import cloudinary
import cloudinary.uploader


# =============================
# CONFIG
# =============================

load_dotenv()

app = Flask(__name__)

# FIX: Secret key must be set via environment variable; fallback only for local dev
app.secret_key = os.getenv("SECRET_KEY", os.urandom(32))


# =============================
# CLOUDINARY CONFIG
# =============================

cloudinary.config(
    cloud_name=os.getenv("CLOUD_NAME"),
    api_key=os.getenv("CLOUD_API_KEY"),
    api_secret=os.getenv("CLOUD_API_SECRET")
)


# =============================
# ALLOWED FILE TYPES
# =============================

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


def allowed_file(filename):
    """Return True only if the filename has an allowed image extension."""
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


# =============================
# DATABASE
# =============================

def get_db():
    """Open and return a fresh psycopg2 connection."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL environment variable is not set.")
    return psycopg2.connect(database_url)


def create_tables():
    """Create tables if they do not already exist. Safe to call at startup."""
    try:
        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS gallery (
                id          SERIAL PRIMARY KEY,
                image_url   TEXT,
                public_id   TEXT,
                category    TEXT,
                created_at  TIMESTAMP DEFAULT NOW()
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id          SERIAL PRIMARY KEY,
                name        TEXT,
                description TEXT,
                features    TEXT,
                image_url   TEXT,
                public_id   TEXT,
                created_at  TIMESTAMP DEFAULT NOW()
            )
        """)

        conn.commit()
        cur.close()
        conn.close()

    except Exception as e:
        # Log the error but don't crash the app startup
        print(f"[WARNING] Could not create tables: {e}")


create_tables()


# =============================
# WEBSITE PAGES
# =============================

# HOME PAGE
@app.route("/")
def home():
    try:
        conn = get_db()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT * FROM products ORDER BY id DESC LIMIT 3")
        products = cur.fetchall()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[ERROR] home(): {e}")
        products = []

    return render_template("index.html", products=products)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/manufacturing")
def manufacturing():
    return render_template("manufacturing.html")


@app.route("/careers")
def careers():
    return render_template("careers.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


# =============================
# PRODUCTS PAGE
# =============================

@app.route("/products")
def products():
    try:
        conn = get_db()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT * FROM products ORDER BY id DESC")
        products = cur.fetchall()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[ERROR] products(): {e}")
        products = []

    return render_template("products.html", products=products)


# =============================
# GALLERY PAGE
# =============================

@app.route("/gallery")
def gallery():
    try:
        conn = get_db()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT * FROM gallery ORDER BY id DESC")
        images = cur.fetchall()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[ERROR] gallery(): {e}")
        images = []

    return render_template("gallery.html", images=images)


# =============================
# EMAIL ENQUIRY
# =============================

@app.route("/send-enquiry", methods=["POST"])
def send_enquiry():
    try:
        name     = request.form.get("name", "").strip()
        company  = request.form.get("company", "").strip()
        phone    = request.form.get("phone", "").strip()
        email    = request.form.get("email", "").strip()
        product  = request.form.get("product", "").strip()
        quantity = request.form.get("quantity", "").strip()
        message  = request.form.get("message", "").strip()

        # Basic server-side validation
        if not name or not phone or not product or not quantity:
            flash("Please fill all required fields.")
            return redirect("/contact")

        body = f"""
New Website Enquiry – Vishudh Agro
===================================

Name     : {name}
Company  : {company}
Phone    : {phone}
Email    : {email}
Product  : {product}
Quantity : {quantity}

Message:
{message}
"""

        msg = MIMEMultipart()
        msg["From"]    = os.getenv("SMTP_EMAIL", "")
        msg["To"]      = os.getenv("RECEIVER_EMAIL", "")
        msg["Subject"] = f"New Product Enquiry from {name} – Vishudh Agro"
        msg.attach(MIMEText(body, "plain"))

        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        server = smtplib.SMTP(os.getenv("SMTP_SERVER", "smtp.gmail.com"), smtp_port)
        server.starttls()
        server.login(os.getenv("SMTP_EMAIL", ""), os.getenv("SMTP_PASSWORD", ""))
        server.send_message(msg)
        server.quit()

        flash("Enquiry sent successfully! We will contact you soon.")

    except Exception as e:
        print(f"[ERROR] send_enquiry(): {e}")
        flash("Something went wrong. Please try again or call us directly.")

    return redirect("/contact")


# =============================
# ADMIN LOGIN
# =============================

@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    # If already logged in, go to dashboard
    if "admin" in session:
        return redirect("/dashboard")

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if (
            username == os.getenv("ADMIN_USER")
            and password == os.getenv("ADMIN_PASS")
        ):
            session["admin"] = True
            return redirect("/dashboard")

        flash("Invalid credentials. Please try again.")

    return render_template("admin/login.html")


# =============================
# DASHBOARD
# =============================

@app.route("/dashboard")
def dashboard():
    if "admin" not in session:
        return redirect("/admin")

    try:
        conn = get_db()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT * FROM products ORDER BY id DESC")
        products = cur.fetchall()
        cur.execute("SELECT * FROM gallery ORDER BY id DESC")
        images = cur.fetchall()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[ERROR] dashboard(): {e}")
        products = []
        images   = []

    return render_template(
        "admin/dashboard.html",
        products=products,
        images=images
    )


# =============================
# ADD PRODUCT
# =============================

@app.route("/add-product", methods=["POST"])
def add_product():
    if "admin" not in session:
        return redirect("/admin")

    try:
        name        = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        features    = request.form.get("features", "").strip()
        image       = request.files.get("image")

        # Validate required fields
        if not name or not description or not image:
            flash("All fields including image are required.")
            return redirect("/dashboard")

        # Validate file type
        if not allowed_file(image.filename):
            flash("Invalid file type. Only PNG, JPG, JPEG, GIF, WEBP are allowed.")
            return redirect("/dashboard")

        # Upload to Cloudinary with auto quality & format optimisation
        upload = cloudinary.uploader.upload(
            image,
            folder="vishudh_agro/products",
            transformation=[{"quality": "auto", "fetch_format": "auto"}]
        )

        image_url = upload["secure_url"]
        public_id = upload.get("public_id", "")

        conn = get_db()
        cur  = conn.cursor()
        cur.execute(
            """
            INSERT INTO products (name, description, features, image_url, public_id)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (name, description, features, image_url, public_id)
        )
        conn.commit()
        cur.close()
        conn.close()

        flash("Product added successfully!")

    except Exception as e:
        print(f"[ERROR] add_product(): {e}")
        flash("Failed to add product. Please try again.")

    return redirect("/dashboard")


# =============================
# DELETE PRODUCT
# =============================

# FIX: Changed from GET to POST to prevent CSRF / accidental deletion via crawlers
@app.route("/delete-product/<int:id>", methods=["POST"])
def delete_product(id):
    if "admin" not in session:
        return redirect("/admin")

    try:
        conn = get_db()
        cur  = conn.cursor()
        cur.execute("DELETE FROM products WHERE id = %s", (id,))
        conn.commit()
        cur.close()
        conn.close()
        flash("Product deleted successfully.")
    except Exception as e:
        print(f"[ERROR] delete_product(): {e}")
        flash("Failed to delete product.")

    return redirect("/dashboard")


# =============================
# ADD GALLERY
# =============================

@app.route("/upload-gallery", methods=["POST"])
def upload_gallery():
    if "admin" not in session:
        return redirect("/admin")

    try:
        image    = request.files.get("image")
        category = request.form.get("category", "General").strip()

        if not image:
            flash("Please select an image to upload.")
            return redirect("/dashboard")

        if not allowed_file(image.filename):
            flash("Invalid file type. Only PNG, JPG, JPEG, GIF, WEBP are allowed.")
            return redirect("/dashboard")

        upload = cloudinary.uploader.upload(
            image,
            folder="vishudh_agro/gallery",
            transformation=[{"quality": "auto", "fetch_format": "auto"}]
        )

        image_url = upload["secure_url"]
        public_id = upload.get("public_id", "")

        conn = get_db()
        cur  = conn.cursor()
        cur.execute(
            "INSERT INTO gallery (image_url, public_id, category) VALUES (%s, %s, %s)",
            (image_url, public_id, category)
        )
        conn.commit()
        cur.close()
        conn.close()

        flash("Image uploaded successfully!")

    except Exception as e:
        print(f"[ERROR] upload_gallery(): {e}")
        flash("Failed to upload image. Please try again.")

    return redirect("/dashboard")


# =============================
# DELETE GALLERY
# =============================

# FIX: Changed from GET to POST to prevent CSRF
@app.route("/delete-gallery/<int:id>", methods=["POST"])
def delete_gallery(id):
    if "admin" not in session:
        return redirect("/admin")

    try:
        conn = get_db()
        cur  = conn.cursor()
        cur.execute("DELETE FROM gallery WHERE id = %s", (id,))
        conn.commit()
        cur.close()
        conn.close()
        flash("Gallery image deleted.")
    except Exception as e:
        print(f"[ERROR] delete_gallery(): {e}")
        flash("Failed to delete image.")

    return redirect("/dashboard")


# =============================
# LOGOUT
# =============================

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/admin")


# =============================
# 404 ERROR HANDLER
# =============================

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


# =============================
# RUN
# =============================

if __name__ == "__main__":
    # FIX: debug=True only when explicitly set via environment variable
    debug_mode = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    port = int(os.getenv("PORT", 5000))
    app.run(debug=debug_mode, host="0.0.0.0", port=port)