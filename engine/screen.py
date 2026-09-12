"""Cribado: de 130.000 composiciones a una lista corta defendible.

El embudo tiene tres filtros en cascada, del mas barato al mas caro:

  1. FISICA      Tiene que poder existir. Criterio de Yang-Zhang: si no forma
                 disolucion solida, fuera. Aqui muere el 80-90%.
  2. ENTORNO     Tiene que sobrevivir al sitio donde va a trabajar. Se somete a
                 los bancos de ensayo del objetivo. Un fallo duro elimina.
  3. ECONOMIA    Tiene que poder venderse: coste, suministro, toxicidad y
                 facilidad de fabricacion.

El orden importa: evaluar la economia de una aleacion que no existe es tirar
computo. Y al reves, ordenar por fisica sin mirar el precio produce listas
preciosas de aleaciones de renio a 3.000 USD/kg que no fabricara nadie.
"""

from data.elements import get
from environments import run

# Objetivos industriales. Cada uno ata una paleta a unos entornos obligatorios
# y a unos pesos de propiedad. Todo explicito y discutible.
TARGETS = {
    "turbina": dict(
        name="Alabe de turbina de nueva generacion",
        palette="refractarias", envs=["turbina"],
        thesis="Cada 50 K de aumento en la temperatura de entrada de turbina "
               "valen ~1% de rendimiento termico. El mercado paga por ese 1%.",
        props=dict(tm=0.40, oxidation=0.30, density=0.10, stiffness=0.20),
        max_price=400),
    "hidrogeno": dict(
        name="Tanque y conduccion de hidrogeno",
        palette="criogenicas", envs=["criogenia", "motor_h2"],
        thesis="Toda la economia del hidrogeno depende de metal que no se "
               "fragilice. Es el cuello de botella material del sector.",
        props=dict(stiffness=0.30, density=0.25, tm=0.10, oxidation=0.35),
        max_price=100),
    "marino": dict(
        name="Estructura marina de 25 anos sin mantenimiento",
        palette="marinas", envs=["fondo_marino"],
        thesis="Una torre eolica marina cuesta mas en mantenimiento que en "
               "acero. Un material que no necesite inspeccion cambia el negocio.",
        props=dict(stiffness=0.35, density=0.15, oxidation=0.30, tm=0.20),
        max_price=80),
    "nuclear": dict(
        name="Vaina y estructura de reactor",
        palette="nucleares", envs=["reactor_nuclear"],
        thesis="Los reactores modulares pequenos necesitan materiales de vaina "
               "mas tolerantes al accidente que el Zircaloy tras Fukushima.",
        props=dict(tm=0.35, oxidation=0.35, stiffness=0.20, density=0.10),
        max_price=200),
    "aeroestructura": dict(
        name="Estructura aeronautica ligera",
        palette="ligeras", envs=["ambiente"],
        thesis="Un kilo menos en un fuselaje vale ~3.000 USD de combustible "
               "ahorrado a lo largo de la vida del avion.",
        props=dict(stiffness=0.50, density=0.30, tm=0.05, oxidation=0.15),
        max_price=120),
    "electrolizador": dict(
        name="Componente de electrolizador PEM",
        palette="nobles", envs=["electrolizador"],
        thesis="El iridio del anodo es el cuello de botella fisico del "
               "hidrogeno verde: la produccion mundial no da para los "
               "gigavatios planificados. Sustituirlo vale una fortuna.",
        props=dict(oxidation=0.45, stiffness=0.20, tm=0.20, density=0.15),
        max_price=20000),
}

# Penalizacion por dificultad de fabricacion. No es cosmetica: una aleacion que
# funde a 3000 K exige horno de haz de electrones en vacio, y una con delta alto
# segrega al solidificar. Ambas cosas multiplican el coste por diez.
def manufacturability(a):
    score = 100.0
    notes = []
    if a["tm_mean_K"] > 2600:
        score -= 35; notes.append("funde por encima de 2600 K: exige fusion por haz de electrones en vacio")
    elif a["tm_mean_K"] > 2100:
        score -= 15; notes.append("funde por encima de 2100 K: horno de arco en atmosfera inerte")
    if a["delta_pct"] > 5.0:
        score -= 20; notes.append(f"desajuste atomico {a['delta_pct']}%: segregacion probable al solidificar")
    if a["n_elements"] >= 5:
        score -= 10; notes.append("5 o mas elementos: control de composicion mas caro")
    if a["price_usd_kg"] > 500:
        score -= 15; notes.append("materia prima cara: el desperdicio de mecanizado pesa mucho")
    return max(0.0, score), notes


