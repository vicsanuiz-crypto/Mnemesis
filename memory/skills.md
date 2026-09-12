# Lecciones y patrones reutilizables

Lo aprendido a base de equivocarse. Vale para cualquier proyecto, no solo el que
lo originó.

## Validar antes de construir

**Validar la VIABILIDAD antes de montar infraestructura.** (Origen: CFO familiar,
jun 2026 — días perdidos en n8n/Docker/Salt Edge que chocaron con un muro previsible:
PSD2 exige verificación de empresa.) Si un camino tiene un muro estructural, decirlo
el primer día, no el quinto.

**Ninguna estrategia se despliega sin backtest.** (Origen: AI-Trader.) Umbral:
**PF ≥ 1.2 y avgR > 0 en in-sample Y out-of-sample**. Si solo pasa en uno, es
sobreajuste. Herramientas: `backtest-*.mjs` en el repo de AI-Trader.

## Metodología de backtest (5 reglas, jul 2026)

1. **La regla de SALIDA define el edge tanto como la entrada.** Comparar dos
   estrategias forzándoles los mismos brackets NO es comparar. Al Donchian se le
   impusieron las salidas de APEX (target ≈9%) y salió negativo, cuando con las
   suyas da PF 2.08 — sus ganadores promedian **+44.65%** y quedaban truncados.
   Cada estrategia se mide con SUS salidas.
2. **Validar en la clase de activo donde se va a operar.** APEX se validó en
   forex/acciones y se desplegó en cripto. No transfiere.
3. **Desconfiar de validaciones con pocos símbolos.** GOOG+MSFT con n=14-17 no
   valida nada. Sobre 92 valores el cuadro cambió por completo (GOOGL incluso perdía).
4. **Dimensionar contando la correlación.** 10 criptos correlacionan 0.75 → 5
   posiciones ≈ 1.2 apuestas independientes. El tope debe ser del **bloque**.
5. **Las barridas de API en ráfaga contaminan los resultados.** Groq bloqueó por
   rate-limit y pareció que todos sus modelos estaban muertos. Verificar con
   llamadas espaciadas antes de declarar algo roto.

## Un hueco declarado vale más que un número inventado

**Cuando no hay base para un dato, devolver `desconocido` y descartar, nunca
rellenar con un valor por defecto.** (Origen: Mnemesis Forge, sep 2026.) En el motor
de aleaciones, un `0` en la entalpía de mezcla no es neutro: **pasa el filtro de
disolución sólida**, así que rellenar huecos con cero habría colado aleaciones
inexistentes hasta el ranking final, indistinguibles de las buenas. El valor por
defecto más «inocuo» suele ser el que más contamina.

Corolario: **acotar el dominio de un modelo en vez de extrapolarlo.** El fallback de
Miedema daba −0.1 kJ/mol para Ir-Al (real: fuertemente exotérmico) porque en pares
transición/no-transición falta un término R. Solución correcta: restringir el modelo
a su dominio válido y declarar el resto desconocido. Al validarlo contra los 109
pares conocidos dentro de ese dominio: **error medio 7 kJ/mol, 81% dentro de ±10**.

## Escala equivocada = filtro que suspende a todo el mundo

**Antes de fijar un umbral, calcular el valor de dos o tres casos conocidos con la
propia fórmula.** (Origen: Mnemesis Forge, sep 2026.) Puse el umbral del índice de
choque térmico un orden de magnitud arriba porque recordé mal la escala. Síntoma:
**el 100% de los candidatos suspendía** el ensayo. Un filtro que rechaza todo o
acepta todo es casi siempre un umbral mal calibrado, no un hallazgo.

Relacionado: **una regla de mezclas no vale para cualquier propiedad.** Para
densidad va bien; para conductividad térmica da 84 W/m·K en un inox 316 cuyo valor
real es **15**, porque los átomos de soluto dispersan los electrones. Hubo que meter
una corrección tipo Nordheim. Contraste tras arreglarlo: Inconel 718 da 12.9 frente
a 11.4 reales.

## Normalizar en lineal lo que abarca décadas

**Si una magnitud abarca varios órdenes de magnitud, normalizar en logaritmo.**
(Origen: Mnemesis Forge, sep 2026.) El coste por kWh iba de 0.014 a 61 USD. Con
min-max lineal, el outlier caro aplastaba la escala y el carbón y el aluminio —que
se llevan un **factor 20**— quedaban prácticamente empatados en el eje de coste.

## Validar contra la realidad publicada, no contra uno mismo

**Los tests de un motor predictivo deben contrastar contra casos reales conocidos,
no contra su propia salida.** (Origen: Mnemesis Forge, sep 2026.) Las 45
comprobaciones miden si el motor reproduce lo que ya se sabe: Zircaloy-4 aprueba el
reactor, el inox 316 suspende agua de mar, el acero al carbono se rompe en criogenia.

**Y cuando un test falla, la primera hipótesis es que el test está mal.** De los
cuatro fallos iniciales, **dos eran errores míos en el enunciado del test**: di por
apto el inox 316 en agua de mar (no lo es, PREN≈25) y afirmé que el wolframio funde
más alto que cualquier elemento (el carbono funde más alto; es el metal que más).

## Observabilidad: los fallos silenciosos son los caros

**Un fallo nunca debe parecerse a un resultado normal.** (Origen: AI-Trader, jul 2026.)
La llamada a la IA fallaba y la función devolvía lista vacía → el agente reportaba
"Sin señales de COMPRA", **indistinguible de un mercado tranquilo**. Llevaba días
perdiendo corridas sin que nadie lo supiera.

Al arreglarlo (marcar el fallo y avisar explícitamente) **se descubrió el problema
real en horas**. Corolario: cuando un sistema "no hace nada", la primera hipótesis
es que está roto, no que no había nada que hacer.

## Configuración persistida ≠ catálogo

**Quitar una opción de una lista NO cambia la que ya está seleccionada y guardada.**
(Origen: AI-Trader, jul 2026.) Se eliminaron modelos de IA muertos del selector,
pero producción seguía con uno de ellos persistido en su config → todas las corridas
fallaban. **Verificar el estado real, no solo el catálogo.**

Patrón de solución: **auto-reparación**. Si la config apunta a algo muerto, cambiar
a un valor seguro conocido, persistirlo y avisar — en vez de fallar para siempre.

## Verificar, no asumir

- **Verificar los push.** Una sesión afirmó haber pusheado el conector neuronal;
  `git ls-remote` demostró que la rama no existía. Comprobar, no dar por hecho.
- **Comprobar en el sitio correcto.** Se miró el estado en la instancia local
  cuando la que manda es la de producción. Extrapolar de la máquina equivocada
  es igual de malo que no mirar.
- **Ante "¿lo comprobaste o lo asumiste?"** de Víctor: casi siempre lo asumí.

## Higiene de datos

**Separar la muestra contaminada de la limpia.** AI-Trader distingue el histórico
total (con un incidente de apalancamiento) del *sistema v2* (post-arreglos, desde
5 jun 2026). Las decisiones se toman **solo** con la muestra limpia; la vieja se
muestra como contexto, nunca como criterio.

**Atribuir bien desde el origen.** Un bug hacía que los trades de un agente se
registraran sin etiqueta y cayeran en el saco "manual" → parecía que Víctor operaba
a mano. La atribución se fija **al abrir** la posición, no al cerrarla.

Relacionado: [[projects]] · [[victor]]
