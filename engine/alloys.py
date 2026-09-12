"""Motor de aleaciones: de una composicion a una prediccion de fase.

Que hace y que NO hace
----------------------
HACE: aplicar los criterios empiricos que la metalurgia computacional usa para
descartar el 99% de las composiciones antes de gastar un solo euro en horno.
Son reglas publicadas, con su rango de validez y su tasa de acierto conocida.

NO HACE: calcular estructura electronica. Esto no es DFT. Un candidato que pase
todos los filtros es una HIPOTESIS priorizada, no un material verificado. El
paso siguiente real es DFT (VASP/Quantum Espresso) o directamente horno de arco.

Criterios implementados (con su referencia)
-------------------------------------------
delta   Desajuste de tamano atomico. Zhang et al., Adv. Eng. Mater. 10 (2008).
        delta <= 6.6% favorece disolucion solida.
DSmix   Entropia de mezcla configuracional, -R*sum(ci*ln ci).
DHmix   Entalpia de mezcla, sum(4*DH_ij*ci*cj) sobre pares.
Omega   Omega = Tm*DSmix/|DHmix|. Yang & Zhang, Mater. Chem. Phys. 132 (2012).
        Omega >= 1.1 AND delta <= 6.6% => disolucion solida. Acierto reportado
        ~ 85-90% sobre el corpus de HEA conocidas.
VEC     Guo et al., J. Appl. Phys. 109 (2011). VEC >= 8 -> FCC;
        6.87 <= VEC < 8 -> FCC+BCC; VEC < 6.87 -> BCC.
Dchi    Dispersion de electronegatividad de Pauling. Alta => intermetalicos.

Limites honestos de estos criterios
-----------------------------------
1. Son reglas de FORMACION, no de ESTABILIDAD a largo plazo. Muchas HEA que
   cumplen Omega>=1.1 se descomponen tras 1000 h a 900 K.
2. Se calibraron con aleaciones equiatomicas de 5 elementos. Fuera de ahi
   (binarios, composiciones muy sesgadas) pierden precision.
3. No dicen nada de procesabilidad: colabilidad, soldabilidad, conformado.
"""

import math

from data.elements import get
from data.hmix import dh_mix

R_GAS = 8.314462618  # J/(mol K)

# Umbrales de la literatura. Centralizados aqui para que se puedan auditar y
# mover en un solo sitio en vez de estar repartidos por el codigo.
DELTA_SS_MAX = 6.6        # %
OMEGA_SS_MIN = 1.1
VEC_FCC_MIN = 8.0
VEC_BCC_MAX = 6.87
DH_AMORPHOUS = (-49.0, -5.5)   # ventana de Zhang para formacion de vidrio metalico

# Umbrales de formacion de capa protectora de oxido (metalurgia clasica de
# aleaciones resistentes a alta temperatura).
PROTECTIVE_FORMERS = {"Al": 0.05, "Cr": 0.12, "Si": 0.02}

# Elementos que no tienen sentido en una aleacion metalica masiva.
EXCLUDED_FROM_ALLOYS = {"H", "N", "O", "F", "S", "P", "Se", "Hg"}


class CompositionError(ValueError):
    """La composicion no se puede evaluar. Siempre con motivo explicito."""


def normalise(comp):
    """Normaliza fracciones molares a suma 1 y valida la composicion."""
    if not comp:
        raise CompositionError("Composicion vacia")
    bad = [s for s in comp if s in EXCLUDED_FROM_ALLOYS]
    if bad:
        raise CompositionError(f"Elementos no validos en aleacion masiva: {bad}")
    total = sum(comp.values())
    if total <= 0:
        raise CompositionError("Las fracciones suman cero o menos")
    return {s: c / total for s, c in comp.items() if c > 0}


