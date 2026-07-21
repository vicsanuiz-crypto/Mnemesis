# Mapa del conector neuronal

Última actualización: **21 jul 2026**

## Empieza aquí

| Archivo | Qué contiene | Léelo cuando… |
|---|---|---|
| [[victor]] | Quién es Víctor, cómo trabaja, qué espera | **siempre**, antes de nada |
| [[projects]] | Estado de cada proyecto | vayas a tocar uno |
| [[skills]] | Lecciones y patrones reutilizables | diseñes o valides algo |
| [[connectors]] | APIs y servicios (sin secretos) | necesites integrar algo |
| [[log]] | Bitácora de sesiones | quieras contexto histórico |

## Cómo se conecta todo

```
                        ┌──────────────┐
                        │   VÍCTOR     │  docente en Canarias · novato en
                        │  (victor.md) │  trading · trato de "socio"
                        └──────┬───────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
   ┌────▼─────┐          ┌─────▼──────┐        ┌──────▼──────┐
   │ AI-TRADER│          │   LOMLOE   │        │ CFO FAMILIAR│
   │ trading  │          │  docencia  │        │  finanzas   │
   │  (papel) │          │   (PWA)    │        │  del hogar  │
   └────┬─────┘          └────────────┘        └──────┬──────┘
        │                                             │
        │  comparten método:                          │
        └──────────► [[skills]] ◄─────────────────────┘
              "validar con datos antes de desplegar"
              "hacer yo el trabajo, no delegárselo"
```

**El hilo que une todo:** Víctor paga por que el trabajo se haga, no por teclear
él. Y en cualquier cosa que toque dinero, **nada se despliega sin evidencia**.

## Estado en una línea

- **AI-Trader** → en papel, agentes auditados uno a uno; regla de oro sin cumplir aún.
- **LOMLOE** → app docente en producción (Netlify + Firebase).
- **CFO familiar** → análisis manual mensual del extracto ING; desfase ~2.000 €/mes.
- **Mnemesis** → este cerebro + un agente de control Android en `agent/` y `android/`.

## Huecos conocidos (para rellenar en futuras sesiones)

Víctor tiene más proyectos de los que hay memoria aquí. Si trabajas en alguno que
no aparezca en [[projects]], **añádelo** en vez de asumir que no existe. No se han
documentado por falta de contexto, no porque no importen.
