# Mnemesis Forge

**Cribado computacional de materiales y combustibles.** Combina los elementos de la
tabla periódica, somete cada candidato a bancos de ensayo que reproducen entornos
reales de servicio, y ordena lo que sobrevive por su potencial de comercialización.

👉 **[Ver la interfaz](https://claude.ai/code/artifact/0656834b-2c5e-4049-961f-6ba6e36a4c30)**

---

## Lo primero: lo que esto NO hace

**No crea elementos nuevos, y ningún software puede.** Un elemento nuevo (Z > 118)
exige un acelerador de iones pesados, se produce átomo a átomo y dura milisegundos.
No hay muestra, no hay propiedad material, no hay producto. Su valor comercial es
exactamente cero.

Donde sí hay descubrimiento vendible es en el **espacio de combinaciones**: con 70
elementos útiles hay más de 12 millones de quintetos posibles y la industria ha
explorado unos pocos miles. Ahí es donde trabaja este motor. Es el mismo método
—*high-throughput screening*— con el que se encontraron las superaleaciones de
turbina y las aleaciones de alta entropía.

## Qué hace

| | |
|---|---|
| **132.110** | composiciones evaluadas por ejecución (~15 s, sin dependencias) |
| **70** | elementos con datos tabulados y trazados |
| **231** | pares con entalpía de mezcla, separados por nivel de confianza |
| **10** | bancos de ensayo (turbina, criogenia, reactor, fondo marino, cohete…) |
| **31** | combustibles, 7 de ellos formulaciones mezcladas |
| **6** | mercados con pesos explícitos y discutibles |

El embudo tiene tres filtros en cascada, del más barato al más caro:

1. **Física** — ¿puede existir? Criterio de Yang-Zhang. Aquí muere el 80-90%.
2. **Entorno** — ¿sobrevive donde va a trabajar? Diez bancos de ensayo.
3. **Economía** — ¿se puede vender? Coste, suministro, toxicidad, fabricabilidad.

## Uso

Python 3.8+, **cero dependencias**.

```bash
python3 engine/report.py      # ejecuta el cribado -> out/results.json
python3 engine/build_ui.py    # inyecta el informe -> out/mnemesis.html
python3 tests/test_engine.py  # 45 comprobaciones contra materiales reales
```

`out/mnemesis.html` es autocontenido: se abre en cualquier navegador sin servidor.

## Cómo está validado

El motor no se valida contra sí mismo, sino contra materiales reales cuyo
comportamiento está publicado. Si la suite cae, cualquier ranking que produzca es
papel mojado.

| Comprobación | Resultado |
|---|---|
| Aleación Cantor `CoCrFeMnNi` | predice FCC monofásica ✓ |
| Refractaria Senkov `HfNbTaTiZr` | predice BCC monofásica ✓ |
| `AlCoCrFeNi` | predice dúplex FCC+BCC ✓ |
| Densidad del Inconel 718 | 8.29 vs 8.19 g/cm³ reales |
| Conductividad del inox 316 | 15.0 vs 15 W/m·K (la regla de mezclas daría 84) |
| Zircaloy-4 en núcleo de reactor | aprueba ✓ (es la vaina real) |
| Cantor en núcleo de reactor | suspende por el cobalto ✓ (activación a Co-60) |
| Inox 316 en agua de mar | suspende, PREN ≈ 25 ✓ |
| Superduplex 2507 en agua de mar | aprueba, PREN ≈ 42 ✓ |
| Acero al carbono en criogenia | suspende por transición dúctil-frágil ✓ |
| Energía de 7 combustibles metálicos | error máximo **1.1%** frente a publicado |

## Criterios implementados

| Qué | Criterio | Referencia |
|---|---|---|
| Formación de fase | `δ ≤ 6.6%` y `Ω ≥ 1.1` | Yang & Zhang, *Mater. Chem. Phys.* 132 (2012) |
| Estructura cristalina | regla del VEC | Guo et al., *J. Appl. Phys.* 109 (2011) |
| Entalpía de mezcla | modelo de Miedema | Takeuchi & Inoue, *Mater. Trans.* 46 (2005) |
| Conductividad térmica | corrección tipo Nordheim | calibrada sobre inox 316 |
| Corrosión por cloruros | `PREN = %Cr + 3.3·%Mo + 1.65·%W` | norma de facto del sector |
| Choque térmico | `R' = k/(E·α)` | índice de Kingery |
| Neutrónica | sección eficaz de captura térmica | tabulada, en barns |
| Combustibles metálicos | `ΔHf(óxido) / masa de metal` | derivado, no copiado |

## Honestidad del dato

Regla dura del proyecto: **cuando no hay base para un número, el motor devuelve
`desconocido` y descarta el candidato. Nunca rellena con cero.** Un cero pasaría el
filtro de disolución sólida y colaría aleaciones inexistentes hasta el ranking final.

- **199 pares de confianza alta** — recopilación de Takeuchi-Inoue.
- **32 pares de confianza media** — sistemas Mg-X y Li-X inmiscibles; el signo está
  fuera de duda, el valor exacto puede bailar. Marcados en la interfaz.
- **Estimación de Miedema** solo entre metales de transición, porque en pares
  transición/no-transición el modelo necesita un término R que no tenemos tabulado
  y produce ceros falsos. Validada contra los 109 pares conocidos:
  **error absoluto medio 7 kJ/mol**, 81% dentro de ±10.
- Los precios son **orden de magnitud** (referencia 2024-2025). Sirven para ordenar
  candidatos, no para presupuestar.

## Límites

- **No es DFT ni dinámica molecular.** Un candidato que pasa todos los filtros es una
  **hipótesis priorizada**, no un material verificado. El paso siguiente real es DFT
  y después horno de arco y difracción de rayos X.
- **Predice formación, no estabilidad.** Muchas aleaciones que cumplen `Ω ≥ 1.1` se
  descomponen tras mil horas a 900 K.
- **No dice nada de procesabilidad real**: colabilidad, soldabilidad, conformado.
- **Las notas son relativas al conjunto evaluado**, no absolutas.
- La regla del VEC se calibró con aleaciones concentradas; para aceros diluidos el
  motor marca confianza baja en vez de disimularlo.

## Estructura

```
engine/
  data/elements.py   70 elementos: 21 propiedades, huecos declarados
  data/hmix.py       231 pares de entalpía + fallback de Miedema acotado
  data/fuels.py      combustibles de referencia y estequiometrías de óxido
  data/extra.py      secciones eficaces de neutrones, dilatación térmica, PREN
  alloys.py          composición -> fase, estructura y propiedades
  environments.py    10 bancos de ensayo, 10 tipos de ensayo
  fuels.py           energía, coste, emisiones y ajuste a mercado
  generate.py        generador combinatorio por paletas
  screen.py          el embudo de tres filtros
  superheavy.py      la respuesta honesta sobre los elementos nuevos
  report.py          ejecuta todo -> out/results.json
  build_ui.py        inyecta el informe -> out/mnemesis.html
ui/template.html     la interfaz
tests/test_engine.py 45 comprobaciones contra la realidad
memory/              el conector neuronal (ver CLAUDE.md)
```
