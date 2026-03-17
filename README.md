# AUTOMATA

Generador automático de sesiones (TrackArchive) para Cubase a partir de una carpeta de stems.

---

## Descripción

AUTOMATA crea sesiones de Cubase utilizando un **template existente** como base.

El sistema **no construye el proyecto desde cero**. En su lugar:

* usa un template de Cubase como estructura (tracks, routing, folders, etc.)
* analiza los stems del usuario
* crea referencias de audio válidas (Pool)
* genera AudioClips y AudioEvents correctamente enlazados

El resultado es una sesión lista para abrir en Cubase, organizada y preparada para mezcla.

---

## Filosofía del sistema

AUTOMATA separa dos conceptos fundamentales:

```
estructura → definida por el template
audio → definido por el usuario
```

Esto permite:

* mantener compatibilidad total con Cubase
* evitar corrupción del proyecto
* reutilizar templates profesionales sin modificarlos
* escalar el sistema sin romper sesiones

---

## Flujo de trabajo

```
carpeta de stems
↓
lectura de archivos
↓
clasificación por tipo (kick, snare, etc.)
↓
asignación a pistas existentes del template
↓
creación de AudioFiles (Pool)
↓
clonación de AudioEvent base
↓
reconexión de referencias (FNPath / IDs)
↓
inserción en pistas
↓
exportación TrackArchive
```

---

## Regla fundamental del sistema

```
AudioFile → AudioClip → AudioEvent → Track
```

Esto implica:

* cada stem genera un AudioFile nuevo
* cada AudioEvent referencia ese AudioFile
* las referencias se conectan por ID
* el template NO define audio, solo estructura

---

## Manejo del Pool de audio (CRÍTICO)

AUTOMATA **NO reutiliza AudioFiles del template**.

Por cada stem:

1. Se crea un nuevo `AudioFile` en el Pool
2. Se reutiliza el ID del AudioFile dentro del AudioEvent
3. Se actualizan todas las referencias internas (FNPath / FPath)
4. Se asegura consistencia total de IDs

Esto garantiza:

* cero archivos offline
* cero conflictos de referencia
* independencia del template

---

## FNPath y referencias internas

Las referencias de audio en Cubase dependen de `FNPath` y `FPath`.

Reglas del sistema:

* cada AudioEvent debe apuntar a un FNPath válido
* los FNPath deben apuntar a:

  ```
  Path = "Media"
  Name = nombre real del archivo
  ```

### Estrategia adoptada

* se reutilizan FNPath globales del template SI existen
* si no hay suficientes:

  * se deben generar nuevos FNPath dinámicamente
* todos los nodos que compartan ID deben ser actualizados

---

## Nombres de archivos

AUTOMATA **NO modifica los nombres originales de los stems**.

Ejemplo:

```
kick.wav
snare_top.wav
pad_ex.wav
```

Reglas:

* el nombre original se mantiene
* el nombre se usa en:

  * Pool (AudioFile.Name)
  * FNPath.Name
  * AudioClip.Name
  * AudioEvent.Description

---

## Clasificación de stems

El sistema clasifica los archivos por palabras clave:

```
kick → KICK
snare / clap → SNARE
hat → HIHAT
bass / 808 → BASS
pad → AMBIENT
piano → KEYS
```

La clasificación:

* NO modifica el archivo
* SOLO determina a qué pista se asigna

---

## Asignación de pistas

Reglas:

* cada stem se asigna a una pista existente del template
* la búsqueda es por coincidencia de palabras
* se usan sinónimos (ej: clap → snare)

### Casos posibles

#### 1. Pista encontrada

→ se inserta el evento

#### 2. Pista no encontrada

→ el stem se ignora (warning en consola)

---

## Manejo de múltiples stems por pista

Ejemplo:

```
kick.wav
kick_layer.wav
```

Resultado:

* ambos se insertan en la misma pista
* se crean múltiples AudioEvents
* NO se crean pistas nuevas
* NO se renombra la pista

---

## Uso del template

El template define:

* tracks
* folders
* grupos
* routing
* FX
* estructura general

AUTOMATA:

* NO modifica la estructura del template
* NO renombra pistas
* NO crea nuevas pistas
* SOLO inserta eventos de audio

---

## Limpieza del template

Antes de insertar nuevos eventos:

* se eliminan todos los `MAudioEvent` existentes

Esto evita:

* duplicación de eventos
* conflictos con audio antiguo
* referencias inconsistentes

---

## Construcción de eventos (detalle técnico)

Por cada stem:

1. Clonar un `MAudioEvent` del template
2. Regenerar:

   * ID del evento
   * AssetOID
   * IDs internos
3. Asignar FNPath correspondiente
4. Crear AudioFile en el Pool con el MISMO ID
5. Actualizar:

   * FNPath.Name
   * FNPath.Path
   * AudioClip.Name
   * Description
6. Insertar en la pista correspondiente

---

## Estructura de salida

```
output/

    session.xml

    Media/
        kick.wav
        snare.wav
        pad.wav
```

---

## Ejecución

### Modo simple

```bash
python3 main.py
```

Defaults:

* stems: `./stems`
* template: `templates/template_basic.xml`
* output: `./output/session.xml`

---

### Modo manual

```bash
python3 main.py \
  --stems /ruta/stems \
  --template /ruta/template.xml \
  --output /ruta/output
```

---

## Requisitos de nombres de stems

### Correcto

```
kick.wav
snare_top.wav
bass_808.wav
lead_vocal.wav
```

### Incorrecto

```
audio1.wav
final.wav
nuevo.wav
sckn.wav
```

Archivos no reconocidos → `OTHER`

---

## Troubleshooting

### Archivos offline

Causas:

* FNPath incorrecto
* ID no sincronizado
* AudioFile no registrado en Pool

---

### Stems no aparecen

* pista no existe en template
* clasificación incorrecta

---

### Error de FNPath insuficiente

* template no tiene suficientes referencias
* solución: generar FNPath dinámicamente

---

## Estado del proyecto

```
MVP funcional en fase de consolidación
```

Completado:

* generación de TrackArchive válido
* manejo de Pool
* inserción de eventos
* compatibilidad con templates

Pendiente:

* generación dinámica de FNPath
* mejora en clasificación
* validación automática de templates
* logs más robustos

---

## Conclusión

AUTOMATA convierte:

```
stems
↓
sesión Cubase organizada
```

de forma automática, consistente y escalable.

El sistema está diseñado para evolucionar hacia pipelines de producción complejos sin depender de intervención manual.
