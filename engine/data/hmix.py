"""Entalpias de mezcla binarias a dilucion infinita, DH_AB (kJ/mol).

Por que importa
---------------
DH_mix es lo que decide si dos metales forman una disolucion solida util, un
compuesto intermetalico fragil, o ni se mezclan. Sin este numero, cualquier
"aleacion nueva" que genere el motor es un nombre bonito sin fisica detras.

Procedencia y honestidad
------------------------
- Los pares del bloque TABULADO provienen del modelo semiempirico de Miedema
  tal y como lo recopilan Takeuchi & Inoue (Mater. Trans. 46 (2005) 2817),
  la tabla que usa de facto toda la literatura de aleaciones de alta entropia.
  Confianza: alta. Error tipico frente a calorimetria: +/- 5 kJ/mol.
- Los pares NO tabulados se estiman con el propio modelo de Miedema a partir de
  phi* y n_ws^(1/3) (bloque MIEDEMA_PARAMS). Confianza: media, +/- 30%.
  El motor marca estos valores como source="miedema_estimado" y la interfaz los
  senala. No se disfrazan de dato medido.
- Si faltan los parametros de Miedema de alguno de los dos elementos, NO se
  inventa un valor: el par queda como None y el candidato se descarta con
  motivo explicito.

Convenio de signo: negativo = mezcla exotermica = los atomos A y B se atraen.
"""

# ---------------------------------------------------------------------------
# Bloque TABULADO. Clave = par ordenado alfabeticamente. Valor = kJ/mol.
# ---------------------------------------------------------------------------
_PAIRS_RAW = """
Al-Ti -30   Al-Zr -44   Al-Hf -39   Al-Nb -18   Al-V -16    Al-Cr -10
Al-Mn -19   Al-Fe -11   Al-Co -19   Al-Ni -22   Al-Cu -1    Al-Zn 1
Al-Mg -2    Al-Li -4    Al-Si -2    Al-Ta -19   Al-Mo -5    Al-W -2
Al-Y -38    Al-Sc -38   Al-Ag -4    Al-Sn 4     Al-Ca -20   Al-La -38
Ti-Zr 0     Ti-Hf 0     Ti-V -2     Ti-Nb 2     Ti-Ta 1     Ti-Cr -7
Ti-Mo -4    Ti-W -6     Ti-Mn -8    Ti-Fe -17   Ti-Co -28   Ti-Ni -35
Ti-Cu -9    Ti-Zn -12   Ti-Si -66   Ti-Ag -2    Ti-Y 15     Ti-Sc 8
Zr-Hf 0     Zr-V -4     Zr-Nb 4     Zr-Ta 3     Zr-Cr -12   Zr-Mo -6
Zr-W -9     Zr-Mn -15   Zr-Fe -25   Zr-Co -41   Zr-Ni -49   Zr-Cu -23
Zr-Zn -31   Zr-Si -84   Zr-Ag -20   Zr-Y 9      Zr-Ti 0
Hf-Nb 4     Hf-Ta 3     Hf-Mo -4    Hf-W -6     Hf-V -2     Hf-Cr -9
Hf-Fe -21   Hf-Co -35   Hf-Ni -42   Hf-Cu -17   Hf-Ti 0     Hf-Zr 0
Cr-Fe -1    Cr-Co -4    Cr-Ni -7    Cr-Cu 12    Cr-Mn 2     Cr-Mo 0
Cr-V -2     Cr-Nb -7    Cr-Ta -7    Cr-W 1      Cr-Zn -5    Cr-Si -37
Fe-Co -1    Fe-Ni -2    Fe-Cu 13    Fe-Mn 0     Fe-Mo -2    Fe-V -7
Fe-Nb -16   Fe-Ta -15   Fe-W 0      Fe-Zn -4    Fe-Si -35   Fe-Ag 28
Co-Ni 0     Co-Cu 6     Co-Mn -5    Co-Mo -5    Co-V -14    Co-Nb -25
Co-Ta -24   Co-W -1     Co-Zn -11   Co-Si -38   Co-Cr -4
Ni-Cu 4     Ni-Mn -8    Ni-Mo -7    Ni-V -18    Ni-Nb -30   Ni-Ta -29
Ni-W -3     Ni-Zn -12   Ni-Si -40   Ni-Y -31    Ni-Mg -4
Cu-Mn 4     Cu-Mo 19    Cu-V 5      Cu-Nb 3     Cu-Ta 2     Cu-W 22
Cu-Zn -6    Cu-Ag 2     Cu-Si -19   Cu-Sn 7     Cu-Mg -3    Cu-Y -22
Mn-Mo 5     Mn-V -1     Mn-Nb -4    Mn-Ta -4    Mn-W 6      Mn-Si -45
Mn-Zn -6    Mn-Ni -8
Mo-Nb -6    Mo-Ta -5    Mo-V 0      Mo-W 0      Mo-Si -35   Mo-Re -4
Nb-Ta 0     Nb-V -1     Nb-W -8     Nb-Si -56   Nb-Re -5
Ta-V -1     Ta-W -7     Ta-Si -56   Ta-Re -6
V-W -1      V-Si -48
W-Si -31    W-Re -3
Zr-Sn -43   Fe-Sn -11   Ni-Sn -4    Co-Sn -13   Ti-Sn -21   Cr-Sn 1
Mn-Sn -7    Nb-Sn -14   Hf-Sn -40   V-Sn -10    Ag-Sn -4    Zn-Sn 1
Mg-Zn -4    Mg-Li 0     Mg-Ca -6    Mg-Y -6     Mg-Sn -9    Mg-Ag -10
Y-Cu -22    Y-Al -38    Y-Ni -31    Y-Co -22    Y-Fe -1
Sc-Al -38   Sc-Ni -39   Sc-Cu -24   Sc-Fe -11   Sc-Co -30
Fe-B -26    Ni-B -24    Co-B -24    Ti-B -58    Zr-B -71    Cr-B -31
Mo-B -34    Nb-B -54    W-B -31     Ta-B -54    Hf-B -66    Al-B 0
Fe-C -50    Ti-C -110   Zr-C -131   Nb-C -102   Ta-C -102   W-C -60
Cr-C -61    Mo-C -67    V-C -100    Hf-C -125   Ni-C 33     Co-C 42
"""

