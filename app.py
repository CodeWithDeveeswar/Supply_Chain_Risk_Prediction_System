from flask import Flask, render_template, request, redirect, session, flash, url_for, jsonify
import sqlite3
from datetime import datetime
from config import *
from utils.excel_export import export_excel
from utils.predictor import run_prediction
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
import subprocess
import pandas as pd

app = Flask(__name__)
app.secret_key = SECRET_KEY or os.getenv("SECRET_KEY") or "local-development-key-change-before-deploy"
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true",
)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# ---------------- DATABASE AND AUTH HELPERS ----------------
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = None
    return conn


def ensure_database_schema():
    """Prepare the database and keep one configured administrator account."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT,
        email TEXT,
        password_hash TEXT,
        created_at TEXT
    )""")
    user_columns = {row[1] for row in cursor.execute("PRAGMA table_info(users)").fetchall()}
    for column, definition in (("email", "TEXT"), ("password_hash", "TEXT"), ("created_at", "TEXT")):
        if column not in user_columns:
            cursor.execute(f"ALTER TABLE users ADD COLUMN {column} {definition}")

    cursor.execute("""CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, supplier TEXT,
        region INTEGER, transport INTEGER, delay REAL, weather INTEGER,
        demand INTEGER, inventory INTEGER, traffic INTEGER, port_delay INTEGER,
        order_value REAL, fuel_cost REAL, risk TEXT, user_id INTEGER
    )""")
    prediction_columns = {row[1] for row in cursor.execute("PRAGMA table_info(predictions)").fetchall()}
    if "user_id" not in prediction_columns:
        cursor.execute("ALTER TABLE predictions ADD COLUMN user_id INTEGER")

    # Migrate legacy plaintext passwords before applying the single-admin setup.
    for user_id, old_password, password_hash in cursor.execute(
        "SELECT id, password, password_hash FROM users"
    ).fetchall():
        if old_password and not password_hash:
            cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?",
                           (generate_password_hash(old_password), user_id))

    admin_username = os.getenv("ADMIN_USERNAME", "").strip()
    admin_password = os.getenv("ADMIN_PASSWORD", "")
    if admin_username and admin_password:
        admin = cursor.execute(
            "SELECT id FROM users WHERE username = ? COLLATE NOCASE", (admin_username,)
        ).fetchone()
        password_hash = generate_password_hash(admin_password)
        now = datetime.now().isoformat(timespec="seconds")
        if admin:
            admin_id = admin[0]
            cursor.execute(
                "UPDATE users SET username = ?, password_hash = ?, password = NULL, email = NULL, created_at = COALESCE(created_at, ?) WHERE id = ?",
                (admin_username, password_hash, now, admin_id),
            )
            cursor.execute("UPDATE predictions SET user_id = ?", (admin_id,))
            cursor.execute("DELETE FROM users WHERE id != ?", (admin_id,))
        else:
            cursor.execute(
                "INSERT INTO users (username, password, email, password_hash, created_at) VALUES (?, NULL, NULL, ?, ?)",
                (admin_username, password_hash, now),
            )
            admin_id = cursor.lastrowid
            cursor.execute("UPDATE predictions SET user_id = ?", (admin_id,))
            cursor.execute("DELETE FROM users WHERE id != ?", (admin_id,))
    else:
        app.logger.warning(
            "ADMIN_USERNAME and ADMIN_PASSWORD are not configured. Set both in .env before logging in."
        )

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_predictions_user_id ON predictions(user_id)")
    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_username_nocase ON users(username COLLATE NOCASE)")
    cursor.execute("UPDATE users SET created_at = COALESCE(created_at, ?)",
                   (datetime.now().isoformat(timespec="seconds"),))
    conn.commit()
    conn.close()

def current_user_id():
    return session.get("user_id")


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user_id():
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped



ensure_database_schema()


# ---------------- AUTHENTICATION ----------------
@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user_id():
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        conn = get_db()
        user = conn.execute(
            "SELECT id, username, password_hash FROM users WHERE username = ? COLLATE NOCASE",
            (username,)
        ).fetchone()
        conn.close()
        if user and user[2] and check_password_hash(user[2], password):
            session.clear()
            session["user_id"] = user[0]
            session["user"] = user[1]
            flash("Login successful.", "success")
            return redirect(url_for("dashboard"))
        flash("Invalid username or password.", "danger")
    return render_template("login.html")


