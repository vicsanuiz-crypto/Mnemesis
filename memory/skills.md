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
