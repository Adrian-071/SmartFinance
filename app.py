from flask import Flask, render_template, request, jsonify, redirect, url_for
from models import db, Usuario, Proyecto
from services import calcular_vpn, calcular_tir
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

app = Flask(__name__)

app.config["SECRET_KEY"] = "clave_super_segura"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///finova.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))


# 🔥 RUTA PRINCIPAL (SIN LOGIN PARA EVITAR ERROR EN RENDER)
@app.route("/")
def index():
    return render_template("index.html")


# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = Usuario.query.filter_by(username=request.form["username"]).first()

        if user and user.check_password(request.form["password"]):
            login_user(user)
            return redirect("/")

    return render_template("auth.html")


# REGISTER
@app.route("/register", methods=["POST"])
def register():
    user_exist = Usuario.query.filter_by(username=request.form["username"]).first()

    if user_exist:
        return redirect("/login")

    nuevo = Usuario(
        username=request.form["username"]
    )

    nuevo.set_password(request.form["password"])

    db.session.add(nuevo)
    db.session.commit()

    return redirect("/login")


# LOGOUT
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")


# CALCULAR VPN Y TIR
@app.route("/calcular", methods=["POST"])
@login_required
def calcular():

    data = request.json

    try:
        inversion = float(data["inversion"])
        tasa = float(data["tasa"])

        flujos = [float(f) for f in data["flujos"] if f != ""]
        flujos = [inversion] + flujos

        if len(flujos) < 2:
            return jsonify({"error": "Debes ingresar al menos un flujo"})

        vpn = calcular_vpn(flujos, tasa)
        tir = calcular_tir(flujos)

        if tir is None:
            analisis = "No se pudo calcular la TIR. Flujos inconsistentes."
        elif vpn > 0 and tir > tasa:
            analisis = "Excelente inversión. Genera valor y supera la tasa esperada."
        elif vpn > 0:
            analisis = "Proyecto rentable pero moderado."
        elif vpn < 0 and tir > tasa:
            analisis = "Resultados inconsistentes, revisar datos."
        else:
            analisis = "No recomendable. Destruye valor."

        nuevo = Proyecto(
            inversion=inversion,
            tasa=tasa,
            vpn=vpn,
            tir=tir,
            analisis=analisis,
            usuario_id=current_user.id
        )

        db.session.add(nuevo)
        db.session.commit()

        tasas = [i / 100 for i in range(1, 50)]
        vpns = [calcular_vpn(flujos, t) for t in tasas]

        return jsonify({
            "vpn": round(vpn, 2),
            "tir": round(tir * 100, 2) if tir else 0,
            "analisis": analisis,
            "tasas": tasas,
            "vpns": vpns
        })

    except:
        return jsonify({"error": "Datos inválidos"})


# HISTORIAL
@app.route("/historial")
@login_required
def historial():

    proyectos = Proyecto.query.filter_by(usuario_id=current_user.id).all()

    data = []
    for p in proyectos:
        data.append({
            "vpn": round(p.vpn, 2),
            "tir": round(p.tir * 100, 2) if p.tir else 0,
            "fecha": p.fecha.strftime("%Y-%m-%d")
        })

    return jsonify(data)


# CREAR BD Y RUN LOCAL
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)