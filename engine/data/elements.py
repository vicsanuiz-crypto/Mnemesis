"""Tabla periódica operativa de Mnemesis.

REGLA DE ORO DE ESTE ARCHIVO: aquí solo entran valores tabulados de referencia
(CRC Handbook, WebElements, Kittel para estructura). Si un valor no se conoce
con seguridad se escribe "-" y el motor lo trata como None, NUNCA se rellena a
ojo. Un hueco honesto es información; un numero inventado envenena todo el
screening.

Unidades y convenios
--------------------
mass       g/mol
en         electronegatividad de Pauling
r_pm       radio metalico (Goldschmidt, CN=12) o covalente para no metales, pm
tm_K/tb_K  fusion y ebullicion a 1 atm, K
rho        densidad a 298 K, g/cm3
vec        valence electron concentration usada en la literatura de HEA
           (electrones s+d de la capa externa; Al=3, Ti=4, Cr=6, Fe=8, Ni=10)
struct     estructura cristalina a 298 K, 1 atm
abund_ppm  abundancia en la corteza continental, mg/kg
price      USD/kg. ATENCION: orden de magnitud indicativo (referencia 2024-2025).
           Los metales menores y los PGM se mueven un 50-300% en un ano.
           Sirve para ordenar candidatos, NO para presupuestar.
k_th       conductividad termica a 300 K, W/(m K)
E_GPa      modulo de Young policristalino, GPa
dHox       entalpia de formacion del oxido mas estable POR MOL DE OXIGENO,
           kJ/mol O. Mas negativo = oxido mas estable = mas avido de oxigeno.
           Es la base del ranking de oxidacion y del rendimiento como combustible.
tox        0 = inocuo, 1 = precaucion, 2 = toxico, 3 = muy toxico/cancerigeno
crit       1 si figura en la lista de materias primas criticas de la UE (2023)
radio      1 si no tiene isotopos estables
"""

