import os
import numpy as np
import xarray as xr

# PATHS

BASE = r"C:\Users\aleja\OneDrive\Escritorio\EODP"

TER = os.path.join(
    BASE,
    r"EODP_TER_2021\EODP_TER_2021\EODP-TS-ISM"
)

# My generated ISM outputs
output = os.path.join(
    TER,
    "myoutput"
)

# Professor reference outputs
output_profe = os.path.join(
    TER,
    "output"
)

# NUMERICAL TOLERANCE

RTOL = 1e-5
ATOL = 1e-8


# NETCDF COMPARISON


def comparar_archivos(ruta, ruta_profe):
    """
    Compare two NetCDF files.

    Checks:
    - Dimensions
    - Variables
    - Dimensions of each variable
    - Shape of each variable
    - Numerical values
    - Non-numerical values
    """

    nombre = os.path.basename(ruta)

    print("\n" + "=" * 80)
    print(f"COMPARANDO: {nombre}")
    print("=" * 80)

    correcto = True

    try:
        with (
            xr.open_dataset(ruta) as ds,
            xr.open_dataset(ruta_profe) as ds_profe
        ):

            # -----------------------------------------------------------------
            # Dimensions
            # -----------------------------------------------------------------

            if dict(ds.sizes) != dict(ds_profe.sizes):
                correcto = False

                print("ERROR: DIMENSIONES INCORRECTAS")
                print("  Tú:    ", dict(ds.sizes))
                print("  Profe: ", dict(ds_profe.sizes))
            else:
                print("DIMENSIONES CORRECTAS")

            # -----------------------------------------------------------------
            # Variables
            # -----------------------------------------------------------------

            vars_mias = set(ds.variables)
            vars_profe = set(ds_profe.variables)

            if vars_mias != vars_profe:
                correcto = False

                print("ERROR: VARIABLES DIFERENTES")
                print("  Solo tuyas: ", sorted(vars_mias - vars_profe))
                print("  Solo profe: ", sorted(vars_profe - vars_mias))
            else:
                print("VARIABLES CORRECTAS")

            # -----------------------------------------------------------------
            # Compare common variables
            # -----------------------------------------------------------------

            for var in sorted(vars_mias & vars_profe):

                a = ds[var].values
                b = ds_profe[var].values

                # Dimensions of variable
                if ds[var].dims != ds_profe[var].dims:
                    correcto = False

                    print(
                        f"ERROR: dimensiones de '{var}' diferentes"
                    )
                    print("  Tú:    ", ds[var].dims)
                    print("  Profe: ", ds_profe[var].dims)

                    continue

                # Shape
                if a.shape != b.shape:
                    correcto = False

                    print(
                        f"ERROR: shape de '{var}' diferente"
                    )
                    print("  Tú:    ", a.shape)
                    print("  Profe: ", b.shape)

                    continue

                # Numerical variables
                if (
                    np.issubdtype(a.dtype, np.number)
                    and np.issubdtype(b.dtype, np.number)
                ):

                    mask = ~np.isclose(
                        a,
                        b,
                        rtol=RTOL,
                        atol=ATOL,
                        equal_nan=True
                    )

                    ndiff = np.count_nonzero(mask)
                    n = mask.size

                    if ndiff == 0:
                        print(f"OK: {var}")

                    else:
                        correcto = False

                        diff = np.abs(
                            a.astype(float) - b.astype(float)
                        )

                        print(
                            f"ERROR: valores diferentes en '{var}'"
                        )
                        print(f"  Diferencias: {ndiff}/{n}")
                        print(
                            f"  Porcentaje: {100 * ndiff / n:.6f}%"
                        )
                        print(
                            f"  Error máximo: {np.nanmax(diff)}"
                        )
                        print(
                            f"  Error medio: {np.nanmean(diff)}"
                        )

                # Non-numerical variables
                else:

                    if np.array_equal(a, b):
                        print(f"OK: {var}")
                    else:
                        correcto = False
                        print(
                            f"ERROR: '{var}' diferente"
                        )

    except Exception as exc:

        correcto = False

        print(
            f"ERROR leyendo/comparando: {exc}"
        )

    # Result

    if correcto:
        print(
            f"RESULTADO: {nombre} -> COINCIDE"
        )
    else:
        print(
            f"RESULTADO: {nombre} -> TIENE DIFERENCIAS"
        )

    return correcto


