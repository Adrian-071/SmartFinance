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

            decision = "CONVIENE INVERTIR" if vpn > 0 else "NO CONVIENE"

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