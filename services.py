def calcular_vpn(flujos, tasa):
    vpn = 0
    for t in range(len(flujos)):
        vpn += flujos[t] / ((1 + tasa) ** t)
    return vpn


def calcular_tir(flujos, tol=1e-6, max_iter=1000):
    if not any(f > 0 for f in flujos) or not any(f < 0 for f in flujos):
        return None

    r = 0.1

    for _ in range(max_iter):
        f = 0
        df = 0

        for t in range(len(flujos)):
            f += flujos[t] / (1 + r) ** t
            df += -t * flujos[t] / (1 + r) ** (t + 1)

        if abs(df) < 1e-10:
            return None

        nuevo_r = r - f / df

        if abs(nuevo_r - r) < tol:
            return nuevo_r

        r = nuevo_r

    return None


def analizar_inversion(vpn, tir, tasa, flujos):
    if tir is None:
        return "No se pudo calcular la TIR. Flujos inconsistentes."

    negativos = sum(1 for f in flujos[1:] if f < 0)
    total = len(flujos) - 1

    if total == 0:
        riesgo = "Desconocido"
    else:
        ratio = negativos / total
        if ratio == 0:
            riesgo = "Bajo"
        elif ratio <= 0.4:
            riesgo = "Medio"
        else:
            riesgo = "Alto"

    if vpn > 0 and tir > tasa:
        if riesgo == "Bajo":
            return "Excelente inversión: alta rentabilidad y bajo riesgo."
        elif riesgo == "Medio":
            return "Buena inversión con riesgo moderado."
        else:
            return "Rentable pero con riesgo elevado."

    elif vpn > 0:
        return "Genera valor pero con rendimiento moderado."

    elif vpn < 0 and tir > tasa:
        return "Resultados inconsistentes, revisar datos."

    else:
        return "No recomendable. Destruye valor."