"""Generador combinatorio: de la tabla periodica a candidatos priorizados.

Estrategia
----------
No se generan combinaciones "a lo bruto" de los 70 elementos: C(70,5) son 12
millones de composiciones, la inmensa mayoria absurdas (nadie va a alear cesio
con osmio). Se parte de PALETAS con intencion metalurgica -- conjuntos de
elementos que la literatura ya ha demostrado que juegan bien juntos para un fin
concreto -- y dentro de cada paleta se barre exhaustivamente.

Esto es exactamente como trabaja el cribado computacional real: el espacio se
acota con conocimiento del dominio y luego se barre sin piedad.
"""

import itertools

from alloys import CompositionError, evaluate

# Paletas de partida. Cada una responde a un objetivo industrial concreto.
PALETTES = {
    "refractarias": dict(
        name="Refractarias de alta temperatura",
        goal="Superar el techo de 1400 K de las superaleaciones de niquel en "
             "turbinas y motores hipersonicos.",
        pool=["Nb", "Mo", "Ta", "W", "V", "Cr", "Ti", "Zr", "Hf", "Re", "Al", "Si"],
        sizes=(4, 5)),
    "ligeras": dict(
        name="Estructurales ligeras",
        goal="Maxima rigidez por unidad de masa para aeronautica y transporte.",
        pool=["Al", "Ti", "Mg", "Li", "Si", "Sc", "Zn", "Cu", "Mn", "Zr", "V", "Cr"],
        sizes=(4, 5)),
    "criogenicas": dict(
        name="Criogenicas y compatibles con hidrogeno",
        goal="Aguantar 20 K y atmosfera de hidrogeno sin fragilizarse: tanques "
             "y conducciones de la economia del hidrogeno.",
        pool=["Fe", "Ni", "Cr", "Mn", "Co", "Cu", "Al", "Ti", "Nb", "Mo", "V", "Zn"],
        sizes=(4, 5)),
    "marinas": dict(
        name="Resistentes a agua de mar",
        goal="Eolica marina, desaladoras y submarino: cloruros a presion durante "
             "25 anos sin mantenimiento.",
        pool=["Fe", "Ni", "Cr", "Mo", "W", "Cu", "Ti", "Co", "Mn", "Nb", "Ta", "Al"],
        sizes=(4, 5)),
    "nucleares": dict(
        name="Nucleares de baja captura neutronica",
        goal="Vainas y estructuras internas de reactor: transparentes a los "
             "neutrones y estables bajo irradiacion.",
        pool=["Zr", "Nb", "Mo", "Ti", "V", "Cr", "Fe", "Al", "Si", "Sn", "Y", "Mg"],
        sizes=(3, 4, 5)),
    "nobles": dict(
        name="Catalisis y medios agresivos",
        goal="Electrolizadores y electrodos: sobrevivir a pH 0 con potencial "
             "anodico, hoy dominio exclusivo del iridio y el platino.",
        pool=["Ti", "Nb", "Ta", "Zr", "Pt", "Pd", "Ru", "Ir", "Ni", "Cr", "W", "Mo"],
        sizes=(3, 4)),
}

# Relaciones molares que se barren. Equiatomica mas variantes sesgadas: casi
# todas las HEA industrialmente utiles NO son equiatomicas exactas.
RATIO_SETS = {
    3: [(1, 1, 1), (2, 1, 1), (3, 1, 1), (2, 2, 1)],
    4: [(1, 1, 1, 1), (2, 1, 1, 1), (3, 1, 1, 1), (2, 2, 1, 1)],
    5: [(1, 1, 1, 1, 1), (2, 1, 1, 1, 1), (1, 1, 1, 1, 0.3), (2, 2, 1, 1, 1)],
}


def generate(palette_key, max_price=None, exclude_toxic=False, exclude_radioactive=True):
    """Barre una paleta completa. Devuelve (candidatos_validos, descartes).

    Los descartes se DEVUELVEN, no se tiran. Saber por que se cayeron 4.000
    composiciones vale tanto como el ranking: es donde se ve si un filtro esta
    mal calibrado y se esta tirando algo bueno.
    """
    p = PALETTES[palette_key]
    out, rejected = [], {}
    seen = set()

    for size in p["sizes"]:
        for combo in itertools.combinations(sorted(p["pool"]), size):
            for ratios in RATIO_SETS[size]:
                # Se permutan los ratios para no fijar arbitrariamente cual es
                # el elemento mayoritario.
                for perm in set(itertools.permutations(ratios)):
                    comp = {s: r for s, r in zip(combo, perm) if r > 0}
                    key = tuple(sorted((s, round(r, 3)) for s, r in comp.items()))
                    if key in seen:
                        continue
                    seen.add(key)
                    try:
                        a = evaluate(comp)
                    except CompositionError as exc:
                        reason = str(exc).split(":")[0]
                        rejected[reason] = rejected.get(reason, 0) + 1
                        continue
                    if exclude_radioactive and a["radioactive"]:
                        rejected["radiactivo"] = rejected.get("radiactivo", 0) + 1
                        continue
                    if exclude_toxic and a["toxic_elements"]:
                        rejected["toxico"] = rejected.get("toxico", 0) + 1
                        continue
                    if max_price and a["price_usd_kg"] > max_price:
                        rejected[f"precio > {max_price} USD/kg"] = \
                            rejected.get(f"precio > {max_price} USD/kg", 0) + 1
                        continue
                    a["palette"] = palette_key
                    out.append(a)
    return out, rejected
