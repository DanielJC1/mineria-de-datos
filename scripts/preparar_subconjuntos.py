"""
Proyecto Final - Minería de Datos (FI UNAM)
Caso: Prevención de diabetes | Fuente: ENSANUT 2018 (INEGI/INSP), "Nueva versión"

Este script extrae, de las tablas originales del INEGI, solo las columnas y
los registros necesarios para el proyecto, para que los archivos resultantes
sean ligeros y se puedan subir a GitHub y cargar en Google Colab.

Universo: adultos de 20 años o más con muestra de sangre venosa
(tabla CN_MUESAN_DETBIO_ADU). El resto de las tablas se filtra a esas
mismas personas usando la llave UPM + VIV_SEL + HOGAR + NUMREN.

Uso:
    python preparar_subconjuntos.py <carpeta_csv_CN> <carpeta_csv_CS> <carpeta_salida>
"""
import sys
from pathlib import Path

import pandas as pd

LLAVE = ["UPM", "VIV_SEL", "HOGAR", "NUMREN"]

TABLAS = {
    # archivo de salida: (componente, archivo original, columnas a conservar)
    "ensanut2018_laboratorio.csv": (
        "CN", "CN_MUESAN_DETBIO_ADU.csv",
        ["P5_1", "P7", "EDAD", "SEXO", "ENT", "DOMINIO", "REGION", "ESTRATO",
         "FACTOR_SV_D", "VALOR_GLU_SUERO", "VALOR_HB1AC", "VALOR_INSULINA",
         "VALOR_COLEST", "VALOR_COL_HDL", "VALOR_COL_LDL", "VALOR_TRIG"],
    ),
    "ensanut2018_antropometria.csv": (
        "CN", "CN_ANTROPOMETRIA.csv",
        ["PESO1_1", "PESO1_2", "TALLA4_1", "TALLA4_2", "CIRCUNFERENCIA8_1",
         "CIRCUNFERENCIA8_2", "PESO12_1", "PESO12_2", "TALLA15_1", "TALLA15_2",
         "CINTURA21_1", "CINTURA21_2", "P6", "P27_1_1", "P27_1_2", "P27_2_1",
         "P27_2_2"],
    ),
    "ensanut2018_cuestionario_adultos.csv": (
        "CS", "CS_ADULTOS.csv",
        ["P3_1", "P4_1", "P6_4", "P6_6", "P7_1_1", "P7_1_2", "P7_1_3",
         "P13_1", "P13_2", "P13_11"],
    ),
    "ensanut2018_residentes.csv": (
        "CS", "CS_RESIDENTES.csv",
        ["NIVEL", "P3_10_OPC1", "P3_11"],
    ),
    "ensanut2018_actividad_fisica.csv": (
        "CS", "CS_ACT_FIS_ADO.csv",
        ["P1", "P2", "P4", "P5", "P7", "P8", "P10"],
    ),
}


def main(dir_cn: Path, dir_cs: Path, salida: Path) -> None:
    salida.mkdir(parents=True, exist_ok=True)
    carpetas = {"CN": dir_cn, "CS": dir_cs}

    # Universo: personas con determinaciones bioquímicas
    lab = pd.read_csv(dir_cn / "CN_MUESAN_DETBIO_ADU.csv", dtype=str)
    universo = lab[LLAVE].drop_duplicates()
    print(f"Universo (adultos con muestra de sangre): {len(universo):,}")

    for archivo_salida, (comp, archivo, columnas) in TABLAS.items():
        df = pd.read_csv(carpetas[comp] / archivo, dtype=str,
                         usecols=LLAVE + columnas)
        df = universo.merge(df, on=LLAVE, how="inner")
        df.to_csv(salida / archivo_salida, index=False)
        tam = (salida / archivo_salida).stat().st_size / 1e6
        print(f"{archivo_salida:40s} {len(df):>7,} filas  {tam:5.1f} MB")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]))
