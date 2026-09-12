"""Banco de ensayos: someter un material a un entorno real y ver si aguanta.

Cada entorno es un banco de pruebas con condiciones concretas (temperatura,
presion, atmosfera, radiacion) y una bateria de ensayos. Cada ensayo devuelve
uno de cuatro veredictos:

  ok          cumple con margen
  limite      cumple pero sin margen: exige validacion experimental
  fallo       no cumple; el motivo se indica siempre con numeros
  no_evaluable falta el dato para juzgarlo. NO es un aprobado.

Esa cuarta categoria es deliberada. Un ensayo sin datos que devolviera "ok"
seria exactamente el fallo silencioso que mas caro sale: el candidato llegaria
al ranking final sin que nadie haya comprobado nada.
"""

from data.elements import get
from data.extra import cte, neutron_barns, PREN_COEFFS, PREN_SEAWATER

OK, LIMITE, FALLO, ND = "ok", "limite", "fallo", "no_evaluable"
_WEIGHT = {OK: 1.0, LIMITE: 0.5, FALLO: 0.0, ND: 0.0}

ENVIRONMENTS = {
    "ambiente": dict(
        name="Ambiente estandar", T=298, P=1.0, atm="aire",
        tests=["oxidacion", "corrosion_cloruro"],
        desc="Referencia de control: 25 C, 1 atm, aire seco."),
    "criogenia": dict(
        name="Tanque criogenico de hidrogeno", T=20, P=3.0, atm="hidrogeno",
        tests=["dbtt", "fragilizacion_h", "choque_termico"], shock="suave",
        desc="20 K con hidrogeno liquido. Mata dos veces: fragilidad a baja "
             "temperatura y fragilizacion por hidrogeno a la vez.",
        market="Aeroespacial e hidrogeno liquido"),
    "turbina": dict(
        name="Turbina de gas (seccion caliente)", T=1700, T_mat=1350, P=40.0, atm="oxidante",
        tests=["margen_termico", "fluencia", "oxidacion", "choque_termico"], shock="severo",
        desc="Gas a 1700 K y 40 bar. El metal NO ve esos 1700 K: la pelicula de "
             "aire de refrigeracion y la barrera termica ceramica lo dejan en unos "
             "1350 K. Por eso un alabe real funciona por encima del punto de fusion "
             "de su propia aleacion sin fundirse.",
        market="Aviacion y generacion electrica"),
    "camara_cohete": dict(
        name="Camara de combustion de cohete", T=3500, T_mat=800, P=200.0, atm="oxidante",
        tests=["margen_termico", "choque_termico", "presion"], shock="extremo",
        desc="Gas a 3500 K y 200 bar. La pared se mantiene sobre 800 K con "
             "refrigeracion regenerativa: el propio combustible circula por canales "
             "en la pared antes de quemarse. Lo que mata aqui no es la temperatura "
             "absoluta sino el gradiente, de ahi que el revestimiento sea de cobre.",
        market="Lanzadores espaciales"),
    "reactor_nuclear": dict(
        name="Nucleo de reactor de agua a presion", T=600, P=155.0, atm="agua_alta_pureza",
        tests=["neutronica", "margen_termico", "presion"],
        desc="600 K, 155 bar y flujo de neutrones. La seccion eficaz manda por "
             "encima de cualquier propiedad mecanica: un material que se come los "
             "neutrones apaga el reactor.",
        market="Energia nuclear"),
    "fondo_marino": dict(
        name="Instalacion submarina profunda", T=277, P=300.0, atm="salmuera",
        tests=["corrosion_cloruro", "presion", "dbtt"],
        desc="3000 m de profundidad: 4 C, 300 bar y cloruros. Es el entorno de "
             "los cables, las valvulas y los amarres en alta mar.",
        market="Eolica marina y submarino"),
    "reentrada": dict(
        name="Reentrada atmosferica", T=2000, T_mat=2000, P=0.1, atm="plasma_oxidante",
        tests=["margen_termico", "oxidacion", "choque_termico"], shock="extremo",
        desc="2000 K en plasma disociado y con gradientes brutales. El oxigeno "
             "atomico ataca incluso a materiales que resisten el O2 molecular.",
        market="Reentrada y vehiculos hipersonicos"),
    "electrolizador": dict(
        name="Electrolizador PEM", T=353, P=30.0, atm="acido_h2",
        tests=["corrosion_acida", "fragilizacion_h", "presion"],
        desc="80 C, 30 bar, pH cercano a 0 y potencial anodico. Solo sobreviven "
             "titanio, platino e iridio; de ahi el coste del hidrogeno verde.",
        market="Hidrogeno verde"),
    "motor_h2": dict(
        name="Motor de combustion de hidrogeno", T=1200, T_mat=950, P=80.0, atm="hidrogeno",
        tests=["margen_termico", "fragilizacion_h", "oxidacion", "fluencia"],
        desc="1200 K en atmosfera de hidrogeno a presion. La fragilizacion por "
             "hidrogeno es el motivo real de que reconvertir motores no sea trivial.",
        market="Transporte pesado"),
    "espacio_profundo": dict(
        name="Espacio profundo", T=150, P=0.0, atm="vacio",
        tests=["dbtt", "choque_termico"], shock="suave",
        desc="Vacio, 150 K de media y ciclado termico de -170 a +120 C cada "
             "orbita. Lo que rompe aqui es la fatiga termica, no la carga.",
        market="Satelites"),
}