@app.route("/dashboard")
@login_required
def dashboard():
    if "user" not in session:
        return redirect("/")

    conn = get_db()
    cursor = conn.cursor()

    # ================= KPI =================
    cursor.execute("SELECT COUNT(*) FROM predictions WHERE user_id = ?", (current_user_id(),))
    total_predictions = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT supplier) FROM predictions WHERE user_id = ?", (current_user_id(),))
    total_suppliers = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM predictions WHERE user_id = ? AND risk='High'", (current_user_id(),))
    high_risk = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM predictions WHERE user_id = ? AND risk='Medium'", (current_user_id(),))
    medium_risk = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM predictions WHERE user_id = ? AND risk='Low'", (current_user_id(),))
    low_risk = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(delay) FROM predictions WHERE user_id = ?", (current_user_id(),))
    avg_delay = round(cursor.fetchone()[0] or 0, 2)

    cursor.execute("SELECT SUM(order_value) FROM predictions WHERE user_id = ?", (current_user_id(),))
    total_value_raw = cursor.fetchone()[0] or 0
    total_value = f"{total_value_raw:,.0f}"

    cursor.execute("SELECT AVG(fuel_cost) FROM predictions WHERE user_id = ?", (current_user_id(),))
    avg_fuel_raw = cursor.fetchone()[0] or 0
    avg_fuel = f"{avg_fuel_raw:.2f}"

    # ================= REGION =================
    regionData = [0,0,0,0,0]
    cursor.execute("SELECT region, COUNT(*) FROM predictions WHERE user_id = ? GROUP BY region", (current_user_id(),))
    for r,c in cursor.fetchall():
        if r < 5:
            regionData[r] = c

    # ================= TRANSPORT =================
    transportData = [0,0,0,0]
    cursor.execute("SELECT transport, COUNT(*) FROM predictions WHERE user_id = ? GROUP BY transport", (current_user_id(),))
    for t,c in cursor.fetchall():
        if t < 4:
            transportData[t] = c

    # ================= WEATHER =================
    weatherData = {
        0: {"Low":0,"Medium":0,"High":0},
        1: {"Low":0,"Medium":0,"High":0},
        2: {"Low":0,"Medium":0,"High":0},
        3: {"Low":0,"Medium":0,"High":0}
    }

    cursor.execute("SELECT weather, risk, COUNT(*) FROM predictions WHERE user_id = ? GROUP BY weather, risk", (current_user_id(),))
    for w,r,c in cursor.fetchall():
        if w in weatherData:
            weatherData[w][r] = c

    # ================= TRAFFIC =================
    trafficData = [0,0,0]
    cursor.execute("SELECT traffic, AVG(delay) FROM predictions WHERE user_id = ? GROUP BY traffic", (current_user_id(),))
    for t,a in cursor.fetchall():
        if t < 3:
            trafficData[t] = round(a,2)

    # ================= DEMAND =================
    demandData = [0,0,0]
    cursor.execute("SELECT demand, COUNT(*) FROM predictions WHERE user_id = ? GROUP BY demand", (current_user_id(),))
    for d,c in cursor.fetchall():
        if d < 3:
            demandData[d] = c

    # ================= STOCK =================
    stockData = {
        "Sufficient": {"Low": 0, "Medium": 0, "High": 0},
        "Low": {"Low": 0, "Medium": 0, "High": 0},
        "Out": {"Low": 0, "Medium": 0, "High": 0}
    }

    cursor.execute("SELECT inventory, risk FROM predictions WHERE user_id = ?", (current_user_id(),))

    for inv, risk in cursor.fetchall():

        inv = int(inv)

        if inv >= 1000:
            stockData["Sufficient"][risk] += 1
        elif inv >= 300:
            stockData["Low"][risk] += 1
        else:
            stockData["Out"][risk] += 1

    # ================= VALUE TREND =================
    valueData = [0]*7
    cursor.execute("""
        SELECT strftime('%w', date), SUM(order_value)
        FROM predictions
        WHERE user_id = ?
        GROUP BY strftime('%w', date)
    """, (current_user_id(),))
    for d,v in cursor.fetchall():
        valueData[int(d)] = v or 0

    # ================= FUEL =================
    cursor.execute("""
        SELECT delay, fuel_cost, risk
        FROM predictions
        WHERE user_id = ? AND fuel_cost IS NOT NULL
        LIMIT 100
    """, (current_user_id(),))

    fuelData = [list(row) for row in cursor.fetchall()]

    # ================= ALERT TABLE =================
    cursor.execute("""
        SELECT supplier, region, delay, weather, risk
        FROM predictions
        WHERE user_id = ? AND risk='High'
        ORDER BY delay DESC
        LIMIT 5
    """, (current_user_id(),))
    alerts = cursor.fetchall()

    conn.close()

    return render_template(
        "dashboard.html",

        total_predictions=total_predictions,
        total_suppliers=total_suppliers,
        high_risk=high_risk,
        medium_risk=medium_risk,
        low_risk=low_risk,
        avg_delay=avg_delay,
        total_value=total_value,
        avg_fuel=avg_fuel,

        regionData=regionData,
        transportData=transportData,
        weatherData=weatherData,
        trafficData=trafficData,
        demandData=demandData,
        stockData=stockData,
        valueData=valueData,
        fuelData=fuelData,

        alerts=alerts
    )
