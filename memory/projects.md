# Proyectos

## 🤖 AI-Trader — trading automatizado (EN PAPEL)

`C:\Users\Asus\Downloads\ai-trader` · repo `vicsanuiz-crypto/ai-trader` · deploy
automático a **Railway** al pushear a `main`.

**Arquitectura:** Railway = instancia principal 24/7 (bot de Telegram, agentes que
operan, monitor). Local = **solo visor** (`TG_BOT_DISABLED=1`, guard 409: no opera).
Estado persistente en volumen `/data` (`DATA_DIR`). Panel protegido con `APP_TOKEN`.

**REGLA DE ORO (acordada con Víctor):** ❗ **NO pasar a dinero real ni escalar
capital** hasta que el *edge v2* (trades desde 5 jun 2026) muestre **profit factor
> 1.2 con ≥ 20 trades cerrados**. A 8 jul 2026 aún no se cumple de forma robusta.

### Estado de los agentes (auditados uno a uno, jul 2026)

| Agente | Estado | Evidencia |
|---|---|---|
| 🟢 Largos | **ON** · premisa validada | backtest 92 acciones: PF 1.35→1.53, avgR +0.21→+0.30, OOS≥IS |
| 🔴 Cortos | **PAUSADO** (`SHORT_PAUSED`) | todas las premisas cortas pierden (PF 0.6-0.75) |
| 🥇 Oro (GLD) | ON · táctico + refugio, solo largo | — |
| 🛢 Crudo (USO) | ON · macro (DXY, XLE), cada 4h | **sin auditar todavía** |
| 🌊 Cripto Swing | **ON** · Donchian 20/10 + SMA50 | 241% ret, maxDD 45% vs 80% HODL, Sharpe 0.70 |
| 🤖 Autotrade | ON · escáner horario | PF 2.97 en v2, pero frágil (ver abajo) |
| ⏱ Intradía | **RETIRADO** · código eliminado | 12 configs, 3 timeframes, ~1.500 sesiones: sin edge |
| 🎯 APEX v2 | **OFF, y así debe seguir** | sin edge en cripto; en acciones, peor que Largos |

**Robustez (clave):** el PF 2.17 aparente del sistema era **frágil**: sin los 3
mejores trades caía a 1.07, y el 79% del P&L venía de un solo agente. Por eso
seguimos en papel. Comando `/robustez` hace este test.

**Riesgo dimensionado con datos:** las 10 criptos correlacionan **0.75** → 5
posiciones ≈ 1.2 apuestas independientes. Por eso el tope de exposición es del
**BLOQUE** cripto (25%), no por agente (`cryptoGrossExposure`).

**Broker:** Alpaca spot para cripto, decidido con datos — gana a Binance porque
los futuros cobran *funding* por mantener, y esta estrategia aguanta semanas
(Alpaca +3.3 pp de CAGR con funding típico del 11%).

**Herramientas permanentes:** `backtest-*.mjs` en el repo. **Ninguna señal se
despliega sin pasar por ahí** (PF≥1.2 y avgR>0 en in-sample Y out-of-sample).

---

## 📚 LOMLOE — app docente (EN PRODUCCIÓN)

`C:\Users\Asus\.claude\Proyectos\lomloe-cloud` · **no es repo git** · se despliega
arrastrando a **Netlify**.

PWA de un solo archivo (`index.html` con CSS/JS inline) + `sw.js` + `manifest.json`.
Etapas conmutables: Primaria (RD 157/2022) y Secundaria ESO (Decreto 30/2023 Canarias).

**Persistencia:** `localStorage` (claves `lomloe_*`) + **Firebase/Firestore** con
login Google y whitelist (admin: vicsanuiz@gmail.com). Sync resuelto por marca de
tiempo (`_clientTime`, gana el más reciente). ⚠️ **Toda clave nueva debe añadirse
a `SYNC_KEYS`** o no sincroniza.

**Adaptación curricular:** `adaptCurricular[alumnoId][subj]` con tipo AC/ACUS,
`cursoRef` (incluye Infantil I3/I4/I5) y 8 campos DAC. `getCicloEfectivo` decide
los criterios (ACUS → curso de referencia; Infantil → 'INF', cualitativa).

---

## 💰 CFO familiar — análisis financiero del hogar

