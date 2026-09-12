"""Ejecuta el cribado completo y emite el informe que consume la interfaz."""

import json
import os
import sys
import time
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data.elements import ELEMENTS                      # noqa: E402
from data.hmix import coverage                          # noqa: E402
from environments import ENVIRONMENTS, run              # noqa: E402
from fuels import (MARKETS, all_base_fuels, blend,      # noqa: E402
                   enrich, score_market)
from generate import PALETTES, generate                 # noqa: E402
from screen import TARGETS, screen                      # noqa: E402
from superheavy import PREDICTED, VERDICT               # noqa: E402

# Formulaciones. Todas tienen precedente real en la literatura o en la
# industria: no son mezclas inventadas para rellenar la tabla.
FORMULATIONS = [
    (dict(jeta1=0.70, metal_b=0.30), "Queroseno con 30% de boro en masa",
     "Combustible de suspension para estatorreactor. Investigado desde los anos "
     "50 (proyecto HEF de la US Navy) por su densidad energetica. Se abandono "
     "por los depositos de B2O3 en la tobera, no por falta de energia."),
    (dict(jeta1=0.80, metal_al=0.20), "Queroseno con 20% de aluminio en masa",
     "Suspension metalizada. El aluminio en propulsante solido lleva decadas "
     "en produccion; el reto aqui es mantener la suspension estable y que el "
     "polvo no sedimente en el deposito."),
    (dict(diesel=0.85, metal_fe=0.15), "Diesel con 15% de hierro en masa",
     "Transicion gradual hacia el ciclo del hierro sin cambiar el motor. El "
     "oxido de hierro se recoge del escape y se regenera con hidrogeno verde."),
    (dict(nh3=0.97, h2_700=0.03), "Amoniaco con 3% de hidrogeno en masa",
     "Craqueo parcial del amoniaco a bordo. El 3% en masa equivale a cerca de "
     "un 20% en volumen, que es como lo cita la literatura. Resuelve el "
     "problema real del amoniaco: su velocidad de llama es tan baja que no "
     "sostiene la combustion sin un acelerante."),
    (dict(ch4_lng=0.97, h2_700=0.03), "Gas natural con 3% de hidrogeno en masa",
     "Hythane. El 3% en masa es aproximadamente el 20% en volumen, el limite "
     "que ya se inyecta en redes de gas reales. Ese tope lo marca la "
     "fragilizacion de las tuberias de acero, no la combustion."),
    (dict(metanol=0.75, metal_al=0.25), "Metanol con 25% de aluminio en masa",
     "Combina un liquido manejable con la densidad volumetrica del aluminio. "
     "Sube el PCI del metanol de 19.9 a cerca de 23 MJ/kg."),
    (dict(metal_fe=0.60, metal_al=0.40), "Polvo mixto hierro-aluminio 60/40 en masa",
     "Los dos metales del ciclo cerrado combinados: el aluminio aporta energia "
     "por kilo y el hierro aporta densidad y facilidad de recuperacion."),
]


def build():
    t0 = time.time()
    report = dict(
        generated_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        elements=list(ELEMENTS.values()),
        environments={k: dict(v, key=k) for k, v in ENVIRONMENTS.items()},
        markets=MARKETS,
        palettes=PALETTES,
        targets=TARGETS,
        superheavy=dict(predicted=PREDICTED, verdict=VERDICT),
        data_quality=dict(
            hmix_pairs=coverage(),
            elements=len(ELEMENTS),
            elements_missing_price=[s for s, e in ELEMENTS.items() if e["price"] is None],
            elements_missing_modulus=[s for s, e in ELEMENTS.items() if e["E_GPa"] is None],
        ),
    )

    # --- Materiales -------------------------------------------------------
    materials, funnels = {}, {}
    generated_cache = {}
    for key, tgt in TARGETS.items():
        pal = tgt["palette"]
        if pal not in generated_cache:
            generated_cache[pal] = generate(pal)[0]
        short, stats = screen(generated_cache[pal], key, top=30)
        # El informe no necesita el acta completa de cada ensayo para los 30;
        # se guarda entera solo para los 10 primeros y resumida para el resto.
        for a in short[10:]:
            a["env_reports"] = {k: dict(env_name=v["env_name"], score=v["score"],
                                        passed=v["passed"])
                                for k, v in a["env_reports"].items()}
        materials[key] = short
        funnels[key] = stats
    report["materials"] = materials
    report["funnels"] = funnels
    report["total_evaluated"] = sum(len(v) for v in generated_cache.values())

    # --- Materiales de referencia, para que el ranking tenga contra que medirse
    from alloys import evaluate
    refs = {
        "Inconel 718": {"Ni": .53, "Cr": .19, "Fe": .18, "Nb": .05, "Mo": .03, "Ti": .02},
        "Acero inoxidable 316L": {"Fe": .65, "Cr": .17, "Ni": .12, "Mo": .025, "Mn": .02},
        "Superduplex 2507": {"Fe": .62, "Cr": .25, "Ni": .07, "Mo": .04, "Mn": .02},
        "Aleacion Cantor CoCrFeMnNi": {"Co": 1, "Cr": 1, "Fe": 1, "Mn": 1, "Ni": 1},
        "Refractaria Senkov HfNbTaTiZr": {"Hf": 1, "Nb": 1, "Ta": 1, "Ti": 1, "Zr": 1},
        "Ti-6Al-4V": {"Ti": .90, "Al": .06, "V": .04},
        "Zircaloy-4": {"Zr": .98, "Sn": .015, "Fe": .003, "Cr": .002},
        "Aluminio 7075": {"Al": .90, "Zn": .056, "Mg": .025, "Cu": .016},
    }
    benchmarks = []
    for name, comp in refs.items():
        a = evaluate(comp, name=name)
        a["env_reports"] = {k: run(a, k) for k in ENVIRONMENTS}
        a["is_benchmark"] = True
        benchmarks.append(a)
    report["benchmarks"] = benchmarks

    # --- Combustibles -----------------------------------------------------
    base = all_base_fuels()
    mixes = []
    for comps, name, note in FORMULATIONS:
        try:
            mixes.append(blend(comps, name, note))
        except ValueError as exc:
            print(f"  aviso: formulacion '{name}' descartada -> {exc}")
    fuels = [enrich(f) for f in base + mixes]
    report["fuels"] = fuels
    report["fuel_rankings"] = {m: score_market(fuels, m) for m in MARKETS}

    report["runtime_s"] = round(time.time() - t0, 1)
    return report


def main():
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out")
    os.makedirs(out_dir, exist_ok=True)
    print("Ejecutando cribado completo...")
    rep = build()
    path = os.path.join(out_dir, "results.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(rep, fh, ensure_ascii=False, separators=(",", ":"))
    size = os.path.getsize(path) / 1024
    print(f"\n  {rep['total_evaluated']} composiciones evaluadas en {rep['runtime_s']}s")
    print(f"  {len(rep['fuels'])} combustibles ({len(FORMULATIONS)} formulaciones)")
    print(f"  {len(rep['benchmarks'])} materiales de referencia")
    print(f"  informe: {path} ({size:.0f} KB)")
    return rep


if __name__ == "__main__":
    main()
