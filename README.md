# auto
automatico
# AUTOMATA

Generador de sesiones/TrackArchive para Cubase a partir de una carpeta de stems.

## Flujo

1. Lee stems desde una carpeta
2. Clasifica por palabras clave (DRUMS/BASS/VOCALS/MUSIC/FX)
3. Muestra vista previa del template
4. Adapta el template dinámicamente:
   - duplica pistas si hay múltiples stems por pista base
   - elimina pistas sobrantes sin audio
5. Vincula audio con rutas relativas en `Audio/`
6. Exporta `Session.trackarchive`

## Ejecutar

### Modo simple (defaults)

```bash
python3 main.py
```

Defaults:
- stems: `./stems`
- template: auto-resuelve `templates/cubase_basic.trackarchive` (o el primero disponible)
- output: `./output/MySong_Session`

### Modo explícito (recomendado para pruebas manuales)

```bash
python3 main.py \
  --stems /ruta/a/mis_stems \
  --template /ruta/a/mi_template.trackarchive \
  --song MiTema \
  --output /ruta/salida
```

Salida:
- `/ruta/salida/MiTema_Session/Session.trackarchive`
- `/ruta/salida/MiTema_Session/Audio/*`

## Troubleshooting rápido

- **Error de template no encontrado**: verifica que exista `templates/` con `.trackarchive` o pasa `--template`.
- **No se encontraron stems**: revisa ruta en `--stems` y extensiones soportadas (`.wav`, `.aif`, `.aiff`, `.flac`).

## Tests

```bash
python3 -m pytest -q
```