# ---------------------------------------------------------------------------
# NIVEL 2: pares de la misma compilacion, pero con menor confianza en la
# transcripcion. Se separan a proposito en vez de mezclarlos con los de arriba.
# Casi todos son sistemas Mg-X y Li-X con metales de transicion: son inmiscibles
# de manual (sus diagramas de fases no muestran ningun intermetalico y la
# solubilidad mutua es despreciable), asi que el signo positivo y grande esta
# fuera de duda aunque el valor exacto pueda bailar.
# Toda aleacion que use uno de estos pares queda marcada en la interfaz.
# ---------------------------------------------------------------------------
_PAIRS_T2_RAW = """
Mg-Ti 16    Mg-Fe 18    Mg-Cr 24    Mg-V 22     Mg-Nb 23    Mg-Mo 36
Mg-Zr 6     Mg-Mn 10    Mg-Si -19   Mg-Sc -3
Li-Ti 34    Li-Cr 40    Li-V 38     Li-Zr 30    Li-Mn 30    Li-Cu 9
Li-Zn -7    Li-Si -34   Li-Sc 12
Si-Zn 2     Si-Y -95    Si-Sc -89   Si-Hf -77   Si-Sn 5     Re-Si -40
V-Zn -6     Nb-Zn -21   Mo-Zn 6     Sc-Zn -28   Al-Re -19
Sn-Y -66    Mo-Sn -7
"""

# Pares donde la confianza es menor (boruros y carburos: la propia tabla de
# Miedema es peor prediciendo compuestos intersticiales que metal-metal).
_LOWER_CONFIDENCE = {"B", "C"}


def _key(a, b):
    return "|".join(sorted((a, b)))


def _load_pairs():
    out = {}
    for tok in _PAIRS_RAW.split():
        if "-" in tok and not tok.lstrip("-").isdigit():
            pending = tok
        else:
            a, b = pending.split("-")
            out[_key(a, b)] = float(tok)
    return out


PAIRS = _load_pairs()

_saved = _PAIRS_RAW
_PAIRS_RAW = _PAIRS_T2_RAW
PAIRS_T2 = _load_pairs()
_PAIRS_RAW = _saved

# ---------------------------------------------------------------------------
# Parametros del modelo de Miedema para los pares no tabulados.
# phi  : funcion de trabajo electronegativa, V
# nws  : densidad electronica en la celda de Wigner-Seitz, (d.u.)^(1/3)
# Vm   : volumen molar, cm3/mol  (se deriva de masa/densidad en el motor,
#        aqui solo van phi y nws, que no son derivables)
# ---------------------------------------------------------------------------
MIEDEMA_PARAMS = {
    "Li": (2.85, 0.98), "Na": (2.70, 0.82), "K": (2.25, 0.65),
    "Mg": (3.45, 1.17), "Ca": (2.55, 0.91), "Sr": (2.40, 0.84), "Ba": (2.32, 0.81),
    "Be": (4.20, 1.60), "B": (4.75, 1.55), "Al": (4.20, 1.39), "Si": (4.70, 1.50),
    "Sc": (3.25, 1.27), "Ti": (3.80, 1.47), "V": (4.25, 1.64), "Cr": (4.65, 1.73),
    "Mn": (4.45, 1.61), "Fe": (4.93, 1.77), "Co": (5.10, 1.75), "Ni": (5.20, 1.75),
    "Cu": (4.45, 1.47), "Zn": (4.10, 1.32), "Ga": (4.10, 1.31), "Ge": (4.55, 1.37),
    "Y": (3.20, 1.21), "Zr": (3.40, 1.39), "Nb": (4.05, 1.62), "Mo": (4.65, 1.77),
    "Ru": (5.40, 1.83), "Rh": (5.40, 1.76), "Pd": (5.45, 1.65), "Ag": (4.35, 1.36),
    "Cd": (4.05, 1.24), "In": (3.90, 1.17), "Sn": (4.15, 1.24), "Sb": (4.40, 1.26),
    "La": (3.05, 1.18), "Ce": (3.18, 1.19), "Nd": (3.19, 1.20), "Gd": (3.20, 1.21),
    "Dy": (3.21, 1.23), "Er": (3.22, 1.24), "Lu": (3.30, 1.27),
    "Hf": (3.55, 1.43), "Ta": (4.05, 1.63), "W": (4.80, 1.81), "Re": (5.30, 1.86),
    "Os": (5.40, 1.85), "Ir": (5.55, 1.83), "Pt": (5.65, 1.78), "Au": (5.15, 1.57),
    "Pb": (4.10, 1.15), "Bi": (4.15, 1.16), "Tl": (3.90, 1.12),
    "Th": (3.30, 1.28), "U": (3.90, 1.56),
}