@app.route("/dashboard-data")
@login_required
def dashboard_data():
    if "user" not in session:
        return {}

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM predictions WHERE user_id = ?", (current_user_id(),))
    total_predictions = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT supplier) FROM predictions WHERE user_id = ?", (current_user_id(),))
    total_suppliers = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM predictions WHERE user_id = ? AND risk='High'", (current_user_id(),))
    high_risk = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM predictions WHERE user_id = ? AND risk='Medium'", (current_user_id(),))
    medium_risk = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM predictions WHERE user_id = ? AND risk='Low'", (current_user_id(),))
    low_risk = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(delay) FROM predictions WHERE user_id = ?", (current_user_id(),))
    avg_delay = round(cursor.fetchone()[0] or 0, 2)

    cursor.execute("SELECT SUM(order_value) FROM predictions WHERE user_id = ?", (current_user_id(),))
    total_value_raw = cursor.fetchone()[0] or 0
    total_value = f"{total_value_raw:,.0f}"

    cursor.execute("SELECT AVG(fuel_cost) FROM predictions WHERE user_id = ?", (current_user_id(),))
    avg_fuel_raw = cursor.fetchone()[0] or 0
    avg_fuel = f"{avg_fuel_raw:.2f}"

    cursor.execute("""
        SELECT supplier, region, delay, weather, risk
        FROM predictions
        WHERE user_id = ? AND risk='High'
        ORDER BY delay DESC
        LIMIT 5
    """, (current_user_id(),))
    alerts = cursor.fetchall()

    conn.close()

    return {
        "total_predictions": total_predictions,
        "total_suppliers": total_suppliers,
        "high_risk": high_risk,
        "medium_risk": medium_risk,
        "low_risk": low_risk,
        "avg_delay": avg_delay,
        "total_value": total_value,
        "avg_fuel": avg_fuel,
        "alerts": alerts
    }