_TABLE = """
sym Z   name                mass     grp per cat          en    r_pm  tm_K    tb_K    rho      vec struct    abund_ppm price   k_th   E_GPa  dHox    tox crit radio
H   1   Hidrogeno           1.008    1   1   no_metal     2.20  53    13.99   20.28   0.00008988 1 gas       1400      4       0.181  -      -285.8  0   0    0
Li  3   Litio               6.94     1   2   alcalino     0.98  152   453.65  1603    0.534    1   bcc       20        90      84.8   4.9    -597.9  1   1    0
Be  4   Berilio             9.0122   2   2   alcalinoter  1.57  112   1560    2742    1.85     2   hcp       2.8       850     200    287    -609.4  3   1    0
B   5   Boro                10.81    13  2   metaloide    2.04  85    2349    4200    2.34     3   romboed   10        1000    27.4   320    -424.5  1   1    0
C   6   Carbono             12.011   14  2   no_metal     2.55  70    3915    4300    2.267    4   hexag     200       1       140    -      -196.8  0   1    0
N   7   Nitrogeno           14.007   15  2   no_metal     3.04  65    63.15   77.36   0.001251 5 gas       19        0.5     0.026  -      -      0   0    0
O   8   Oxigeno             15.999   16  2   no_metal     3.44  60    54.36   90.20   0.001429 6 gas       461000    0.3     0.027  -      -      0   0    0
F   9   Fluor               18.998   17  2   halogeno     3.98  50    53.53   85.03   0.001696 7 gas       585       2       0.028  -      -      3   1    0
Na  11  Sodio               22.990   1   3   alcalino     0.93  186   370.87  1156    0.968    1   bcc       23600     3       142    10     -415.9  1   0    0
Mg  12  Magnesio            24.305   2   3   alcalinoter  1.31  160   923     1363    1.738    2   hcp       23300     3.5     156    45     -601.6  0   1    0
Al  13  Aluminio            26.982   13  3   metal_pobre  1.61  143   933.47  2792    2.70     3   fcc       82300     2.4     237    70     -558.6  0   1    0
Si  14  Silicio             28.085   14  3   metaloide    1.90  111   1687    3538    2.329    4   diamante  282000    2.5     149    150    -455.4  0   1    0
P   15  Fosforo             30.974   15  3   no_metal     2.19  107   317.3   553     1.823    5   ortorromb 1050      3       0.236  -      -      2   1    0
S   16  Azufre              32.06    16  3   no_metal     2.58  105   388.36  717.8   2.067    6   ortorromb 350       0.1     0.205  -      -      0   0    0
K   19  Potasio             39.098   1   4   alcalino     0.82  227   336.53  1032    0.862    1   bcc       20900     10      102.5  3.5    -363.2  1   0    0
Ca  20  Calcio              40.078   2   4   alcalinoter  1.00  197   1115    1757    1.55     2   fcc       41500     2       201    20     -634.9  0   0    0
Sc  21  Escandio            44.956   3   4   trans        1.36  162   1814    3109    2.985    3   hcp       22        3800    15.8   74     -636.3  1   1    0
Ti  22  Titanio             47.867   4   4   trans        1.54  147   1941    3560    4.506    4   hcp       5650      12      21.9   116    -472.0  0   1    0
V   23  Vanadio             50.942   5   4   trans        1.63  134   2183    3680    6.11     5   bcc       120       30      30.7   128    -310.1  2   1    0
Cr  24  Cromo               51.996   6   4   trans        1.66  128   2180    2944    7.19     6   bcc       102       9       93.9   279    -379.9  2   0    0
Mn  25  Manganeso           54.938   7   4   trans        1.55  127   1519    2334    7.21     7   cubico    950       2       7.81   198    -385.2  1   1    0
Fe  26  Hierro              55.845   8   4   trans        1.83  126   1811    3134    7.874    8   bcc       56300     0.6     80.4   211    -274.7  0   0    0
Co  27  Cobalto             58.933   9   4   trans        1.88  125   1768    3200    8.90     9   hcp       25        33      100    209    -237.9  2   1    0
Ni  28  Niquel              58.693   10  4   trans        1.91  124   1728    3186    8.908    10  fcc       84        18      90.9   200    -239.7  2   1    0
Cu  29  Cobre               63.546   11  4   trans        1.90  128   1357.77 2835    8.96     11  fcc       60        9       401    130    -157.3  1   1    0
Zn  30  Zinc                65.38    12  4   trans        1.65  134   692.68  1180    7.14     12  hcp       70        2.8     116    108    -350.5  1   0    0
Ga  31  Galio               69.723   13  4   metal_pobre  1.81  135   302.91  2673    5.91     3   ortorromb 19        300     40.6   9.8    -365.6  1   1    0
Ge  32  Germanio            72.630   14  4   metaloide    2.01  122   1211.4  3106    5.323    4   diamante  1.5       1200    60.2   103    -290.0  1   1    0
As  33  Arsenico            74.922   15  4   metaloide    2.18  119   1090    887     5.727    5   romboed   1.8       2       50.2   8      -219.0  3   1    0
Se  34  Selenio             78.971   16  4   no_metal     2.55  120   494     958     4.809    6   hexag     0.05      30      0.52   10     -      2   0    0
Rb  37  Rubidio             85.468   1   5   alcalino     0.82  248   312.46  961     1.532    1   bcc       90        15000   58.2   2.4    -389.8  1   0    0
Sr  38  Estroncio           87.62    2   5   alcalinoter  0.95  215   1050    1655    2.64     2   fcc       370       7       35.4   15.7   -592.0  1   1    0
Y   39  Itrio               88.906   3   5   trans        1.22  180   1799    3609    4.472    3   hcp       33        120     17.2   63.5   -635.1  1   1    0
Zr  40  Circonio            91.224   4   5   trans        1.33  160   2128    4682    6.52     4   hcp       165       35      22.6   88     -550.3  0   0    0
Nb  41  Niobio              92.906   5   5   trans        1.60  146   2750    5017    8.57     5   bcc       20        45      53.7   105    -379.9  1   1    0
Mo  42  Molibdeno           95.95    6   5   trans        2.16  139   2896    4912    10.28    6   bcc       1.2       40      138    329    -248.4  1   0    0
Ru  44  Rutenio             101.07   8   5   trans        2.20  134   2607    4423    12.45    8   hcp       0.001     14000   117    447    -152.5  1   1    0
Rh  45  Rodio               102.91   9   5   trans        2.28  134   2237    3968    12.41    9   fcc       0.0002    150000  150    275    -115.0  1   1    0
Pd  46  Paladio             106.42   10  5   trans        2.20  137   1828.05 3236    12.023   10  fcc       0.015     35000   71.8   121    -85.4   1   1    0
Ag  47  Plata               107.87   11  5   trans        1.93  144   1234.93 2435    10.49    11  fcc       0.075     900     429    83     -31.1   1   0    0
Cd  48  Cadmio              112.41   12  5   trans        1.69  151   594.22  1040    8.65     12  hcp       0.15      3       96.6   50     -258.4  3   0    0
In  49  Indio               114.82   13  5   metal_pobre  1.78  167   429.75  2345    7.31     3   tetrag    0.25      250     81.8   11     -308.7  1   1    0
Sn  50  Estano              118.71   14  5   metal_pobre  1.96  140   505.08  2875    7.265    4   tetrag    2.3       30      66.8   50     -290.2  0   0    0
Sb  51  Antimonio           121.76   15  5   metaloide    2.05  140   903.78  1860    6.697    5   romboed   0.2       13      24.4   55     -234.7  2   1    0
Te  52  Teluro              127.60   16  5   metaloide    2.10  140   722.66  1261    6.24     6   hexag     0.001     70      2.35   43     -161.0  2   0    0
Cs  55  Cesio               132.91   1   6   alcalino     0.79  265   301.59  944     1.93     1   bcc       3         60000   35.9   1.7    -345.8  1   0    0
Ba  56  Bario               137.33   2   6   alcalinoter  0.89  222   1000    2170    3.51     2   bcc       425       3       18.4   13     -548.0  2   1    0
La  57  Lantano             138.91   3   6   lantanido    1.10  187   1193    3737    6.162    3   hexag     39        7       13.4   36.6   -597.9  1   1    0
Ce  58  Cerio               140.12   3   6   lantanido    1.12  182   1068    3716    6.770    3   fcc       66.5      5       11.3   33.6   -725.9  1   1    0
Nd  60  Neodimio            144.24   3   6   lantanido    1.14  181   1297    3347    7.01     3   hexag     41.5      85      16.5   41.4   -603.3  1   1    0
Sm  62  Samario             150.36   3   6   lantanido    1.17  180   1345    2067    7.52     3   romboed   7.05      15      13.3   49.7   -608.4  1   1    0
Gd  64  Gadolinio           157.25   3   6   lantanido    1.20  180   1585    3546    7.90     3   hcp       6.2       50      10.6   54.8   -602.8  1   1    0
Dy  66  Disprosio           162.50   3   6   lantanido    1.22  178   1680    2840    8.551    3   hcp       5.2       350     10.7   61.4   -600.4  1   1    0
Er  68  Erbio               167.26   3   6   lantanido    1.24  176   1802    3141    9.066    3   hcp       3.5       60      14.5   69.9   -606.0  1   1    0
Yb  70  Iterbio             173.05   3   6   lantanido    1.10  194   1097    1469    6.90     3   fcc       3.2       25      38.5   23.9   -580.8  1   1    0
Lu  71  Lutecio             174.97   3   6   lantanido    1.27  174   1925    3675    9.841    3   hcp       0.8       700     16.4   68.6   -598.9  1   1    0
Hf  72  Hafnio              178.49   4   6   trans        1.30  159   2506    4876    13.31    4   hcp       3         1000    23.0   78     -572.4  1   1    0
Ta  73  Tantalo             180.95   5   6   trans        1.50  146   3290    5731    16.69    5   bcc       2         250     57.5   186    -409.2  1   1    0
W   74  Wolframio           183.84   6   6   trans        2.36  139   3695    5828    19.25    6   bcc       1.25      35      173    411    -281.0  1   1    0
Re  75  Renio               186.21   7   6   trans        1.90  137   3459    5869    21.02    7   hcp       0.0007    3000    47.9   463    -212.0  1   0    0
Os  76  Osmio               190.23   8   6   trans        2.20  135   3306    5285    22.59    8   hcp       0.0001    40000   87.6   -      -131.3  2   0    0
Ir  77  Iridio              192.22   9   6   trans        2.20  136   2719    4701    22.56    9   fcc       0.001     150000  147    528    -137.9  1   1    0
Pt  78  Platino             195.08   10  6   trans        2.28  139   2041.4  4098    21.45    10  fcc       0.005     30000   71.6   168    -42.0   1   1    0
Au  79  Oro                 196.97   11  6   trans        2.54  144   1337.33 3129    19.30    11  fcc       0.004     75000   318    79     19.3    1   0    0
Hg  80  Mercurio            200.59   12  6   trans        2.00  151   234.32  629.88  13.534   12  liquido   0.085     35      8.30   -      -90.8   3   0    0
Tl  81  Talio               204.38   13  6   metal_pobre  1.62  170   577     1746    11.85    3   hcp       0.85      4500    46.1   8      -178.7  3   0    0
Pb  82  Plomo               207.2    14  6   metal_pobre  1.87  175   600.61  2022    11.34    4   fcc       14        2.2     35.3   16     -219.0  3   0    0
Bi  83  Bismuto             208.98   15  6   metal_pobre  2.02  156   544.7   1837    9.78     5   romboed   0.009     15      7.97   32     -191.6  1   1    0
Th  90  Torio               232.04   3   7   actinido     1.30  179   2115    5061    11.72    4   fcc       9.6       300     54.0   79     -613.0  2   0    1
U   92  Uranio              238.03   3   7   actinido     1.38  156   1405.3  4404    19.05    6   ortorromb 2.7       130     27.5   208    -541.0  3   0    1
"""