Flujo real: **Víctor manda el PDF del extracto de ING → yo hago el informe.**
(Se abandonó automatizarlo: los agregadores PSD2 exigen verificación de empresa,
inviable como particular. La infraestructura n8n/Docker quedó montada pero NO es
el camino — ver [[skills]].)

**Situación (mayo 2026):** aportación planificada 2.800 €/mes (Víctor 800 + Miriam
2.000) frente a un gasto real ≈ **4.870 €/mes** → desfase estructural ≈ **−2.000 €/mes**
que tapan con inyecciones desde ahorros.

**Las 3 fugas recurrentes:** efectivo en cajeros (~680 €, sin rastro), salud/estética
(~925 €), restaurantes/bares (~472 €). ⚠️ **La estética es tema delicado** (mayoría
de Miriam): tratar con tacto, sin señalar culpables.

---

## 🧠 Mnemesis — este repo

`repo vicsanuiz-crypto/Mnemesis` · rama `claude/materials-fuels-agent-hhp4xo`.

Dos cosas conviven aquí:
1. **El conector neuronal** (`CLAUDE.md` + `memory/`) — este cerebro externo.
2. **Mnemesis Forge** (`engine/`, `ui/`, `tests/`) — motor de cribado computacional
   de materiales y combustibles. Ver abajo.

⚠️ **Aviso histórico:** una sesión anterior afirmó haber creado y pusheado el
conector neuronal en la rama `claude/neural-connector-chats-skills-1mbwse`. **Ese
push nunca llegó** — se verificó con `git ls-remote` y esa rama no existía. Lección:
**verificar los push, no darlos por hechos.**

### 🗑️ Agente de control Android — RETIRADO (12 sep 2026)

Código eliminado del repo por decisión de Víctor: "no vamos a seguir con el agente
para el móvil". Vivía en `agent/` (TypeScript + Gemini) y `android/` (Kotlin,
AccessibilityService). Recuperable desde el historial git o desde la rama
`claude/android-control-agent-3u45kc`. No se auditó nunca en detalle.

---

## ⚗️ Mnemesis Forge — cribado de materiales y combustibles (12 sep 2026)

Python 3, **cero dependencias**. `python3 engine/report.py && python3 engine/build_ui.py`
produce `out/mnemesis.html`, un panel autocontenido.
Interfaz publicada: https://claude.ai/code/artifact/0656834b-2c5e-4049-961f-6ba6e36a4c30

**Qué hace:** genera 132.110 composiciones desde 6 paletas con intención metalúrgica,
las pasa por un embudo de 3 filtros (física → entorno → economía) y las ordena para
6 objetivos industriales. Aparte, compara 31 combustibles (13 de referencia, 11
metálicos derivados de la tabla periódica, 7 formulaciones) contra 6 mercados.

**⛔ Límite declarado desde el minuto uno:** NO crea elementos nuevos. Z>118 exige
acelerador, produce átomos sueltos que duran milisegundos, valor comercial cero.
El valor está en las combinaciones, no en elementos inéditos. Está escrito en el
README, en `engine/superheavy.py` y en la pestaña «Método» de la interfaz.

**Validación (lo que da crédito al motor):** 45 tests contra materiales reales
publicados. Cantor→FCC, Senkov→BCC, AlCoCrFeNi→dúplex, Inconel 718 ρ=8.29 vs 8.19,
Zircaloy-4 aprueba reactor, Cantor lo suspende por el cobalto (activación Co-60),
inox 316 suspende agua de mar (PREN 25) y superduplex 2507 la aprueba (PREN 42),
7 combustibles metálicos con error máximo 1.1%.

**Criterios:** Yang-Zhang (δ≤6.6%, Ω≥1.1) para fase · VEC de Guo para estructura ·
Miedema/Takeuchi-Inoue para entalpía · Nordheim para conductividad · PREN para
cloruros · Kingery para choque térmico · sección eficaz para neutrónica.

**Regla dura de dato:** si no hay base para un número, devuelve `desconocido` y
descarta el candidato. **Nunca rellena con cero** — un cero pasaría el filtro de
disolución sólida y colaría aleaciones inexistentes hasta el ranking final.

Relacionado: [[victor]] · [[skills]] · [[connectors]]
