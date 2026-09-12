"""Elementos superpesados: la respuesta honesta a "crear elementos nuevos".

Esto no es un modulo de cribado. Esta aqui porque la pregunta "?podemos crear
elementos nuevos y comercializarlos?" merece una respuesta con numeros en vez de
un no seco, y porque un motor que se callara este limite estaria vendiendo humo.

Los hechos, verificables
------------------------
- La tabla periodica esta COMPLETA hasta Z=118 (oganeson). No quedan huecos.
- Los cuatro ultimos (nihonio 113, moscovio 115, teneso 117, oganeson 118) se
  confirmaron en 2015-2016. Del oganeson se han fabricado unos POCOS ATOMOS en
  toda la historia, de uno en uno.
- El siguiente, Z=119, se lleva persiguiendo desde 2018 en RIKEN (Japon) y en
  el JINR (Dubna). A fecha de hoy no hay sintesis confirmada.
- Las vidas medias de la zona caen a milisegundos o menos. La "isla de
  estabilidad" prevista alrededor de Z=114-126 podria llegar a minutos u horas
  en el mejor de los casos teoricos: sigue siendo inutilizable como material.
- Coste: un acelerador de iones pesados dedicado meses a un blanco para producir
  un punado de atomos. No hay escala posible. No existe mercado.

Conclusion operativa: el valor economico de sintetizar elementos nuevos es CERO,
y lo seguira siendo mientras la fisica nuclear sea la que es. Por eso Mnemesis
trabaja en COMBINACIONES de los elementos que existen, que es donde si hay
descubrimientos con salida industrial.

Lo unico que si se puede calcular sobre ellos es extrapolacion periodica, y se
ofrece etiquetada como lo que es: curiosidad cientifica.
"""

# Extrapolaciones por tendencia de grupo. Son PREDICCIONES teoricas publicadas,
# no medidas: de estos elementos no se ha pesado jamas una muestra macroscopica
# porque nunca ha existido una.
PREDICTED = [
    dict(Z=119, name="Ununennio (Uue)", group=1, period=8,
         analogue="Francio / Cesio",
         predicted="Alcalino. Densidad estimada 3 g/cm3, fusion ~0-30 C. "
                   "Los efectos relativistas contraen su orbital 8s, asi que "
                   "seria MENOS reactivo que el cesio, rompiendo la tendencia "
                   "del grupo.",
         status="No sintetizado. Intentos en curso en RIKEN y JINR desde 2018."),
    dict(Z=120, name="Unbinilio (Ubn)", group=2, period=8,
         analogue="Radio / Bario",
         predicted="Alcalinoterreo. Densidad estimada 7 g/cm3. Se espera que "
                   "sea el limite practico de la sintesis por fusion fria.",
         status="No sintetizado. Intentos fallidos documentados en GSI (2011)."),
    dict(Z=126, name="Unbihexio (Ubh)", group=None, period=8,
         analogue="Sin analogo claro: bloque g",
         predicted="Candidato central de la isla de estabilidad segun varios "
                   "modelos de capas. Estrenaria el bloque g, una region de la "
                   "tabla periodica que nunca se ha observado.",
         status="Totalmente hipotetico. Fuera del alcance de los aceleradores "
                "actuales."),
]

VERDICT = dict(
    question="?Puede Mnemesis crear elementos nuevos y comercializarlos?",
    answer="No, y ningun software puede.",
    why="Un elemento nuevo exige un acelerador de iones pesados, produce atomos "
        "de uno en uno y dura milisegundos. No hay muestra, no hay propiedad "
        "material, no hay producto. El valor comercial es exactamente cero.",
    instead="Donde si hay descubrimiento comercializable es en el espacio de "
            "COMBINACIONES: con 70 elementos utiles hay mas de 12 millones de "
            "quintetos posibles, y la industria ha explorado unos pocos miles. "
            "Ahi es donde trabaja este motor.",
)