# ---------------- PREDICT ----------------
@app.route("/predict", methods=["GET", "POST"])
@login_required
def predict():
    if "user" not in session:
        return redirect("/")

    if request.method == "POST":

        conn = get_db()
        cursor = conn.cursor()

        # ================= MAPPING =================
        region_map = {
            "asia": 0,
            "europe": 1,
            "north america": 2,
            "south america": 3,
            "africa": 4
        }

        transport_map = {
            "truck": 0,
            "rail": 1,
            "ship": 2,
            "air": 3
        }

        weather_map = {
            "clear": 0,
            "rain": 1,
            "storm": 2,
            "fog": 3
        }

        traffic_map = {
            "low": 0,
            "medium": 1,
            "high": 2
        }

        demand_map = {
            "low": 0,
            "medium": 1,
            "high": 2
        }

        # ================= FILE UPLOAD =================
        file = request.files.get("file")

        if file and file.filename != "":

            upload_folder = os.path.join(os.getcwd(), "uploads")

            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{secure_filename(file.filename)}"
            file_path = os.path.join(upload_folder, filename)

            file.save(file_path)

            if filename.endswith(".csv"):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)

            inserted = 0

            for _, row in df.iterrows():
                try:
                    supplier = str(row.get("supplier", "Unknown"))

                    # 🔥 SMART CONVERSION FUNCTION
                    def convert(value, mapping):
                        if isinstance(value, str):
                            return mapping.get(value.strip().lower(), 0)
                        return int(value)

                    region = convert(row.get("region", 0), region_map)
                    transport = convert(row.get("transport", 0), transport_map)
                    weather = convert(row.get("weather", 0), weather_map)
                    traffic = convert(row.get("traffic", 0), traffic_map)
                    demand = convert(row.get("demand", 0), demand_map)

                    delay = float(row.get("delay", 0))
                    inventory = int(row.get("inventory", 0))
                    port_delay = int(row.get("port_delay", 0))
                    order_value = float(row.get("order_value", 0))

                    # ================= PREDICTION =================
                    result = run_prediction({
                        "delay": delay,
                        "traffic": traffic,
                        "weather": weather,
                        "inventory": inventory,
                        "order_value": order_value,
                        "port_delay": port_delay
                    })

                    risk = result.get("risk", "Unknown")
                    fuel_cost = result.get("fuel_cost", 0)

                    date = datetime.now().strftime("%Y-%m-%d %H:%M")

                    cursor.execute("""
                        INSERT INTO predictions (
                            date, supplier, region, transport, delay,
                            weather, demand, inventory, traffic,
                            port_delay, order_value, fuel_cost, risk, user_id
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        date, supplier, region, transport, delay,
                        weather, demand, inventory, traffic,
                        port_delay, order_value, fuel_cost, risk, current_user_id()
                    ))

                    inserted += 1

                except Exception as e:
                    print("Row skipped:", e)

            conn.commit()
            conn.close()

            subprocess.Popen(["python", "model/train_model.py"])

            flash(f"{inserted} records uploaded & predicted successfully", "success")
            return redirect("/dashboard")

        # ================= MANUAL FORM =================
        def convert_form(value, mapping):
            if isinstance(value, str) and not value.isdigit():
                return mapping.get(value.lower(), 0)
            return int(value)

        supplier = request.form.get("supplier")

        region = convert_form(request.form.get("region"), region_map)
        transport = convert_form(request.form.get("transport"), transport_map)
        weather = convert_form(request.form.get("weather"), weather_map)
        traffic = convert_form(request.form.get("traffic"), traffic_map)
        demand = convert_form(request.form.get("demand"), demand_map)

        delay = float(request.form.get("delay"))
        inventory = int(request.form.get("inventory"))
        port_delay = int(request.form.get("port_delay"))
        order_value = float(request.form.get("order_value"))

        result = run_prediction({
            "delay": delay,
            "traffic": traffic,
            "weather": weather,
            "inventory": inventory,
            "order_value": order_value,
            "port_delay": port_delay
        })

        risk = result.get("risk", "Unknown")
        fuel_cost = result.get("fuel_cost", 0)
        confidence = result.get("confidence", 0)
        explanation = result.get("explanation", [])

        date = datetime.now().strftime("%Y-%m-%d %H:%M")

        cursor.execute("""
            INSERT INTO predictions (
                date, supplier, region, transport, delay,
                weather, demand, inventory, traffic,
                port_delay, order_value, fuel_cost, risk, user_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            date, supplier, region, transport, delay,
            weather, demand, inventory, traffic,
            port_delay, order_value, fuel_cost, risk, current_user_id()
        ))

        conn.commit()
        conn.close()

        flash(f"Prediction completed: {risk} Risk", "success")

        return render_template(
            "result.html",
            risk=risk,
            confidence=confidence,
            explanation=explanation,
            fuel_cost=fuel_cost,
            data={
                "supplier": supplier,
                "region": region,
                "transport": transport,
                "delay": delay,
                "weather": weather,
                "demand": demand,
                "inventory": inventory,
                "traffic": traffic,
                "port_delay": port_delay,
                "order_value": order_value
            }
        )

    return render_template("predict.html")