def supply_risk(a):
    """Riesgo de suministro. Abundancia en la corteza y lista de materias primas
    criticas de la UE. Un material excelente hecho de disprosio es un material
    que China puede apagar."""
    comp = a["composition"]
    # Media geometrica ponderada de la abundancia: castiga fuerte que UN solo
    # componente sea rarisimo, que es como funciona de verdad una cadena de
    # suministro (se rompe por el eslabon escaso, no por el promedio).
    import math
    log_ab = sum(comp[s] * math.log10(max(get(s)["abund_ppm"], 1e-6)) for s in comp)
    base = min(100.0, max(0.0, (log_ab + 4.0) / 9.0 * 100.0))
    crit_frac = sum(comp[s] for s in comp if get(s)["crit"])
    score = base * (1.0 - 0.4 * crit_frac)
    return round(score, 1), round(crit_frac, 3)


def _norm(vals, higher_better=True):
    clean = [v for v in vals if v is not None]
    if not clean:
        return [0.5] * len(vals)
    lo, hi = min(clean), max(clean)
    span = hi - lo
    out = []
    for v in vals:
        if v is None:
            out.append(0.0)
        elif span == 0:
            out.append(0.5)
        else:
            x = (v - lo) / span
            out.append(x if higher_better else 1.0 - x)
    return out


_OX_SCORE = {"alumina": 1.0, "silice": 0.8, "cromia": 0.7, "noble": 0.9, "sin_proteccion": 0.0}


def screen(candidates, target_key, top=40):
    """Ejecuta el embudo completo. Devuelve (lista corta, estadisticas)."""
    t = TARGETS[target_key]
    stats = {"entrada": len(candidates)}

    # --- Filtro 1: fisica -------------------------------------------------
    phase_ok = [a for a in candidates if a["phase"] == "disolucion_solida"]
    stats["tras_fisica"] = len(phase_ok)

    # --- Filtro 1b: precio (barato de aplicar, quita mucho) ---------------
    priced = [a for a in phase_ok if a["price_usd_kg"] <= t["max_price"]]
    stats["tras_precio"] = len(priced)

    # --- Filtro 2: entorno ------------------------------------------------
    survivors = []
    for a in priced:
        acts = {e: run(a, e) for e in t["envs"]}
        if any(act["failures"] for act in acts.values()):
            continue
        scores = [act["score"] for act in acts.values() if act["score"] is not None]
        a = dict(a, env_reports=acts,
                 env_score=round(sum(scores) / len(scores), 1) if scores else None,
                 env_unknowns=sorted({u for act in acts.values() for u in act["unknowns"]}))
        survivors.append(a)
    stats["tras_entorno"] = len(survivors)
    if not survivors:
        return [], stats

    # --- Filtro 3: puntuacion compuesta -----------------------------------
    w = t["props"]
    n_tm = _norm([a["tm_mean_K"] for a in survivors], True)
    n_rho = _norm([a["density"] for a in survivors], False)
    n_st = _norm([a["specific_stiffness"] for a in survivors], True)
    n_ox = [_OX_SCORE.get(a["oxidation"]["class"], 0.0) for a in survivors]
    n_price = _norm([a["price_usd_kg"] for a in survivors], False)

    out = []
    for i, a in enumerate(survivors):
        perf = (w["tm"] * n_tm[i] + w["density"] * n_rho[i]
                + w["stiffness"] * n_st[i] + w["oxidation"] * n_ox[i])
        manu, manu_notes = manufacturability(a)
        supply, crit_frac = supply_risk(a)
        # Comercial = puede venderse. Tecnico = funciona. Se separan a proposito:
        # mezclarlos esconde el motivo por el que un candidato sube o baja.
        commercial = 0.45 * n_price[i] * 100 + 0.30 * supply + 0.25 * manu
        tox_pen = 1.0 - 0.15 * len(a["toxic_elements"])
        total = (0.50 * perf * 100 + 0.25 * (a["env_score"] or 0)
                 + 0.25 * commercial) * tox_pen
        out.append(dict(
            a, target=target_key,
            perf_score=round(perf * 100, 1),
            commercial_score=round(commercial, 1),
            manufacturability=round(manu, 1), manufacturability_notes=manu_notes,
            supply_score=supply, critical_fraction=crit_frac,
            score=round(total, 1),
            breakdown=dict(tm=round(n_tm[i], 3), density=round(n_rho[i], 3),
                           stiffness=round(n_st[i], 3), oxidation=round(n_ox[i], 3),
                           price=round(n_price[i], 3)),
        ))
    out.sort(key=lambda a: -a["score"])

    # --- Diversidad: no devolver 40 variantes del mismo sistema -----------
    # Sin esto, el top se llena de la misma familia con ratios ligeramente
    # distintos y la lista corta no aporta informacion nueva.
    seen, short = {}, []
    for a in out:
        fam = "".join(sorted(a["composition"]))
        if seen.get(fam, 0) >= 2:
            continue
        seen[fam] = seen.get(fam, 0) + 1
        short.append(a)
        if len(short) >= top:
            break
    for rank, a in enumerate(short, 1):
        a["rank"] = rank
    stats["familias_distintas"] = len(seen)
    stats["lista_corta"] = len(short)
    return short, stats