def _v(cond_ok, cond_limit):
    return OK if cond_ok else (LIMITE if cond_limit else FALLO)


def _tmat(env):
    """Temperatura que ve REALMENTE el metal. En componentes refrigerados no es
    la del gas: confundirlas suspende a las superaleaciones de niquel, que
    llevan 60 anos funcionando en turbinas por encima de su punto de fusion."""
    return env.get("T_mat", env["T"])


def _test_margen_termico(alloy, env):
    tm = alloy["tm_mean_K"]
    t_mat = _tmat(env)
    ratio = t_mat / tm
    cooled = "" if t_mat == env["T"] else f" (gas a {env['T']} K, metal refrigerado a {t_mat} K)"
    if ratio >= 1.0:
        return FALLO, f"funde: T de metal {t_mat} K >= Tm estimada {tm:.0f} K{cooled}"
    verdict = _v(ratio <= 0.6, ratio <= 0.8)
    return verdict, (f"T/Tm = {ratio:.2f} (Tm estimada {tm:.0f} K){cooled}. "
                     "Por encima de 0.6 la resistencia cae rapido; por encima de 0.8 "
                     "solo sirve con refrigeracion activa.")


def _test_fluencia(alloy, env):
    """La fluencia es deformacion lenta bajo carga a T alta. El parametro que
    manda es la temperatura homologa T/Tm: por encima de 0.5 hay fluencia
    apreciable en escalas de miles de horas."""
    ratio = _tmat(env) / alloy["tm_mean_K"]
    verdict = _v(ratio <= 0.5, ratio <= 0.7)
    return verdict, (f"temperatura homologa {ratio:.2f}. Por encima de 0.5 hay "
                     "fluencia medible a 1000 h; por encima de 0.7 el material "
                     "se deforma bajo su propio peso.")


def _test_oxidacion(alloy, env):
    ox = alloy["oxidation"]
    if env["atm"] not in ("aire", "oxidante", "plasma_oxidante"):
        return OK, "atmosfera no oxidante"
    if env["T"] < 700:
        return OK, f"a {env['T']} K la cinetica de oxidacion es despreciable"
    if ox["class"] == "noble":
        return OK, ox["note"]
    if ox["class"] == "sin_proteccion":
        return FALLO, (f"a {env['T']} K en atmosfera oxidante y {ox['note']}: "
                       "oxidacion interna, no superficial. Se degrada en horas.")
    if env["atm"] == "plasma_oxidante" and ox["class"] != "alumina":
        return LIMITE, (f"capa de {ox['class']}: la cromia se volatiliza como CrO3 "
                        "por encima de 1200 K y la silice se erosiona con oxigeno "
                        "atomico. Solo la alumina aguanta este entorno.")
    if env["T"] > 1400 and ox["class"] == "cromia":
        return LIMITE, ("capa de cromia por encima de 1400 K: se volatiliza como "
                        "CrO3 y la proteccion se consume. Necesita recubrimiento.")
    return OK, ox["note"]