# Constantes empiricas del modelo de Miedema, agrupadas por tipo de par.
# P en kJ/(V^2 * mol), Q/P = 9.4 (V * d.u.^(-1/3))^2, R corrige pares
# metal_de_transicion / no_de_transicion (aqui 0: solo usamos el fallback
# entre metales, donde R no interviene).
_P_TT = 14.1   # transicion - transicion
_P_NN = 10.7   # no transicion - no transicion
_P_TN = 12.3   # mixto
_Q_OVER_P = 9.4

_TRANSITION = set("Sc Ti V Cr Mn Fe Co Ni Cu Y Zr Nb Mo Ru Rh Pd Ag Hf Ta W Re Os Ir Pt Au Th U".split())


def _miedema(a, b, vm_a, vm_b):
    """Estimacion de Miedema de DH_AB a dilucion infinita, kJ/mol.

    LIMITE DELIBERADO: solo se aplica a pares transicion-transicion.

    El modelo completo lleva un tercer termino, -R, que solo actua cuando se
    mezcla un metal de transicion con uno que no lo es (Al, Mg, Si, Sn...).
    Sin el, esos pares salen casi nulos por cancelacion: el Ir-Al calculado dio
    -0.1 kJ/mol cuando experimentalmente es fuertemente exotermico. Como no
    disponemos de la tabla de R con garantias, se prefiere declarar el par
    desconocido antes que publicar un cero falso, que es el peor error posible
    aqui: un cero pasa todos los filtros de "disolucion solida" y colaria
    aleaciones inexistentes hasta el ranking final.

    Devuelve None si falta algun parametro o si el par cae fuera del dominio.
    """
    if a not in MIEDEMA_PARAMS or b not in MIEDEMA_PARAMS:
        return None
    if a not in _TRANSITION or b not in _TRANSITION:
        return None
    phi_a, nws_a = MIEDEMA_PARAMS[a]
    phi_b, nws_b = MIEDEMA_PARAMS[b]
    P = _P_TT
    dphi = phi_a - phi_b
    dnws = nws_a - nws_b
    # Volumen de la celda corregido (aproximacion estandar V^(2/3))
    v_a = vm_a ** (2.0 / 3.0)
    v_b = vm_b ** (2.0 / 3.0)
    nws_mean_inv = 2.0 / (1.0 / nws_a + 1.0 / nws_b)
    pref = 2.0 * P * (v_a * v_b) / (v_a + v_b) / nws_mean_inv
    return pref * (-(dphi ** 2) + _Q_OVER_P * (dnws ** 2))


def dh_mix(a, b, vm_a=None, vm_b=None):
    """DH_AB del par (a, b).

    Devuelve (valor_kJ_mol, fuente, confianza) donde fuente es
    'tabulado' | 'miedema_estimado' | 'desconocido' y confianza es
    'alta' | 'media' | 'baja' | None.

    'desconocido' NO es un fallo del motor: es la respuesta correcta cuando no
    hay base para dar un numero. Quien lo reciba debe descartar el candidato,
    no sustituirlo por cero.
    """
    if a == b:
        return 0.0, "trivial", "alta"
    val = PAIRS.get(_key(a, b))
    if val is not None:
        conf = "media" if (_LOWER_CONFIDENCE & {a, b}) else "alta"
        return val, "tabulado", conf
    val = PAIRS_T2.get(_key(a, b))
    if val is not None:
        return val, "tabulado_nivel2", "media"
    if vm_a is not None and vm_b is not None:
        est = _miedema(a, b, vm_a, vm_b)
        if est is not None:
            return round(est, 1), "miedema_estimado", "media"
    return None, "desconocido", None


def coverage():
    """Cuantos pares hay por nivel de confianza. Sin esto no se sabe de que
    fiarse: es la metrica de calidad de dato de todo el motor."""
    return {"alta": len(PAIRS), "media": len(PAIRS_T2), "total": len(PAIRS) + len(PAIRS_T2)}
