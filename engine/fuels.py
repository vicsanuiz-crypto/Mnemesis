"""Motor de combustibles: energia, coste, emisiones y ajuste a mercado.

Tesis de diseno
---------------
"Potencial de comercializacion" no existe en abstracto. Un combustible es
brillante o inutil SEGUN EL MERCADO. El hidrogeno liquido es el rey en masa y un
desastre en volumen: excelente para un cohete, ruinoso para un portacontenedores.
Por eso aqui nada se puntua en el vacio: cada candidato se puntua contra un
PERFIL DE MERCADO con pesos explicitos y auditables.

Los combustibles metalicos se derivan de la tabla periodica, no se copian de
ningun sitio: energia = |DHf(oxido)| / masa de metal. Eso los mantiene
consistentes con data/elements.py y permite verificarlos uno a uno.
"""

from data.elements import get
from data.fuels import OXIDES, REFERENCE_FUELS, DHF_H2O_GAS

MJ_PER_KWH = 3.6

# Fraccion de volumen que ocupa realmente un polvo metalico apilado. Un polvo
# esferico bien compactado ronda 0.60-0.64; se usa 0.60 por prudencia. Ignorarlo
# inflaria la densidad volumetrica de todos los metales un 65%.
POWDER_PACKING = 0.60

# Metales con ciclo cerrado demostrado: su oxido se puede reducir de vuelta a
# metal con electricidad o hidrogeno renovables, asi que funcionan como
# VECTOR de energia recargable, no como combustible consumido.
# (Fe: TU Eindhoven / Metalot, ciclo con H2 verde. Zn/Al: solar termoquimico ETH.)
REGENERABLE = {"Fe", "Zn", "Al", "Mg", "Si", "B"}

# Perfiles de mercado. Los pesos suman 1 y estan a la vista a proposito: son la
# unica parte subjetiva de todo el motor y el usuario debe poder discutirlos.
MARKETS = {
    "aviacion": dict(
        name="Aviacion comercial",
        why="El avion paga cada kilo y cada litro. Un combustible que pese mas "
            "reduce carga de pago; uno que ocupe mas no cabe en el ala.",
        w=dict(gravimetric=0.35, volumetric=0.25, cost=0.15, co2=0.10, trl=0.10, safety=0.05)),
    "maritimo": dict(
        name="Transporte maritimo",
        why="El buque tiene volumen de sobra y margenes finos. Manda el coste "
            "por kWh y la normativa de la OMI sobre emisiones.",
        w=dict(gravimetric=0.00, volumetric=0.25, cost=0.30, co2=0.25, trl=0.10, safety=0.10)),
    "automocion": dict(
        name="Automocion",
        why="El deposito es pequeno y el cliente mira el precio en el surtidor. "
            "Densidad volumetrica y coste por encima de todo.",
        w=dict(gravimetric=0.05, volumetric=0.30, cost=0.25, co2=0.20, trl=0.15, safety=0.05)),
    "ramjet": dict(
        name="Propulsion volumetrica (ramjet, misil, torpedo)",
        why="Aqui el volumen es la unica restriccion dura: el fuselaje esta dado. "
            "Es el unico mercado donde el boro tiene sentido economico.",
        w=dict(gravimetric=0.15, volumetric=0.55, cost=0.05, co2=0.00, trl=0.15, safety=0.10)),
    "red": dict(
        name="Almacenamiento estacionario de red",
        why="El terreno es barato y el ciclo es largo. Solo importan el coste "
            "del kWh almacenado y que la tecnologia exista ya.",
        w=dict(gravimetric=0.00, volumetric=0.05, cost=0.45, co2=0.25, trl=0.20, safety=0.05)),
    "industrial": dict(
        name="Calor industrial de alta temperatura",
        why="Cemento, acero y vidrio necesitan llama de 1400 C sin carbono. "
            "Coste y madurez mandan; el volumen del deposito da igual.",
        w=dict(gravimetric=0.00, volumetric=0.05, cost=0.35, co2=0.30, trl=0.20, safety=0.10)),
}


def metal_fuel(sym):
    """Deriva un combustible metalico desde la tabla periodica.

    energia = |DHf(oxido)| / (moles de metal * masa atomica)
    Se comprueba contra valores publicados en tests/test_engine.py.
    """
    el = get(sym)
    if sym not in OXIDES:
        raise ValueError(f"No hay estequiometria de oxido para {sym}")
    oxide, x, y = OXIDES[sym]
    dhox = el["dHox"]
    if dhox is None:
        raise ValueError(f"{sym} no tiene entalpia de oxido tabulada")
    dhf = DHF_H2O_GAS if sym == "H" else dhox * y   # H2: PCI usa agua vapor
    lhv = abs(dhf) / (x * el["mass"])               # kJ/g == MJ/kg
    if sym == "H":
        return None  # el hidrogeno ya entra por REFERENCE_FUELS con su almacenamiento

    return dict(
        id=f"metal_{sym.lower()}", name=f"{el['name']} en polvo", formula=sym,
        cls="metal", lhv=round(lhv, 2),
        rho_store=round(el["rho"] * 1000 * POWDER_PACKING, 0),
        store=f"polvo solido a granel (empaquetado {POWDER_PACKING:.0%})",
        penalty=0.0, co2=0.0, price=el["price"], trl=_metal_trl(sym), tox=el["tox"],
        oxide=oxide, regenerable=sym in REGENERABLE,
        note=_metal_note(sym, el, oxide),
    )