_HEADER = "sym Z name mass grp per cat en r_pm tm_K tb_K rho vec struct abund_ppm price k_th E_GPa dHox tox crit radio".split()
_FLOATS = {"mass", "en", "r_pm", "tm_K", "tb_K", "rho", "abund_ppm", "price", "k_th", "E_GPa", "dHox"}
_INTS = {"Z", "grp", "per", "vec", "tox", "crit", "radio"}


def _parse():
    out = {}
    for line in _TABLE.strip().splitlines():
        parts = line.split()
        if parts[0] == "sym":
            continue
        if len(parts) != len(_HEADER):
            raise ValueError(
                f"Fila mal formada ({len(parts)} campos, se esperaban {len(_HEADER)}): {parts[0]}"
            )
        rec = {}
        for key, raw in zip(_HEADER, parts):
            if raw == "-":
                rec[key] = None
            elif key in _FLOATS:
                rec[key] = float(raw)
            elif key in _INTS:
                rec[key] = int(raw)
            else:
                rec[key] = raw
        rec["name"] = rec["name"].replace("_", " ")
        out[rec["sym"]] = rec
    return out


ELEMENTS = _parse()


def get(sym):
    """Devuelve el registro de un elemento o lanza KeyError con mensaje util."""
    try:
        return ELEMENTS[sym]
    except KeyError:
        raise KeyError(
            f"'{sym}' no esta en la tabla de Mnemesis. "
            f"Disponibles: {', '.join(sorted(ELEMENTS))}"
        ) from None


def require(sym, field):
    """Lee un campo obligatorio. Si falta, falla ruidosamente en vez de
    devolver None y contaminar un calculo aguas abajo (leccion de skills.md:
    un fallo nunca debe parecerse a un resultado normal)."""
    val = get(sym).get(field)
    if val is None:
        raise ValueError(f"Dato ausente: {sym}.{field} no esta tabulado en Mnemesis")
    return val
