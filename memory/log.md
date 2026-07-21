# Bitácora

Entradas nuevas **arriba**. Formato: fecha · qué se decidió · con qué evidencia.

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
