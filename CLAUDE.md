# Mnemesis — conector neuronal de Víctor

> **Instrucción para cualquier sesión que abra este repo: lee `memory/` ANTES de nada.**
> Empieza por `memory/index.md` (mapa de cómo se conecta todo) y luego el archivo
> del proyecto en el que vayas a trabajar. No arranques en blanco.

## Qué es esto

Un **cerebro externo versionado**. No es memoria mágica: son archivos que se cargan
al empezar y se actualizan al cerrar algo importante. La ventaja frente a la memoria
interna de una herramienta es que **es de Víctor, está en su GitHub, y es auditable**:
se puede leer, corregir y revertir.

## Cómo usarlo

1. **Al empezar** → leer `memory/index.md` + el archivo del proyecto relevante.
2. **Durante** → si una memoria dice algo sobre código (rutas, funciones, flags),
   **verificarlo contra el código actual antes de afirmarlo**. Las memorias son
   fotos del pasado, no estado vivo.
3. **Al cerrar algo importante** → anotarlo en el archivo que toque y añadir una
   línea en `memory/log.md`. Si es una decisión con evidencia, guardar la evidencia
   (números, no impresiones).

## Reglas de escritura de memoria

- **Un hecho, un sitio.** Antes de crear algo nuevo, buscar si ya existe y actualizarlo.
- **Guardar el PORQUÉ, no solo el QUÉ.** Una decisión sin su motivo se revierte sola
  en la siguiente sesión.
- **Guardar también los errores y lo que NO funcionó**, con su evidencia. Una memoria
  que solo recoge aciertos hace repetir los fallos.
- **Fechas absolutas** ("8 jul 2026"), nunca "ayer" o "la semana pasada".
- **No inventar.** Si algo no se sabe, se escribe que no se sabe. Un hueco honesto
  es útil; un dato inventado envenena todas las sesiones siguientes.
- Enlaces entre notas con `[[nombre-de-archivo]]`.

## Estructura

```
memory/
├── index.md        ← mapa: qué hay y cómo se conecta (empezar aquí)
├── victor.md       ← quién es, cómo trabaja, qué espera de mí
├── projects.md     ← estado de cada proyecto
├── skills.md       ← patrones y lecciones reutilizables entre proyectos
├── connectors.md   ← APIs, servicios y credenciales (SIN secretos)
└── log.md          ← bitácora de sesiones y decisiones
```

## Seguridad

**Nunca escribir secretos aquí** (claves API, tokens, contraseñas). Este repo puede
volverse público. En `connectors.md` se anota *qué* servicio se usa y *dónde* vive
su clave (p. ej. "`.env` del proyecto"), nunca el valor.