def evaluate(comp, name=None):
    """Evalua una composicion. Devuelve un dict con todas las magnitudes y,
    crucialmente, la trazabilidad de que dato es medido y cual estimado."""
    c = normalise(comp)
    syms = sorted(c, key=lambda s: -c[s])

    els = {s: get(s) for s in syms}
    for s, e in els.items():
        for field in ("r_pm", "tm_K", "rho", "mass", "en", "vec"):
            if e[field] is None:
                raise CompositionError(f"Falta {s}.{field}; no se puede evaluar")

    # --- Desajuste de tamano atomico -------------------------------------
    r_mean = sum(c[s] * els[s]["r_pm"] for s in syms)
    delta = 100.0 * math.sqrt(
        sum(c[s] * (1.0 - els[s]["r_pm"] / r_mean) ** 2 for s in syms)
    )

    # --- Entropia configuracional ----------------------------------------
    ds_mix = -R_GAS * sum(c[s] * math.log(c[s]) for s in syms)

    # --- Entalpia de mezcla ----------------------------------------------
    dh_mix_total = 0.0
    estimated_pairs, unknown_pairs, tier2_pairs = [], [], []
    for i, a in enumerate(syms):
        for b in syms[i + 1:]:
            vm_a = els[a]["mass"] / els[a]["rho"]
            vm_b = els[b]["mass"] / els[b]["rho"]
            val, source, _conf = dh_mix(a, b, vm_a, vm_b)
            if val is None:
                unknown_pairs.append(f"{a}-{b}")
                continue
            if source == "miedema_estimado":
                estimated_pairs.append(f"{a}-{b}")
            elif source == "tabulado_nivel2":
                tier2_pairs.append(f"{a}-{b}")
            dh_mix_total += 4.0 * val * c[a] * c[b]

    if unknown_pairs:
        raise CompositionError(
            "Sin entalpia de mezcla para: " + ", ".join(unknown_pairs)
        )

    # --- Omega ------------------------------------------------------------
    tm_mean = sum(c[s] * els[s]["tm_K"] for s in syms)
    if abs(dh_mix_total) < 1e-6:
        omega = float("inf")  # mezcla ideal: la entropia domina sin oposicion
    else:
        omega = tm_mean * ds_mix / (abs(dh_mix_total) * 1000.0)

    # --- VEC y electronegatividad ----------------------------------------
    vec = sum(c[s] * els[s]["vec"] for s in syms)
    en_mean = sum(c[s] * els[s]["en"] for s in syms)
    d_chi = math.sqrt(sum(c[s] * (els[s]["en"] - en_mean) ** 2 for s in syms))

    # --- Propiedades por regla de mezclas --------------------------------
    m_mean = sum(c[s] * els[s]["mass"] for s in syms)
    v_molar = sum(c[s] * els[s]["mass"] / els[s]["rho"] for s in syms)
    rho = m_mean / v_molar

    k_alloy, k_disorder = _thermal_conductivity(c, els)

    e_vals = [(c[s], els[s]["E_GPa"]) for s in syms if els[s]["E_GPa"] is not None]
    e_cov = sum(w for w, _ in e_vals)
    modulus = sum(w * v for w, v in e_vals) / e_cov if e_cov > 0.5 else None

    price = sum(c[s] * els[s]["mass"] * els[s]["price"] for s in syms) / m_mean

    # --- Fase prevista ----------------------------------------------------
    phase, phase_why = _predict_phase(delta, omega, dh_mix_total, len(syms))
    structure, struct_conf, struct_why = _predict_structure(vec, phase, c, els)

    # --- Indices derivados (indices, NO valores de ensayo) ----------------
    ss_hardening = delta * (modulus if modulus else 100.0) / 100.0
    specific_stiffness = modulus / rho if modulus else None
    oxidation = _oxidation_resistance(c, els)

    return {
        "name": name or _auto_name(c),
        "composition": {s: round(c[s], 4) for s in syms},
        "n_elements": len(syms),
        "delta_pct": round(delta, 2),
        "ds_mix": round(ds_mix, 2),
        "dh_mix": round(dh_mix_total, 2),
        "omega": round(omega, 2) if omega != float("inf") else None,
        "omega_infinite": omega == float("inf"),
        "tm_mean_K": round(tm_mean, 0),
        "vec": round(vec, 2),
        "d_chi": round(d_chi, 3),
        "density": round(rho, 2),
        "k_th": round(k_alloy, 1) if k_alloy else None,
        "k_disorder_factor": round(k_disorder, 2),
        "modulus_GPa": round(modulus, 0) if modulus else None,
        "modulus_coverage": round(e_cov, 2),
        "specific_stiffness": round(specific_stiffness, 2) if specific_stiffness else None,
        "price_usd_kg": round(price, 2),
        "phase": phase,
        "phase_why": phase_why,
        "structure": structure,
        "structure_confidence": struct_conf,
        "structure_why": struct_why,
        "max_fraction": round(max(c.values()), 3),
        "regime": "concentrada" if max(c.values()) <= 0.5 else (
            "diluida" if max(c.values()) < 0.85 else "casi_pura"),
        "ss_hardening_index": round(ss_hardening, 1),
        "oxidation": oxidation,
        "estimated_pairs": estimated_pairs,
        "tier2_pairs": tier2_pairs,
        "data_quality": ("estimado" if estimated_pairs
                         else ("nivel2" if tier2_pairs else "tabulado")),
        "toxic_elements": [s for s in syms if els[s]["tox"] >= 2],
        "critical_elements": [s for s in syms if els[s]["crit"]],
        "radioactive": any(els[s]["radio"] for s in syms),
    }


