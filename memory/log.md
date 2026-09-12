# Bitácora

Entradas nuevas **arriba**. Formato: fecha · qué se decidió · con qué evidencia.

---

## 12 sep 2026 — Se retira el agente Android y nace Mnemesis Forge

**Decisión de Víctor:** "no vamos a seguir con el agente para el móvil". Se elimina
`agent/` (TypeScript + Gemini) y `android/` (Kotlin). Recuperable del historial git
y de la rama `claude/android-control-agent-3u45kc`. **Se conservaron `CLAUDE.md` y
`memory/`** pese al "borra el contenido del repo": son el cerebro externo, no el
proyecto retirado. Se le avisó explícitamente por si quería borrarlos también.

**Lo primero que se le dijo, antes de construir nada:** su idea de "construir
elementos nuevos" **no es posible en software**. Z>118 exige acelerador de iones
pesados, produce átomos de uno en uno y dura milisegundos: valor comercial cero.
Lo que sí vale es el cribado de COMBINACIONES, que es lo que se ha construido.
Esa distinción queda escrita en el README, en `engine/superheavy.py` y en la
interfaz, para que ninguna sesión futura la difumine.

**Qué se entregó:** motor Python sin dependencias que evalúa 132.110 composiciones
en ~15 s, las pasa por un embudo física→entorno→economía para 6 objetivos
industriales, compara 31 combustibles contra 6 mercados, y vuelca todo en un panel
HTML autocontenido. 45 tests de regresión contra materiales reales publicados.

**Cinco errores propios, encontrados y corregidos con evidencia:**
1. **Fallback de Miedema fuera de dominio** → daba −0.1 kJ/mol en Ir-Al (real: muy
   negativo). Se acotó a pares transición-transición. Validado: error medio
   **7 kJ/mol**, 81% dentro de ±10 sobre 109 pares conocidos.
2. **Regla de mezclas para conductividad térmica** → 84 W/m·K en un inox 316 cuyo
   valor real es **15**. Se metió corrección tipo Nordheim, calibrada; Inconel 718
   da ahora 12.9 frente a 11.4 reales.
3. **Umbral de choque térmico un orden de magnitud arriba** → suspendía el **100%**
   de los candidatos. Recalibrado con anclas reales (inox 0.004, W 0.094, Cu 0.187).
4. **Temperatura de gas confundida con temperatura de metal** → los álabes de
   turbina real trabajan por encima del punto de fusión de su aleación gracias a
   refrigeración y barrera térmica. Sin esa distinción, turbina daba 0 supervivientes.
5. **Normalización lineal de una magnitud que abarca 4 décadas** (coste por kWh):
   el carbón y el aluminio, con un factor 20 entre ellos, salían casi empatados.

**Dos errores más que resultaron ser del test, no del motor:** di por apto el inox
316 en agua de mar (no lo es, PREN≈25) y afirmé que el wolframio funde más alto que
cualquier elemento (es el metal que más; el carbono funde más alto). Todo en [[skills]].

**Interfaz publicada:** https://claude.ai/code/artifact/0656834b-2c5e-4049-961f-6ba6e36a4c30

---

## 21 jul 2026 — Se construye Mnemesis de verdad + auditoría completa de AI-Trader

**Mnemesis:** se crea el conector neuronal (`CLAUDE.md` + `memory/`) con conocimiento
verificado. Motivo: una sesión anterior dijo haberlo pusheado en la rama
`claude/neural-connector-chats-skills-1mbwse`, pero **`git ls-remote` demostró que
esa rama nunca existió**. Solo se ha escrito lo que consta; los proyectos sin
contexto (VoxAI, alarma, etc.) se dejan como hueco declarado, no se inventan.

**AI-Trader — auditoría agente por agente:**
- 🔴 **Cortos → PAUSADO.** Se probaron todas las premisas cortas, incluida la idea
  de Víctor de aprovechar las correcciones dentro del alza (reversión a la media).
  Todas pierden (PF 0.6-0.75). El scalp acierta 60% pero pierde igual: los squeezes
  se comen las correcciones.
- 🎯 **APEX v2 → confirmado OFF.** Sin edge en cripto (OOS PF 0.94). En acciones sí
  hay señal, pero Largos rinde más con ~60% más operaciones. Su validación original
  (GOOG/MSFT) eran 2 símbolos con n=14-17: sin valor estadístico.
- 🌊 **Cripto Swing → activado** con tope de exposición del bloque (25%) tras medir
  la correlación real (0.75).
- ⏱ **Intradía → código eliminado** (~460 líneas). Verificado que nunca operó.

**Incidente destapado:** el escáner llevaba **días fallando cada 30 min** — la
config de producción apuntaba a un modelo de IA muerto. Se implementó
**auto-reparación**. Lo descubrió el arreglo de observabilidad, no una revisión.

**Errores propios registrados:** (1) quitar modelos del catálogo sin comprobar cuál
estaba seleccionado en producción; (2) comparar el Donchian con salidas ajenas, lo
que lo hacía parecer malo. Ambos en [[skills]].

---

## 8 jul 2026 — Regla de proceso: nada se despliega sin backtest

Tras retirar el intradía (12 configuraciones, 3 timeframes, ~1.500 sesiones, sin
edge) se fija la regla: **PF ≥ 1.2 y avgR > 0 en IS y OOS** antes de desplegar
cualquier señal. Los backtesters quedan como patrimonio del proyecto.

---

## Jun 2026 — Se abandona automatizar el CFO familiar

Los agregadores PSD2 exigen verificación de empresa; el tier gratuito solo da bancos
de prueba. **No es viable como particular.** Se vuelve al flujo simple: Víctor manda
el PDF, yo hago el informe. De aquí sale la regla de **validar viabilidad antes de
montar infraestructura** ([[skills]]).

---

## Jun 2026 — Regla de oro de AI-Trader

**No pasar a dinero real hasta PF > 1.2 con ≥ 20 trades** en la muestra limpia
(post-arreglos, desde 5 jun 2026). Motivo: un incidente previo llegó a apalancar la
cuenta 2:1 por sizing sobre buying power con controles fail-open. Todo corregido,
pero la regla se mantiene.
