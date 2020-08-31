# -*- coding: utf-8 -*-
""" runWRFpost
Esta funcion es la encargada de crear una clase ParametrizaciónWRF
que es la que configura y ejecuta una parametrización del modelo.
DEBE ser ejecutada dentro de un nodo por un script de slurm.

Attributes:
    codigo(str): define que parametrizacion se va a correr A, B, C, etc.

"""

import os
from optparse import OptionParser
from parametrizaciones import ParametrizacionWRF


def main():
    parser = OptionParser()
    parser.add_option("--param", dest="param")
    (opts, _) = parser.parse_args()
    codigo = opts.param

    # Se crea la clase para esta parametrización
    param_class = ParametrizacionWRF(codigo)

    # Ejecutar WRF
    if os.getenv('RUN_WRF') == '1':
        param_class.run_wrf()

    # Extraer variables útiles
    if os.getenv('EXTRAER_VARIABLES') == '1':
        param_class.extraer_variables()

    # Almacenar datos puntuales
    if os.getenv('DATOS_METEO') == '1':
        param_class.tabla_datos()

    # Generar gráficos
    if os.getenv('MAPAS') == '1':
        param_class.generar_graficos()


if __name__ == "__main__":
    main()