def _test_choque_termico(alloy, env):
    """Indice de Kingery: R' = k / (E * alpha), en W/(m K) / (GPa * 1e-6/K).

    Escala real, calculada con esta misma formula y los datos de la tabla:
        acero inoxidable 316   0.004   malo
        superaleacion de Ni    0.004   malo (por eso todo alabe lleva barrera termica)
        titanio                0.022
        molibdeno              0.087
        wolframio              0.094   excelente (es el material del divertor de ITER)
        aluminio               0.147
        cobre                  0.187   excelente (por eso el revestimiento de la
                                       camara de un motor cohete es de cobre)
    Los umbrales de abajo salen de esta escala, no de un numero redondo.
    """
    comp = alloy["composition"]
    a = _mix(comp, cte)
    if a is None or alloy["modulus_GPa"] is None:
        return ND, "falta dilatacion termica o modulo elastico para al menos un componente"
    k = alloy.get("k_th")
    if k is None:
        return ND, "falta conductividad termica de algun componente"
    r = k / (alloy["modulus_GPa"] * a)          # W/(m K) / (GPa * 1e-6/K)
    # El umbral depende de la brusquedad del gradiente. Un tanque criogenico se
    # llena en minutos; una tobera de cohete ve 3000 K en milisegundos. Exigir
    # lo mismo a los dos suspenderia el acero inoxidable en aplicaciones donde
    # lleva decadas funcionando.
    ok_thr, lim_thr = {"suave": (0.004, 0.0015), "severo": (0.015, 0.004),
                       "extremo": (0.060, 0.020)}[env.get("shock", "severo")]
    verdict = _v(r >= ok_thr, r >= lim_thr)
    return verdict, (f"indice de choque termico k/(E*alpha) = {r:.3f} frente al "
                     f"umbral {ok_thr:.2f} de un gradiente {env.get('shock','severo')} "
                     f"(k={k:.0f} W/mK, E={alloy['modulus_GPa']:.0f} GPa, "
                     f"alpha={a:.1f}e-6/K). Escala: inoxidable 0.004, titanio 0.022, "
                     "wolframio 0.094, cobre 0.187.")


def _test_dbtt(alloy, env):
    """Transicion ductil-fragil. Los metales BCC y HCP la sufren; los FCC no.
    Es la razon por la que los tanques criogenicos y los buques polares se
    construyen en acero austenitico (FCC) o aluminio, nunca en acero al carbono."""
    st = alloy["structure"]
    if env["T"] > 250:
        return OK, f"a {env['T']} K no hay riesgo de transicion ductil-fragil"
    if st == "fcc":
        return OK, "estructura FCC: no presenta transicion ductil-fragil, mantiene "\
                   "tenacidad hasta temperaturas de helio liquido"
    if st == "bcc":
        return FALLO, (f"estructura BCC a {env['T']} K: transicion ductil-fragil. "
                       "Rompe de forma fragil sin aviso, que es como se parten los "
                       "cascos soldados en frio.")
    if st == "fcc+bcc":
        return LIMITE, ("mezcla FCC+BCC: la fase BCC es el eslabon fragil. Exige "
                        "ensayo Charpy a la temperatura de servicio.")
    if st == "hcp":
        return LIMITE, ("estructura HCP: comportamiento mixto y hay que ensayarlo. "
                        "El titanio y el circonio conservan tenacidad en criogenia "
                        "(el Ti-5Al-2.5Sn ELI es aleacion estandar de tanque de "
                        "hidrogeno liquido), pero el magnesio y el zinc son fragiles.")
    return ND, f"estructura '{st}' sin criterio de transicion ductil-fragil establecido"


def _test_fragilizacion_h(alloy, env):
    """El hidrogeno difunde por la red y fragiliza. La difusividad en BCC es
    unos 4 ordenes de magnitud mayor que en FCC: por eso un acero austenitico
    aguanta hidrogeno y uno ferritico no."""
    if env["atm"] not in ("hidrogeno", "acido_h2"):
        return OK, "sin hidrogeno en el entorno"
    st = alloy["structure"]
    if st == "fcc":
        return OK, ("estructura FCC: la difusividad del hidrogeno es unas 10.000 "
                    "veces menor que en BCC. Es la eleccion estandar para servicio "
                    "en hidrogeno.")
    if st == "bcc":
        return FALLO, ("estructura BCC en hidrogeno: difusion rapida por la red, "
                       "acumulacion en bordes de grano y fractura intergranular.")
    if st == "fcc+bcc":
        return LIMITE, "la fase BCC es via de entrada del hidrogeno; requiere ensayo"
    if st == "hcp":
        return LIMITE, ("estructura HCP: el modo de fallo no es difusion sino "
                        "formacion de hidruros fragiles. El circonio y el titanio "
                        "forman ZrH2 y TiH2 que ampollan el material. Exige ensayo "
                        "de carga de hidrogeno, no se decide en el papel.")
    return ND, f"estructura '{st}' sin criterio de fragilizacion establecido"


def _test_corrosion_cloruro(alloy, env):
    """PREN: el numero que la industria usa para decidir si un acero aguanta
    agua de mar. Es una formula de norma, no una heuristica nuestra."""
    if env["atm"] not in ("salmuera", "aire"):
        return OK, "sin cloruros en el entorno"
    wt = _weight_percent(alloy["composition"])
    pren = sum(PREN_COEFFS.get(s, 0.0) * w for s, w in wt.items())
    if env["atm"] == "aire":
        return (OK, f"PREN {pren:.0f}: sin cloruros relevantes en aire seco")
    verdict = _v(pren >= PREN_SEAWATER + 8, pren >= PREN_SEAWATER)
    return verdict, (f"PREN = {pren:.0f} (umbral {PREN_SEAWATER:.0f} para agua de mar). "
                     "Formula: %Cr + 3.3*%Mo + 1.65*%W en masa.")


