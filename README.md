# Prevención de diabetes con ENSANUT 2018 – Proyecto Final de Minería de Datos

Proyecto Final de Minería de Datos (Facultad de Ingeniería, UNAM), desarrollado con la metodología CRISP-DM.
Caso de negocio: **prevención de diabetes**.

## Fuente de datos

Encuesta Nacional de Salud y Nutrición (ENSANUT) 2018, INEGI / INSP. Microdatos en CSV, sección **"Nueva versión"**:
https://www.inegi.org.mx/programas/ensanut/2018/

Las tablas originales pesan demasiado para GitHub (más de 400 MB descomprimidas). Por eso la carpeta `data/` solo contiene
**subconjuntos** con las columnas y los registros que usa el proyecto. Se generan con `scripts/preparar_subconjuntos.py`.

## Universo

Adultos de 20 años o más con muestra de sangre venosa y determinaciones bioquímicas (tabla `CN_MUESAN_DETBIO_ADU`):
**13,220 personas**. Las demás tablas se filtran a esas mismas personas.

Las tablas se unen con la llave **`UPM + VIV_SEL + HOGAR + NUMREN`**. Hay que leerlas como texto (`dtype=str`) para no perder los ceros a la izquierda.

## Archivos en `data/`

| Archivo | Tabla original | Contenido |
|---|---|---|
| `ensanut2018_laboratorio.csv` | CN_MUESAN_DETBIO_ADU | Edad, sexo, entidad, horas de ayuno, diagnóstico previo, glucosa, HbA1c, insulina, perfil de lípidos, factor de expansión |
| `ensanut2018_antropometria.csv` | CN_ANTROPOMETRIA | Peso, talla, cintura y presión arterial |
| `ensanut2018_cuestionario_adultos.csv` | CS_ADULTOS | Diagnósticos previos (diabetes, hipertensión, colesterol, triglicéridos), antecedentes familiares, tabaco y alcohol |
| `ensanut2018_residentes.csv` | CS_RESIDENTES | Escolaridad, derechohabiencia, lengua indígena |
| `ensanut2018_actividad_fisica.csv` | CS_ACT_FIS_ADO | Actividad física vigorosa, moderada, caminata y tiempo sentado (IPAQ corto) |

## Diccionario de las variables principales

| Variable | Descripción | Códigos |
|---|---|---|
| `P5_1` | Horas desde el último alimento | 00–24, 99 = no especificado |
| `P7` (laboratorio) | ¿Algún médico le ha dicho que tiene diabetes? | 1 Sí, 2 No, 3 Sí, durante el embarazo, 9 No sabe |
| `VALOR_GLU_SUERO` | Glucosa sérica (mg/dL) | |
| `VALOR_HB1AC` | Hemoglobina glicosilada (%) | |
| `FACTOR_SV_D` | Factor de expansión de la muestra de sangre | |
| `ENT` | Entidad federativa | 09 = CDMX, 15 = Estado de México |
| `DOMINIO` | Dominio | 1 Urbano, 2 Rural |
| `PESO1_*`, `TALLA4_*`, `CIRCUNFERENCIA8_*` | Peso (kg), talla (cm) y cintura (cm) de personas de **20 a 59 años** | 222.222 / 222.2 = no se midió |
| `PESO12_*`, `TALLA15_*`, `CINTURA21_*` | Peso, talla y cintura de personas de **60 años o más** | 222.222 / 222.2 = no se midió |
| `P6` (antropometría) | Embarazo / lactancia | 1 Embarazada, 2 Lactando, 3 Ambos, 4 Ninguno |
| `P27_1_1`, `P27_1_2` | Primera medición de presión arterial: sistólica y diastólica (mmHg) | 222 = no se midió |
| `P27_2_1`, `P27_2_2` | Segunda medición de presión arterial: sistólica y diastólica | |
| `P3_1` | ¿Algún médico le ha dicho que tiene diabetes? | 1 Sí, 2 Sí, durante el embarazo, 3 No |
| `P4_1` | ¿Algún médico le ha dicho que tiene la presión alta? | 1 Sí, 2 No |
| `P6_4` / `P6_6` | ¿Algún médico le ha dicho que tiene el colesterol / los triglicéridos altos? | 1 Sí, 2 No |
| `P7_1_1` / `P7_1_2` / `P7_1_3` | ¿Su padre / madre / hermano(a) tiene o tuvo diabetes? | 1 Sí, 2 No, 9 No sabe |
| `P13_1` | ¿Ha fumado al menos 100 cigarrillos en su vida? | 1 Sí, 2 No, 9 No sabe |
| `P13_2` | Actualmente fuma… | 1 Diario, 2 Algunos días, 3 No fuma, 8 No responde |
| `P13_11` | ¿Actualmente toma (alcohol)? | 1 Sí, 2 No, 3 Nunca ha tomado |
| `NIVEL` | Último nivel escolar aprobado | 00 Ninguno, 02 Primaria, 03 Secundaria, 04 Preparatoria, 10 Licenciatura, 11 Maestría, 12 Doctorado, etc. |
| `P3_10_OPC1` | Derechohabiencia (primera opción) | 01 IMSS, 02 ISSSTE, 07 Seguro Popular, 09 Seguro privado, 11 Sin afiliación, etc. |
| `P1`, `P4`, `P7` (actividad física) | Días de actividad vigorosa / moderada / caminata en la última semana | 55, 88, 99 = especiales |
| `P2`, `P5`, `P8` (actividad física) | Tiempo por día de esa actividad | HH:MM; 88:88 / 99:99 = sin dato |
| `P10` (actividad física) | Tiempo sentado al día | HH:MM |

Los diccionarios completos están en los descriptores oficiales del INEGI (`ensanut_2018_nueva_version_fd_cn.xlsx` y `_fd_cs.xlsx`).

## Cómo cargar los datos en Colab

```python
import pandas as pd

BASE = "https://raw.githubusercontent.com/<usuario>/<repositorio>/main/data/"
lab = pd.read_csv(BASE + "ensanut2018_laboratorio.csv", dtype=str)
```

## Cómo regenerar los subconjuntos

```bash
python scripts/preparar_subconjuntos.py <carpeta_csv_CN> <carpeta_csv_CS> data
```