# ---------------- HISTORY ----------------
@app.route("/history")
@login_required
def history():
    if "user" not in session:
        return redirect("/")

    # Server-side pagination: load no more than 20 records per request.
    per_page = 20
    page = request.args.get("page", 1, type=int)
    page = max(page or 1, 1)
    search = request.args.get("search", "", type=str).strip()
    risk_filter = request.args.get("risk", "", type=str).strip().title()
    if risk_filter not in ("", "High", "Medium", "Low"):
        risk_filter = ""

    where_parts = ["user_id = ?"]
    params = [current_user_id()]

    if search:
        like = f"%{search}%"

        # Search both stored numeric values and the labels shown in the table.
        # For example, transport is stored as 2 but displayed as "Ship".
        search_columns = [
            "CAST(id AS TEXT)",
            "CAST(date AS TEXT)",
            "CAST(supplier AS TEXT)",
            "CAST(region AS TEXT)",
            """CASE region
                WHEN 0 THEN 'Asia'
                WHEN 1 THEN 'Europe'
                WHEN 2 THEN 'North America'
                WHEN 3 THEN 'South America'
                WHEN 4 THEN 'Africa'
                ELSE 'Unknown' END""",
            "CAST(transport AS TEXT)",
            """CASE transport
                WHEN 0 THEN 'Truck'
                WHEN 1 THEN 'Rail'
                WHEN 2 THEN 'Ship'
                WHEN 3 THEN 'Air'
                ELSE 'Unknown' END""",
            "CAST(delay AS TEXT)",
            "CAST(weather AS TEXT)",
            """CASE weather
                WHEN 0 THEN 'Clear'
                WHEN 1 THEN 'Rain'
                WHEN 2 THEN 'Storm'
                WHEN 3 THEN 'Snow Fog'
                WHEN 4 THEN 'Fog'
                ELSE 'Unknown' END""",
            "CAST(inventory AS TEXT)",
            "CAST(order_value AS TEXT)",
            "CAST(risk AS TEXT)",
            "CAST(demand AS TEXT)",
            "CAST(traffic AS TEXT)",
            "CAST(port_delay AS TEXT)",
            "CAST(fuel_cost AS TEXT)"
        ]

        where_parts.append(
            "(" + " OR ".join(f"{column} LIKE ?" for column in search_columns) + ")"
        )
        params.extend([like] * len(search_columns))

    if risk_filter:
        where_parts.append("risk = ?")
        params.append(risk_filter)

    where_sql = (" WHERE " + " AND ".join(where_parts)) if where_parts else ""

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM predictions" + where_sql, params)
    total_records = cursor.fetchone()[0] or 0
    total_pages = max(1, (total_records + per_page - 1) // per_page)
    page = min(page, total_pages)
    offset = (page - 1) * per_page

    cursor.execute(
        "SELECT * FROM predictions" + where_sql + " ORDER BY id DESC LIMIT ? OFFSET ?",
        params + [per_page, offset]
    )
    rows = cursor.fetchall()
    conn.close()

    data = [{
        "id": r[0], "date": r[1], "supplier": r[2], "region": r[3],
        "transport": r[4], "delay": r[5], "weather": r[6], "demand": r[7],
        "inventory": r[8], "traffic": r[9], "port_delay": r[10],
        "order_value": r[11], "fuel_cost": r[12], "risk_level": r[13]
    } for r in rows]

    return render_template(
        "history.html", data=data, page=page, per_page=per_page,
        total_records=total_records, total_pages=total_pages,
        search=search, risk_filter=risk_filter,
        start_record=(offset + 1 if total_records else 0),
        end_record=min(offset + len(data), total_records)
    )

@app.route("/export_excel")
@login_required
def export_excel_route():
    if "user" not in session:
        return redirect("/")

    return export_excel(DB_PATH, current_user_id())

@app.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete_single(id):
    if "user" not in session:
        return {"status": "unauthorized"}, 401

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM predictions WHERE id = ? AND user_id = ?", (id, current_user_id()))
    conn.commit()
    conn.close()

    return {"status": "success"}

@app.route("/delete_all", methods=["POST"])
@login_required
def delete_all():
    if "user" not in session:
        return {"status": "unauthorized"}, 401

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM predictions WHERE user_id = ?", (current_user_id(),))
    conn.commit()
    conn.close()

    return {"status": "success"}

@app.route("/save-dashboard-image", methods=["POST"])
@login_required
def save_dashboard_image():
    import os, base64
    from flask import request, jsonify

    data = request.get_json(silent=True) or {}
    image = data.get("image", "")
    if not image.startswith("data:image/png;base64,"):
        return jsonify({"status": "error", "message": "Invalid image data"}), 400
    try:
        image_bytes = base64.b64decode(image.split(",", 1)[1], validate=True)
    except (ValueError, IndexError):
        return jsonify({"status": "error", "message": "Invalid image data"}), 400
    if len(image_bytes) > 10 * 1024 * 1024:
        return jsonify({"status": "error", "message": "Image is too large"}), 413

    downloads_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Downloads")
    os.makedirs(downloads_path, exist_ok=True)
    filename = f"dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    file_path = os.path.join(downloads_path, filename)
    with open(file_path, "wb") as image_file:
        image_file.write(image_bytes)
    return jsonify({"status": "saved", "filename": filename})

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)