# FIND NETCDF OUTPUTS

def obtener_archivos_nc(carpeta):
    """
    Return all NetCDF files directly inside the output folder.
    """

    if not os.path.isdir(carpeta):
        raise FileNotFoundError(
            f"No existe la carpeta:\n{carpeta}"
        )

    return sorted(
        f
        for f in os.listdir(carpeta)
        if f.lower().endswith(".nc")
    )


# CROSS-VALIDATION

def cross_validate():

    print("=" * 80)
    print("CROSS-VALIDATION DE LOS OUTPUTS ISM")
    print("=" * 80)

    print(
        "Carpeta outputs ISM:",
        output
    )

    print(
        "Carpeta profesora:",
        output_profe
    )

    # Check folders

    if not os.path.isdir(output):
        raise FileNotFoundError(
            f"No existe tu carpeta de outputs:\n{output}"
        )

    if not os.path.isdir(output_profe):
        raise FileNotFoundError(
            f"No existe la carpeta de referencia:\n{output_profe}"
        )

    # Get NetCDF files

    archivos_mios = set(
        obtener_archivos_nc(output)
    )

    archivos_profe = set(
        obtener_archivos_nc(output_profe)
    )

    archivos_comunes = sorted(
        archivos_mios & archivos_profe
    )

    solo_mios = sorted(
        archivos_mios - archivos_profe
    )

    solo_profe = sorted(
        archivos_profe - archivos_mios
    )

    print("\nArchivos NetCDF encontrados:")
    print("  Tú:          ", len(archivos_mios))
    print("  Profe:       ", len(archivos_profe))
    print("  En común:    ", len(archivos_comunes))

    # Files not compared

    if solo_mios:
        print(
            "\nARCHIVOS SOLO EN TU OUTPUT "
            "(NO SE COMPARAN):"
        )

        for nombre in solo_mios:
            print("  -", nombre)

    if solo_profe:
        print(
            "\nARCHIVOS SOLO EN EL OUTPUT DEL PROFESOR "
            "(NO SE COMPARAN):"
        )

        for nombre in solo_profe:
            print("  -", nombre)

    if not solo_mios and not solo_profe:
        print(
            "\nARCHIVOS: mismos NetCDF en ambas carpetas"
        )

    print(
        "\nIMPORTANTE: solo se comparan archivos presentes "
        "en AMBAS carpetas."
    )

    # Compare ONLY common files

    resultados = {}

    for nombre in archivos_comunes:

        ruta = os.path.join(
            output,
            nombre
        )

        profe = os.path.join(
            output_profe,
            nombre
        )

        resultados[nombre] = comparar_archivos(
            ruta,
            profe
        )

    # Resumen final

    print("\n" + "=" * 80)
    print("RESUMEN FINAL")
    print("=" * 80)

    for nombre, ok in resultados.items():

        print(
            f"{nombre}: "
            f"{'COINCIDE' if ok else 'TIENE DIFERENCIAS'}"
        )

    print("\n" + "=" * 80)

    if resultados and all(resultados.values()):

        print(
            "RESULTADO GLOBAL: "
            "TODOS LOS OUTPUTS COINCIDEN CON LA REFERENCIA"
        )

    elif not resultados:

        print(
            "RESULTADO GLOBAL: "
            "NO HAY ARCHIVOS PARA COMPARAR"
        )

    else:

        n_ok = sum(resultados.values())
        n_total = len(resultados)

        print(
            "RESULTADO: "
            f"{n_ok}/{n_total} OUTPUTS COINCIDEN"
        )

    print("=" * 80)

    return bool(resultados) and all(
        resultados.values()
    )


# MAIN

if __name__ == "__main__":

    cross_validate()
