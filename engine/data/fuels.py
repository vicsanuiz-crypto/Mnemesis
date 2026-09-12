"""Combustibles de referencia y estequiometrias de oxidacion.

Todo lo de aqui es dato TABULADO o DERIVADO de la tabla periodica, nunca
estimado a ojo. Los combustibles metalicos se calculan desde dHox y la
estequiometria del oxido, asi que son internamente consistentes con
data/elements.py: si se corrige un dato alli, el combustible se corrige solo.

PCI vs PCS: se usa el poder calorifico INFERIOR (LHV, agua producto en fase
vapor) porque es el que ve un motor real. El superior (HHV) solo se aprovecha
con condensacion, tipico en calderas, no en propulsion.

co2_g_MJ es CO2 directo de la combustion (tank-to-wheel). NO incluye la huella
de produccion (well-to-tank): un hidrogeno gris tiene 0 aqui y ~100 g/MJ en el
ciclo completo. Esta distincion se muestra explicitamente en la interfaz porque
es donde mas se manipulan los numeros en este sector.
"""

# Estequiometria del oxido mas estable: elemento -> (x, y) en MxOy.
# Con esto y dHox (kJ/mol O) se deriva la energia de combustion del metal.
OXIDES = {
    "H": ("H2O", 2, 1), "Li": ("Li2O", 2, 1), "Be": ("BeO", 1, 1),
    "B": ("B2O3", 2, 3), "C": ("CO2", 1, 2), "Na": ("Na2O", 2, 1),
    "Mg": ("MgO", 1, 1), "Al": ("Al2O3", 2, 3), "Si": ("SiO2", 1, 2),
    "K": ("K2O", 2, 1), "Ca": ("CaO", 1, 1), "Ti": ("TiO2", 1, 2),
    "V": ("V2O5", 2, 5), "Cr": ("Cr2O3", 2, 3), "Mn": ("MnO", 1, 1),
    "Fe": ("Fe2O3", 2, 3), "Co": ("CoO", 1, 1), "Ni": ("NiO", 1, 1),
    "Cu": ("CuO", 1, 1), "Zn": ("ZnO", 1, 1), "Zr": ("ZrO2", 1, 2),
    "Nb": ("Nb2O5", 2, 5), "Mo": ("MoO3", 1, 3), "Hf": ("HfO2", 1, 2),
    "Ta": ("Ta2O5", 2, 5), "W": ("WO3", 1, 3), "Y": ("Y2O3", 2, 3),
    "La": ("La2O3", 2, 3), "Ce": ("CeO2", 1, 2), "Th": ("ThO2", 1, 2),
    "U": ("UO2", 1, 2),
}

# Correccion para el hidrogeno: dHox tabulado corresponde a H2O LIQUIDA (PCS).
# El PCI usa H2O vapor: -241.8 kJ/mol.
DHF_H2O_GAS = -241.8