# Constante de desorden de la correccion tipo Nordheim. Calibrada contra el
# acero inoxidable 316 (ver validacion abajo).
NORDHEIM_A = 8.9


def _thermal_conductivity(c, els):
    """Conductividad termica de la aleacion, NO por regla de mezclas.

    Por que hace falta esto: la regla de mezclas da 84 W/mK para un inoxidable
    316 cuyo valor real es 15. Alear introduce atomos de soluto que dispersan
    los electrones de conduccion, y ese efecto no es lineal: segun la regla de
    Nordheim la resistividad anadida va como suma de ci*(1-ci), maxima en la
    composicion equiatomica. Ignorarlo inflaba la conductividad de toda aleacion
    concentrada por un factor de 5 a 8, y con ella el indice de choque termico.

        k = k_mezcla / (1 + A * sum(ci*(1-ci)))

    Validacion de la constante A = 8.9 (calculado frente a valor publicado):
        inox 316         15.0 vs 15      exacto (es la calibracion)
        Inconel 718      12.9 vs 11.4    +13%
        aleacion Cantor   9.2 vs 12-13   -28%
        cuproniquel 90/10  142 vs 40     3.5x de mas  <-- peor caso conocido

    Es decir: buena para aleaciones concentradas multicomponente, mala para
    binarios muy diluidos de metales nobles. Como aqui el objetivo son
    aleaciones concentradas, sirve; pero el veredicto de choque termico que
    depende de ella debe leerse como indicativo, no como medida.
    """
    ks = {s: els[s]["k_th"] for s in c}
    if any(v is None for v in ks.values()):
        return None, 1.0
    k_mix = sum(c[s] * ks[s] for s in c)
    disorder = sum(ci * (1.0 - ci) for ci in c.values())
    factor = 1.0 + NORDHEIM_A * disorder
    return k_mix / factor, factor


def _predict_phase(delta, omega, dh, n):
    """Aplica el criterio de Yang-Zhang y devuelve (fase, motivo legible)."""
    if delta <= DELTA_SS_MAX and (omega == float("inf") or omega >= OMEGA_SS_MIN):
        return "disolucion_solida", (
            f"delta {delta:.1f}% <= {DELTA_SS_MAX} y Omega "
            + ("infinito" if omega == float("inf") else f"{omega:.2f} >= {OMEGA_SS_MIN}")
        )
    if delta > DELTA_SS_MAX and DH_AMORPHOUS[0] <= dh <= DH_AMORPHOUS[1] and n >= 3:
        return "amorfa", (
            f"delta {delta:.1f}% > {DELTA_SS_MAX} con DHmix {dh:.0f} kJ/mol en la "
            "ventana de formacion de vidrio metalico"
        )
    if dh < -15:
        return "intermetalico", (
            f"DHmix {dh:.0f} kJ/mol muy exotermico: se ordenara en compuestos"
        )
    if delta > DELTA_SS_MAX:
        return "mixta", f"delta {delta:.1f}% excede {DELTA_SS_MAX}: segregacion probable"
    return "mixta", f"Omega {omega:.2f} < {OMEGA_SS_MIN}: la entalpia gana a la entropia"