def _test_corrosion_acida(alloy, env):
    """Medio acido con potencial anodico: solo pasivan el titanio, el niobio,
    el tantalo, el circonio y los metales nobles."""
    resistant = {"Ti", "Nb", "Ta", "Zr", "Pt", "Au", "Ir", "Pd", "Rh", "Ru"}
    frac = sum(c for s, c in alloy["composition"].items() if s in resistant)
    verdict = _v(frac >= 0.85, frac >= 0.60)
    return verdict, (f"{frac:.0%} de la composicion pasiva en medio acido oxidante "
                     "(Ti, Nb, Ta, Zr y metales nobles). Por debajo del 60% se "
                     "disuelve en semanas a pH 0 con potencial anodico.")


def _test_neutronica(alloy, env):
    comp = alloy["composition"]
    missing = [s for s in comp if neutron_barns(s) is None]
    if missing:
        return ND, f"sin seccion eficaz tabulada para {', '.join(missing)}"
    sigma = sum(c * neutron_barns(s) for s, c in comp.items())
    verdict = _v(sigma <= 1.0, sigma <= 5.0)
    culprits = sorted(comp, key=lambda s: -comp[s] * neutron_barns(s))[:2]
    return verdict, (f"seccion eficaz media {sigma:.2f} barns. Referencia: el "
                     f"circonio de las vainas reales da 0.18 b. Mayor contribucion: "
                     f"{', '.join(culprits)}.")


def _test_presion(alloy, env):
    e = alloy["modulus_GPa"]
    if e is None:
        return ND, "sin modulo elastico suficiente en la composicion"
    p_gpa = env["P"] / 10000.0
    ratio = p_gpa / e
    verdict = _v(ratio <= 1e-3, ratio <= 5e-3)
    return verdict, (f"presion {env['P']:.0f} bar frente a modulo {e:.0f} GPa: "
                     f"deformacion elastica {ratio*100:.4f}%. El limite real de un "
                     "recipiente lo marca el espesor de pared, no el material, "
                     "salvo en estos ordenes de magnitud.")


_TESTS = {
    "margen_termico": _test_margen_termico,
    "fluencia": _test_fluencia,
    "oxidacion": _test_oxidacion,
    "choque_termico": _test_choque_termico,
    "dbtt": _test_dbtt,
    "fragilizacion_h": _test_fragilizacion_h,
    "corrosion_cloruro": _test_corrosion_cloruro,
    "corrosion_acida": _test_corrosion_acida,
    "neutronica": _test_neutronica,
    "presion": _test_presion,
}

_LABEL = {
    "margen_termico": "Margen termico", "fluencia": "Fluencia a largo plazo",
    "oxidacion": "Oxidacion", "choque_termico": "Choque termico",
    "dbtt": "Transicion ductil-fragil", "fragilizacion_h": "Fragilizacion por hidrogeno",
    "corrosion_cloruro": "Corrosion por cloruros", "corrosion_acida": "Corrosion acida",
    "neutronica": "Absorcion de neutrones", "presion": "Carga por presion",
}


def _mix(comp, fn):
    """Media ponderada, devolviendo None si falta cualquier componente."""
    vals = {s: fn(s) for s in comp}
    if any(v is None for v in vals.values()):
        return None
    return sum(comp[s] * vals[s] for s in comp)


def _weight_percent(comp):
    masses = {s: comp[s] * get(s)["mass"] for s in comp}
    total = sum(masses.values())
    return {s: 100.0 * m / total for s, m in masses.items()}


def run(alloy, env_key):
    """Somete una aleacion a un entorno. Devuelve el acta completa del ensayo."""
    env = ENVIRONMENTS[env_key]
    results = []
    for t in env["tests"]:
        verdict, why = _TESTS[t](alloy, env)
        results.append(dict(test=t, label=_LABEL[t], verdict=verdict, detail=why))
    scored = [r for r in results if r["verdict"] != ND]
    score = (100.0 * sum(_WEIGHT[r["verdict"]] for r in scored) / len(scored)) if scored else None
    return dict(
        env=env_key, env_name=env["name"], T=env["T"], P=env["P"], atm=env["atm"],
        results=results,
        score=round(score, 0) if score is not None else None,
        passed=all(r["verdict"] in (OK, LIMITE) for r in results) and not any(
            r["verdict"] == ND for r in results),
        failures=[r["label"] for r in results if r["verdict"] == FALLO],
        unknowns=[r["label"] for r in results if r["verdict"] == ND],
    )


def run_all(alloy):
    return {k: run(alloy, k) for k in ENVIRONMENTS}