def _metal_trl(sym):
    """Madurez como combustible de COMBUSTION CONTINUA, que es el uso que se
    esta evaluando. No confundir con su madurez en otros usos: el aluminio en
    propulsante solido de cohete es TRL 9 desde hace decadas, pero quemarlo de
    forma continua y controlada en un quemador sigue sin resolverse, y ese es
    el escenario que puntuamos aqui. Poner 8 contradecia nuestra propia nota."""
    return {"Fe": 5, "Al": 5, "Mg": 4, "Zn": 4, "B": 3, "Si": 3,
            "Li": 2, "Ti": 2}.get(sym, 1)


def _metal_note(sym, el, oxide):
    base = {
        "Al": "Ya se quema a escala industrial: el 15-20% de la masa de un propulsor "
              "solido de cohete es aluminio. Fuera de eso, encender y controlar polvo "
              "de aluminio en un quemador continuo sigue sin resolverse.",
        "Fe": "El caso mas serio de combustible metalico civil. Densidad volumetrica "
              "altisima pese a su pobre energia por kilo, oxido solido y capturable al "
              "100%, y reduccion de vuelta a hierro con hidrogeno verde. Ya hay una "
              "cervecera en Paises Bajos funcionando con calor de polvo de hierro.",
        "B": "El mayor contenido energetico por litro de toda la quimica conocida. "
             "Su problema es de cinetica, no de energia: la capa de B2O3 fundido "
             "asfixia la particula y retrasa la combustion.",
        "Mg": "Arde con facilidad y bajo punto de ignicion, por eso se usa en "
              "bengalas y en torpedos con ciclo agua-magnesio.",
        "Si": "Abundantisimo y con buena energia por litro, pero su oxido es un vidrio "
              "refractario que bloquea la combustion completa.",
        "Zn": "Poca energia, pero su ciclo ZnO -> Zn con calor solar concentrado esta "
              "demostrado en planta piloto.",
        "Li": "Energia excelente, pero reacciona con nitrogeno, agua y CO2 a la vez. "
              "Solo tiene sentido en sistemas cerrados.",
    }.get(sym)
    if base:
        return base
    return (f"Derivado de la tabla periodica ({el['name']} -> {oxide}). "
            "Sin desarrollo conocido como combustible: figura para comparar.")


def blend(components, name, note="", trl=None):
    """Mezcla por fracciones MASICAS. components = {id_o_sym: fraccion}.

    OJO con las mezclas de gases: la industria las cita casi siempre en
    VOLUMEN, y la diferencia es brutal. Un hythane del 20% en volumen de
    hidrogeno es solo un 3% en masa, porque el hidrogeno es ocho veces mas
    ligero que el metano. Confundirlos infla el PCI de la mezcla un 40%.

    La densidad de una mezcla se calcula por volumenes (1/sum(wi/rhoi)), NO
    promediando densidades: promediar densidades es un error clasico que puede
    desviar el resultado un 20%.
    """
    catalogue = {f["id"]: f for f in all_base_fuels()}
    total = sum(components.values())
    if abs(total - 1.0) > 1e-6:
        components = {k: v / total for k, v in components.items()}

    parts = []
    for key, w in components.items():
        f = catalogue.get(key) or catalogue.get(f"metal_{key.lower()}")
        if f is None:
            raise ValueError(f"Componente desconocido en la mezcla: {key}")
        parts.append((w, f))

    lhv = sum(w * f["lhv"] for w, f in parts)
    rho = 1.0 / sum(w / f["rho_store"] for w, f in parts)
    co2 = (sum(w * f["lhv"] * f["co2"] for w, f in parts) / lhv) if lhv else 0.0
    price = sum(w * f["price"] for w, f in parts)
    penalty = sum(w * f["lhv"] * f["penalty"] for w, f in parts) / lhv if lhv else 0.0
    return dict(
        id="mix_" + "_".join(sorted(components)), name=name, cls="formulacion",
        formula=" + ".join(f"{w:.0%} {f['formula']}" for w, f in parts),
        lhv=round(lhv, 2), rho_store=round(rho, 0),
        store="; ".join(sorted({f["store"] for _, f in parts})),
        penalty=round(penalty, 3), co2=round(co2, 1), price=round(price, 3),
        # La madurez de una mezcla la marca su componente MENOS maduro: la
        # cadena se rompe por el eslabon debil, no por la media.
        trl=trl if trl is not None else min(f["trl"] for _, f in parts),
        tox=max(f["tox"] for _, f in parts),
        regenerable=all(f.get("regenerable") for _, f in parts),
        components={f["name"]: round(w, 3) for w, f in parts},
        note=note,
    )