def _predict_structure(vec, phase, c, els):
    """Estructura prevista, CON su dominio de validez declarado.

    La regla del VEC (Guo 2011) se calibro con aleaciones CONCENTRADAS de 4-5
    elementos. Aplicarla a una aleacion diluida da resultados malos y hay que
    decirlo: con ella, un acero al carbono (Fe 99%) sale "fcc+bcc" cuando es
    ferrita BCC pura, y el 316L sale "fcc+bcc" cuando es austenitico. Para esos
    aceros diluidos la herramienta correcta es el diagrama de Schaeffler
    (Cr-equivalente frente a Ni-equivalente), que este motor NO implementa
    porque su objetivo es el espacio de aleaciones concentradas.

    Asi que fuera del dominio no se disimula: se responde con la estructura del
    elemento mayoritario cuando la aleacion es casi pura, y se marca confianza
    baja cuando es diluida.
    """
    if phase not in ("disolucion_solida", "mixta"):
        return "-", "alta", "fase no metalica en disolucion: la regla del VEC no aplica"
    top = max(c, key=c.get)
    frac = c[top]
    if frac >= 0.85:
        st = els[top]["struct"]
        st = st if st in ("fcc", "bcc", "hcp") else "-"
        return st, "alta", (f"{top} supone el {frac:.0%}: la aleacion hereda su "
                            f"estructura ({els[top]['struct']})")
    if frac > 0.5:
        st = "fcc" if vec >= VEC_FCC_MIN else ("bcc" if vec < VEC_BCC_MAX else "fcc+bcc")
        return st, "baja", (
            f"VEC {vec:.2f}, pero {top} supone el {frac:.0%}: aleacion diluida, "
            "fuera del dominio con el que se calibro la regla del VEC. Para aceros "
            "diluidos el criterio valido es el diagrama de Schaeffler.")
    st = "fcc" if vec >= VEC_FCC_MIN else ("bcc" if vec < VEC_BCC_MAX else "fcc+bcc")
    return st, "alta", (f"VEC {vec:.2f} en aleacion concentrada (max {frac:.0%}): "
                        "dentro del dominio de calibracion de la regla")


def _oxidation_resistance(c, els):
    """Clasifica la capacidad de formar capa protectora.

    Metalurgia clasica: por encima de cierto contenido, Al forma alumina,
    Cr forma cromia y Si forma silice. Esas capas son adherentes y frenan la
    difusion de oxigeno. Por debajo del umbral no se forma capa continua y el
    material se oxida de forma catastrofica (oxidacion interna)."""
    formers = [s for s, thr in PROTECTIVE_FORMERS.items() if c.get(s, 0) >= thr]
    if not formers:
        noble = sum(c[s] for s in c if els[s]["dHox"] is not None and els[s]["dHox"] > -160)
        if noble >= 0.5:
            return {"class": "noble", "formers": [], "note": "mayoria de elementos nobles: no se oxida apreciablemente"}
        return {"class": "sin_proteccion", "formers": [],
                "note": "ningun formador de capa alcanza el umbral (Al>=5%, Cr>=12%, Si>=2%)"}
    cls = "alumina" if "Al" in formers else ("cromia" if "Cr" in formers else "silice")
    return {"class": cls, "formers": formers,
            "note": f"forma capa protectora de {cls} gracias a {'+'.join(formers)}"}


def _auto_name(c):
    """Nombre estilo literatura HEA: CoCrFeNi, Al0.3CoCrFeNi..."""
    syms = sorted(c, key=lambda s: (-c[s], s))
    ref = c[syms[0]]
    parts = []
    for s in syms:
        ratio = c[s] / ref
        parts.append(s if abs(ratio - 1) < 0.02 else f"{s}{ratio:.2f}".rstrip("0").rstrip("."))
    return "".join(parts)