# ---------------------------------------------------------------------------
# Combustibles quimicos de referencia. Valores tabulados (CRC, GREET, IEA).
#   lhv       MJ/kg (poder calorifico inferior)
#   rho_store kg/m3 en su estado de almacenamiento real
#   store     descripcion del estado de almacenamiento
#   penalty   energia gastada en llevarlo a ese estado, como fraccion del PCI
#             (licuefaccion, compresion). Fuente: IEA Global Hydrogen Review.
#   co2       g CO2 por MJ, combustion directa
#   price     USD/kg indicativo 2024-2025
#   trl       nivel de madurez tecnologica 1-9
#   tox       0-3
# ---------------------------------------------------------------------------
REFERENCE_FUELS = [
    dict(id="h2_liq", name="Hidrogeno liquido", formula="H2", cls="hidrogeno",
         lhv=120.0, rho_store=70.8, store="liquido a 20 K (-253 C)", penalty=0.33,
         co2=0.0, price=6.0, trl=8, tox=0,
         note="Maxima energia por kilo de todo lo conocido quimicamente. Su problema nunca fue la energia: es el volumen, la criogenia y el boil-off de 0.3-1%/dia."),
    dict(id="h2_700", name="Hidrogeno comprimido 700 bar", formula="H2", cls="hidrogeno",
         lhv=120.0, rho_store=42.0, store="gas a 700 bar", penalty=0.12,
         co2=0.0, price=6.0, trl=9, tox=0,
         note="Estandar en automocion de pila de combustible. Tanque tipo IV de fibra de carbono: el deposito pesa 15-20x lo que el hidrogeno que contiene."),
    dict(id="nh3", name="Amoniaco", formula="NH3", cls="portador_h2",
         lhv=18.6, rho_store=682.0, store="liquido a 8.6 bar y 20 C", penalty=0.07,
         co2=0.0, price=0.6, trl=8, tox=3,
         note="El candidato serio para transporte maritimo: cero carbono en el escape, se licua con presion moderada y ya existe una industria y una logistica de 180 Mt/ano. Contrapartidas reales: toxico, y su combustion emite NOx y N2O (este ultimo, 273x mas potente que el CO2 como gas de efecto invernadero)."),
    dict(id="ch4_lng", name="Gas natural licuado", formula="CH4", cls="hidrocarburo",
         lhv=50.0, rho_store=422.0, store="liquido a 111 K", penalty=0.10,
         co2=55.0, price=0.5, trl=9, tox=0,
         note="Referencia fosil del sector maritimo. El metano fugado aguas arriba puede anular su ventaja frente al fuel oil."),
    dict(id="gasolina", name="Gasolina", formula="~C8H18", cls="hidrocarburo",
         lhv=44.0, rho_store=745.0, store="liquido ambiente", penalty=0.0,
         co2=72.0, price=0.9, trl=9, tox=2,
         note="El patron contra el que se mide todo. Nadie ha batido su combinacion de densidad, coste y facilidad de manejo."),
    dict(id="diesel", name="Diesel", formula="~C12H23", cls="hidrocarburo",
         lhv=43.0, rho_store=832.0, store="liquido ambiente", penalty=0.0,
         co2=73.7, price=0.9, trl=9, tox=2,
         note="Maxima densidad volumetrica entre los liquidos convencionales."),
    dict(id="jeta1", name="Queroseno de aviacion Jet A-1", formula="~C12H24", cls="hidrocarburo",
         lhv=43.0, rho_store=800.0, store="liquido ambiente", penalty=0.0,
         co2=73.2, price=0.8, trl=9, tox=2,
         note="La barrera real de la aviacion: 43 MJ/kg y 34 MJ/L simultaneamente. Ningun sustituto no fosil se acerca a las dos cifras a la vez."),
    dict(id="metanol", name="Metanol", formula="CH3OH", cls="alcohol",
         lhv=19.9, rho_store=792.0, store="liquido ambiente", penalty=0.0,
         co2=69.1, price=0.4, trl=9, tox=3,
         note="Liquido a temperatura ambiente y sintetizable desde CO2 capturado. Maersk apuesta por el en portacontenedores. La mitad de energia por litro que el diesel."),
    dict(id="etanol", name="Etanol", formula="C2H5OH", cls="alcohol",
         lhv=26.8, rho_store=789.0, store="liquido ambiente", penalty=0.0,
         co2=71.3, price=0.7, trl=9, tox=1,
         note="Maduro e infraestructura resuelta. Su limite es agricola, no tecnico: compite por suelo con la alimentacion."),
    dict(id="dme", name="Dimetil eter", formula="CH3OCH3", cls="e_fuel",
         lhv=28.8, rho_store=668.0, store="liquido a 5 bar", penalty=0.04,
         co2=67.6, price=0.7, trl=7, tox=1,
         note="Se maneja como el butano y arde en ciclo diesel casi sin hollin."),
    dict(id="libh4", name="Borohidruro de litio", formula="LiBH4", cls="hidruro",
         lhv=65.2, rho_store=666.0, store="solido ambiente", penalty=0.0,
         co2=0.0, price=200.0, trl=3, tox=2,
         note="18.5% de hidrogeno en masa, el mejor hidruro conocido. Su muro es la reversibilidad: recargarlo exige 600 C y 150 bar, asi que hoy es de un solo uso."),
    dict(id="n2h4", name="Hidracina", formula="N2H4", cls="monopropelente",
         lhv=19.4, rho_store=1021.0, store="liquido ambiente", penalty=0.0,
         co2=0.0, price=60.0, trl=9, tox=3,
         note="Monopropelente estandar de control de actitud en satelites. Cancerigeno y en proceso de sustitucion por LMP-103S y AF-M315E."),
    dict(id="carbon", name="Carbon (hulla)", formula="~C", cls="solido_fosil",
         lhv=30.0, rho_store=1300.0, store="solido a granel", penalty=0.0,
         co2=94.6, price=0.12, trl=9, tox=2,
         note="Incluido solo como suelo de coste y techo de emisiones: es la referencia inferior contra la que se compara todo."),
]