def all_base_fuels():
    """Referencia tabulada + metales derivados de la tabla periodica."""
    out = [dict(f, regenerable=f.get("regenerable", False)) for f in REFERENCE_FUELS]
    for sym in ("Al", "Fe", "B", "Mg", "Si", "Zn", "Li", "Ti", "Ca", "Zr", "Ce"):
        m = metal_fuel(sym)
        if m:
            out.append(m)
    return out


def enrich(f):
    """Anade las magnitudes derivadas que realmente se comparan."""
    usable = f["lhv"] * (1.0 - f["penalty"])          # MJ/kg netos tras almacenar
    vol = f["lhv"] * f["rho_store"] / 1000.0           # MJ/L (rho en kg/m3)
    usable_vol = vol * (1.0 - f["penalty"])
    cost_kwh = f["price"] / (usable / MJ_PER_KWH) if usable > 0 else None
    return dict(
        f,
        usable_MJ_kg=round(usable, 2),
        MJ_per_L=round(vol, 2),
        usable_MJ_L=round(usable_vol, 2),
        cost_usd_kwh=round(cost_kwh, 4) if cost_kwh else None,
        co2_kg_per_MWh=round(f["co2"] * MJ_PER_KWH, 1),
        safety=round(_safety(f), 2),
    )


def _safety(f):
    """Indice de seguridad 0-10. Es una HEURISTICA declarada, no una norma.
    Penaliza toxicidad, criogenia, alta presion y los solidos pirofóricos."""
    s = 10.0 - 2.2 * f["tox"]
    store = f["store"].lower()
    if "20 k" in store or "111 k" in store:
        s -= 1.5                      # criogenia
    if "700 bar" in store:
        s -= 2.0                      # alta presion
    elif "bar" in store:
        s -= 0.7
    if f["cls"] == "metal":
        s -= 1.0                      # polvo metalico: riesgo de explosion de polvo
    return max(0.0, min(10.0, s))


def score_market(fuels, market_key):
    """Puntua un conjunto de combustibles contra un perfil de mercado.

    Normalizacion min-max DENTRO del conjunto evaluado. Consecuencia que hay que
    tener presente: la puntuacion es RELATIVA. Anadir o quitar candidatos cambia
    las notas de todos. Es comparacion entre iguales, no una nota absoluta.
    """
    if market_key not in MARKETS:
        raise KeyError(f"Mercado desconocido: {market_key}. Hay: {list(MARKETS)}")
    w = MARKETS[market_key]["w"]

    crit = {
        "gravimetric": ([f["usable_MJ_kg"] for f in fuels], True),
        "volumetric":  ([f["usable_MJ_L"] for f in fuels], True),
        "cost":        ([f["cost_usd_kwh"] for f in fuels], False),
        "co2":         ([f["co2"] for f in fuels], False),
        "trl":         ([f["trl"] for f in fuels], True),
        "safety":      ([f["safety"] for f in fuels], True),
    }
    # El coste por kWh abarca cuatro ordenes de magnitud en este conjunto
    # (0.014 USD/kWh el carbon, 61 el boro). Con normalizacion lineal, el
    # outlier caro aplasta la escala y el carbon y el aluminio -- que se llevan
    # un factor 20 -- acaban practicamente empatados en el eje de coste.
    # En magnitudes que abarcan decadas se normaliza en logaritmo.
    import math
    LOG_SCALE = {"cost"}

    norm = {}
    for k, (vals, higher_better) in crit.items():
        use_log = k in LOG_SCALE
        prep = [(math.log10(max(v, 1e-9)) if use_log else v) if v is not None else None
                for v in vals]
        clean = [v for v in prep if v is not None]
        lo, hi = min(clean), max(clean)
        span = hi - lo
        norm[k] = []
        for v in prep:
            if v is None:
                norm[k].append(0.0)
            elif span == 0:
                norm[k].append(0.5)
            else:
                x = (v - lo) / span
                norm[k].append(x if higher_better else 1.0 - x)

    out = []
    for i, f in enumerate(fuels):
        breakdown = {k: round(norm[k][i], 3) for k in crit}
        total = sum(w[k] * norm[k][i] for k in crit)
        out.append(dict(f, market=market_key, score=round(100 * total, 1),
                        breakdown=breakdown))
    out.sort(key=lambda f: -f["score"])
    for rank, f in enumerate(out, 1):
        f["rank"] = rank
    return out
