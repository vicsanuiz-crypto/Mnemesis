"""Datos complementarios para los ensayos de entorno.

Solo se tabula lo que hace falta para un ensayo concreto, y solo para los
elementos donde el valor es solido. Los ausentes devuelven None y el ensayo
correspondiente responde "no evaluable" en vez de aprobar por defecto. Aprobar
por defecto seria el fallo silencioso clasico: el candidato pasaria el filtro
nuclear sin que nadie haya mirado su seccion eficaz.
"""

# Seccion eficaz de captura de neutrones termicos (2200 m/s), en barns.
# Decide si un material puede estar dentro del nucleo de un reactor: el circonio
# (0.18 b) es la vaina del combustible nuclear de todo el planeta precisamente
# por esto, mientras que el hafnio (104 b), su vecino quimico casi identico, se
# usa para lo contrario: barras de control.
NEUTRON_BARNS = {
    "H": 0.333, "Li": 70.5, "Be": 0.0076, "B": 767.0, "C": 0.0035,
    "Na": 0.53, "Mg": 0.063, "Al": 0.231, "Si": 0.171, "K": 2.1, "Ca": 0.43,
    "Sc": 27.5, "Ti": 6.1, "V": 5.08, "Cr": 3.05, "Mn": 13.3, "Fe": 2.56,
    "Co": 37.18, "Ni": 4.49, "Cu": 3.78, "Zn": 1.11, "Ga": 2.75, "Ge": 2.2,
    "Y": 1.28, "Zr": 0.184, "Nb": 1.15, "Mo": 2.48, "Ru": 2.56, "Rh": 145.0,
    "Pd": 6.9, "Ag": 63.3, "Cd": 2520.0, "In": 193.8, "Sn": 0.626, "Sb": 5.1,
    "La": 8.97, "Ce": 0.63, "Nd": 50.5, "Sm": 5922.0, "Gd": 49700.0,
    "Dy": 994.0, "Er": 159.0, "Lu": 74.0, "Hf": 104.1, "Ta": 20.6, "W": 18.3,
    "Re": 90.0, "Os": 16.0, "Ir": 425.0, "Pt": 10.3, "Au": 98.65,
    "Pb": 0.171, "Bi": 0.0338, "Th": 7.37, "U": 7.57,
}

# Coeficiente de dilatacion termica lineal a 300 K, 10^-6 / K.
CTE_1E6_K = {
    "Li": 46.0, "Be": 11.3, "B": 6.0, "C": 7.1, "Na": 71.0, "Mg": 24.8,
    "Al": 23.1, "Si": 2.6, "K": 83.0, "Ca": 22.3, "Sc": 10.2, "Ti": 8.6,
    "V": 8.4, "Cr": 4.9, "Mn": 21.7, "Fe": 11.8, "Co": 13.0, "Ni": 13.4,
    "Cu": 16.5, "Zn": 30.2, "Ga": 18.0, "Ge": 6.0, "Sr": 22.5, "Y": 10.6,
    "Zr": 5.7, "Nb": 7.3, "Mo": 4.8, "Ru": 6.4, "Rh": 8.2, "Pd": 11.8,
    "Ag": 18.9, "Cd": 30.8, "In": 32.1, "Sn": 22.0, "Sb": 11.0, "Ba": 20.6,
    "La": 12.1, "Ce": 6.3, "Nd": 9.6, "Sm": 12.7, "Gd": 9.4, "Dy": 9.9,
    "Er": 12.2, "Yb": 26.3, "Lu": 9.9, "Hf": 5.9, "Ta": 6.3, "W": 4.5,
    "Re": 6.2, "Os": 5.1, "Ir": 6.4, "Pt": 8.8, "Au": 14.2, "Tl": 29.9,
    "Pb": 28.9, "Bi": 13.4, "Th": 11.0, "U": 13.9,
}

# Resistencia a picadura por cloruros. PREN = %Cr + 3.3*%Mo + 1.65*%W + 16*%N
# (norma de facto en aceros inoxidables y aleaciones de niquel; % en masa).
# PREN >= 32 es el umbral practico para agua de mar; >= 40 para ambientes
# agrios con cloruro y temperatura.
PREN_COEFFS = {"Cr": 1.0, "Mo": 3.3, "W": 1.65, "N": 16.0}
PREN_SEAWATER = 32.0


def neutron_barns(sym):
    return NEUTRON_BARNS.get(sym)


def cte(sym):
    return CTE_1E6_K.get(sym)
