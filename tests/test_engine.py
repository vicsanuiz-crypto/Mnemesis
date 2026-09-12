"""Suite de regresion de Mnemesis.

No comprueba que el codigo "no pete": comprueba que el motor SIGUE REPRODUCIENDO
la realidad. Cada test contrasta contra un material o un combustible real cuyo
comportamiento esta publicado y es verificable.

Si uno de estos cae, el motor ha dejado de predecir bien y cualquier ranking que
produzca es papel mojado. Ejecutar con:  python3 tests/test_engine.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "engine"))

from alloys import evaluate                                  # noqa: E402
from data.elements import ELEMENTS                           # noqa: E402
from data.hmix import dh_mix, PAIRS                          # noqa: E402
from environments import run                                 # noqa: E402
from fuels import all_base_fuels, enrich, metal_fuel, score_market  # noqa: E402

FAILS = []


def check(label, got, expected, tol=None, note=""):
    if tol is None:
        ok = got == expected
        detail = f"{got!r} (esperado {expected!r})"
    else:
        ok = abs(got - expected) <= tol
        detail = f"{got:.3f} (esperado {expected} +/- {tol})"
    print(("  OK   " if ok else "  FALLA ") + f"{label}: {detail}" + (f"  [{note}]" if note else ""))
    if not ok:
        FAILS.append(label)


print("\n== Integridad de la tabla periodica ==")
check("numero de elementos", len(ELEMENTS) >= 70, True)
check("densidades positivas", all(e["rho"] > 0 for e in ELEMENTS.values()), True)
check("Tm < Tb en todos los elementos condensados",
      all(e["tb_K"] > e["tm_K"] for e in ELEMENTS.values()
          if e["tb_K"] and e["tm_K"] and e["sym"] != "As"), True,
      note="el arsenico sublima, por eso se excluye")
check("densidad del wolframio", ELEMENTS["W"]["rho"], 19.25, 0.01)
_metals = [e for e in ELEMENTS.values() if e["cat"] in
           ("trans", "metal_pobre", "alcalino", "alcalinoter", "lantanido", "actinido")]
check("el wolframio funde mas alto que cualquier metal",
      max(_metals, key=lambda e: e["tm_K"])["sym"], "W",
      note="el carbono funde aun mas alto (3915 K) pero no es metal")

print("\n== Entalpias de mezcla contra valores publicados ==")
for a, b, exp in [("Ni", "Al", -22), ("Cu", "Ni", 4), ("Fe", "Cr", -1),
                  ("Ti", "Ni", -35), ("Cu", "Zr", -23), ("Fe", "Cu", 13)]:
    check(f"DHmix {a}-{b}", dh_mix(a, b)[0], exp, 0.01)
check("simetria del par (orden indiferente)", dh_mix("Al", "Ni")[0], dh_mix("Ni", "Al")[0], 0.001)
check("par inexistente devuelve desconocido, no cero", dh_mix("Cs", "Os")[1], "desconocido",
      note="inventar un cero colaria aleaciones imposibles por el filtro de disolucion solida")

print("\n== Aleaciones reales: fase y estructura ==")
cantor = evaluate({"Co": 1, "Cr": 1, "Fe": 1, "Mn": 1, "Ni": 1})
check("Cantor CoCrFeMnNi es disolucion solida", cantor["phase"], "disolucion_solida")
check("Cantor es FCC", cantor["structure"], "fcc", note="confirmado por difraccion en la literatura")
check("Cantor delta < 6.6%", cantor["delta_pct"] < 6.6, True)

senkov = evaluate({"Hf": 1, "Nb": 1, "Ta": 1, "Ti": 1, "Zr": 1})
check("Senkov HfNbTaTiZr es disolucion solida", senkov["phase"], "disolucion_solida")
check("Senkov es BCC", senkov["structure"], "bcc")

alcocrfeni = evaluate({"Al": 1, "Co": 1, "Cr": 1, "Fe": 1, "Ni": 1})
check("AlCoCrFeNi es duplex FCC+BCC", alcocrfeni["structure"], "fcc+bcc")

acero = evaluate({"Fe": 0.99, "Mn": 0.01})
check("acero al carbono es BCC (ferrita)", acero["structure"], "bcc")
check("acero al carbono se marca como casi puro", acero["regime"], "casi_pura")

inox = evaluate({"Fe": 0.65, "Cr": 0.17, "Ni": 0.12, "Mo": 0.025, "Mn": 0.02})
check("el inox 316 se marca fuera del dominio de la regla del VEC",
      inox["structure_confidence"], "baja",
      note="es diluido; el criterio valido seria Schaeffler, que no implementamos")

print("\n== Propiedades fisicas contra valores medidos ==")
check("densidad Inconel 718", evaluate(
    {"Ni": 0.53, "Cr": 0.19, "Fe": 0.18, "Nb": 0.05, "Mo": 0.03, "Ti": 0.02})["density"],
    8.19, 0.25, note="valor publicado 8.19 g/cm3")
check("conductividad termica del inox 316 (regla de Nordheim)", inox["k_th"], 15.0, 2.0,
      note="la regla de mezclas sin corregir daria 84")
check("conductividad de un metal puro no se corrige",
      evaluate({"W": 1})["k_th"], 173.0, 0.1)

print("\n== Bancos de ensayo contra comportamiento conocido ==")
check("Zircaloy-4 supera el nucleo de reactor",
      run(evaluate({"Zr": 0.98, "Sn": 0.015, "Fe": 0.003, "Cr": 0.002}), "reactor_nuclear")["passed"],
      True, note="es la vaina de combustible nuclear real")
check("la aleacion Cantor NO pasa el reactor",
      "Absorcion de neutrones" in run(cantor, "reactor_nuclear")["failures"], True,
      note="el cobalto se activa a Co-60; por eso esta vetado en internos de reactor")
check("el acero al carbono se rompe en criogenia",
      "Transicion ductil-fragil" in run(acero, "criogenia")["failures"], True)
check("una aleacion FCC aguanta la criogenia",
      run(cantor, "criogenia")["passed"], True)
check("el inox 316 NO aguanta agua de mar (PREN ~25 < 32)",
      "Corrosion por cloruros" in run(inox, "fondo_marino")["failures"], True,
      note="correcto: el 316 pica en agua de mar estancada")
superduplex = evaluate({"Fe": 0.62, "Cr": 0.25, "Ni": 0.07, "Mo": 0.04, "Mn": 0.02})
check("el superduplex 2507 SI aguanta agua de mar (PREN ~42)",
      run(superduplex, "fondo_marino")["passed"], True)
check("el Inconel 625 aguanta agua de mar",
      run(evaluate({"Ni": 0.61, "Cr": 0.215, "Mo": 0.09, "Nb": 0.037, "Fe": 0.04}),
          "fondo_marino")["passed"], True)

print("\n== Combustibles derivados de la tabla periodica ==")
for sym, exp in [("Al", 31.0), ("Fe", 7.4), ("B", 58.9), ("Mg", 24.7),
                 ("Si", 32.6), ("Zn", 5.3), ("Li", 43.1)]:
    check(f"energia de combustion del {sym}", metal_fuel(sym)["lhv"], exp, exp * 0.02,
          note="MJ/kg, contra valor publicado")

fuels = [enrich(f) for f in all_base_fuels()]
by_id = {f["id"]: f for f in fuels}
check("PCI del hidrogeno", by_id["h2_liq"]["lhv"], 120.0, 0.5)
check("PCI del queroseno", by_id["jeta1"]["lhv"], 43.0, 0.5)
check("el diesel es mas denso en energia por litro que el metanol",
      by_id["diesel"]["MJ_per_L"] > by_id["metanol"]["MJ_per_L"], True)
check("el hidrogeno liquido gana en MJ/kg a todo lo quimico",
      max(fuels, key=lambda f: f["lhv"])["id"] in ("h2_liq", "h2_700", "libh4"), True)
check("el boro gana en MJ/L", max(fuels, key=lambda f: f["MJ_per_L"])["id"], "metal_b",
      note="por eso es el combustible de referencia teorica en ramjets")
check("el hidrogeno pierde en MJ/L contra el diesel",
      by_id["h2_liq"]["MJ_per_L"] < by_id["diesel"]["MJ_per_L"], True,
      note="el problema del hidrogeno nunca fue la energia, es el volumen")

print("\n== Puntuacion por mercado ==")
top_ram = score_market(fuels, "ramjet")[0]
check("en propulsion volumetrica gana un combustible de alta densidad",
      top_ram["MJ_per_L"] > by_id["jeta1"]["MJ_per_L"], True, note=f"gano {top_ram['name']}")
top_red = score_market(fuels, "red")[0]
top_ram_cost = top_ram["cost_usd_kwh"]
check("los pesos de mercado cambian de verdad la respuesta",
      top_red["id"] != top_ram["id"], True,
      note=f"red: {top_red['name']} / ramjet: {top_ram['name']}")
check("en almacenamiento de red no gana un exotico caro",
      top_red["cost_usd_kwh"] < top_ram_cost / 10, True,
      note=f"gano {top_red['name']} a {top_red['cost_usd_kwh']:.3f} USD/kWh")
check("el ganador en red no es intensivo en carbono",
      top_red["co2"] < 60, True, note=f"{top_red['co2']} g CO2/MJ")

print("\n" + "=" * 62)
if FAILS:
    print(f"FALLAN {len(FAILS)} comprobaciones:")
    for f in FAILS:
        print("   - " + f)
    sys.exit(1)
print("Todas las comprobaciones pasan. El motor reproduce la realidad conocida.")
