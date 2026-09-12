"""Inyecta el informe en la plantilla y produce la interfaz autocontenida."""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")


def main():
    data_path = os.path.join(ROOT, "out", "results.json")
    if not os.path.exists(data_path):
        print("No hay informe. Ejecuta primero: python3 engine/report.py")
        return 1
    with open(data_path, encoding="utf-8") as fh:
        raw = fh.read()
    # El JSON va dentro de <script type="application/json">, asi que lo unico
    # que hay que neutralizar es una secuencia que cierre la etiqueta.
    raw = raw.replace("</", "<\\/")
    with open(os.path.join(ROOT, "ui", "template.html"), encoding="utf-8") as fh:
        tpl = fh.read()
    if "__DATA__" not in tpl:
        print("La plantilla no tiene marcador __DATA__")
        return 1
    html = tpl.replace("__DATA__", raw)
    out = os.path.join(ROOT, "out", "mnemesis.html")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(html)
    print(f"Interfaz generada: {out} ({os.path.getsize(out)/1024:.0f} KB)")
    # Comprobacion minima: que el JSON incrustado se pueda releer.
    json.loads(raw.replace("<\\/", "</"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
