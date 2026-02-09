# Taller Introducción al Diseño Bioclimático — 2026-2

Repositorio del taller con videos de clase, libretas de Jupyter y proyectos de simulación.

## Estructura

```
libro/          Fuente del libro (Quarto)
docs/           Libro renderizado (GitHub Pages)
pyproject.toml  Entorno Python (uv)
```

## Uso

```bash
# Instalar dependencias
uv sync

# Previsualizar el libro
quarto preview libro/

# Renderizar el libro
quarto render libro/
```

## Agregar una clase nueva

1. Crear carpeta `libro/clases/NNN-nombre/`
2. Crear `index.qmd` con el video y notas
3. Agregar la línea en `libro/_quarto.yml` bajo `chapters:`
4. `quarto render libro/`
# idb-2026-2
