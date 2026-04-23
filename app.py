from flask import Flask, render_template, request

app = Flask(__name__)

# 🔹 VPN
def calcular_vpn(flujos, tasa):
    return sum(flujos[t] / ((1 + tasa) ** t) for t in range(len(flujos)))

# 🔹 TIR
def calcular_tir(flujos, r=0.1, tol=1e-6, max_iter=100):
    for _ in range(max_iter):
        f = sum(flujos[t] / (1 + r) ** t for t in range(len(flujos)))
        df = sum(-t * flujos[t] / (1 + r) ** (t + 1) for t in range(len(flujos)))

        if df == 0:
            return None

        nuevo_r = r - f / df

        if abs(nuevo_r - r) < tol:
            return nuevo_r

        r = nuevo_r

    return None

@app.route("/", methods=["GET", "POST"])
def index():
    resultado = None
    grafica = None

    if request.method == "POST":
        try:
            inversion = float(request.form["inversion"])
            tasa = float(request.form["tasa"])
            flujos = [inversion] + [float(x) for x in request.form["flujos"].split(",")]

            vpn = calcular_vpn(flujos, tasa)
            tir = calcular_tir(flujos)

            decision = "✅ CONVIENE INVERTIR" if vpn > 0 else "❌ NO CONVIENE"

            # 📊 Datos para gráfica
            tasas = [i / 100 for i in range(1, 50)]
            vpns = [calcular_vpn(flujos, t) for t in tasas]

            grafica = {
                "tasas": tasas,
                "vpns": vpns
            }

            resultado = {
                "vpn": round(vpn, 2),
                "tir": round(tir * 100, 2) if tir else None,
                "decision": decision
            }

        except:
            resultado = {"error": "Datos inválidos"}

    return render_template("index.html", resultado=resultado, grafica=grafica)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)