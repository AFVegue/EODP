# L1B TESTS
#
# 1) CROSS-VALIDATE THE 8 L1B OUTPUTS AGAINST THE PROFESSOR REFERENCE.
# 2) PLOT EQUALISED VS NON-EQUALISED VS TRUTH FOR VNIR-0.
#
# The reference output folder is: EODP-TS-L1B/output
#
# The truth is: EODP-TS-L1B/input/ism_toa_isrf_VNIR-0.nc

import os
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt

# PATHS
BASE = (r"C:\Users\aleja\OneDrive\Escritorio\EODP")
TER = os.path.join( BASE, r"EODP_TER_2021\EODP_TER_2021\EODP-TS-L1B" )

# mis outputs
output = os.path.join(TER, "output_l1b")
output_noteq = os.path.join(TER, "output_l1b_noteq")
# reference outputs
output_profe = os.path.join(TER, "output")
# Truth
input_truth = os.path.join(TER, "input")
# Numerical tolerance.
RTOL = 1e-5
ATOL = 1e-8



# NETCDF COMPARISON

def comparar_archivos(ruta, ruta_profe):
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

            # Dimensions
            if dict(ds.sizes) != dict(ds_profe.sizes):
                correcto = False
                print("ERROR: DIMENSIONES INCORRECTAS")
                print("  Tú:    ", dict(ds.sizes))
                print("  Profe: ", dict(ds_profe.sizes))
            else:
                print("DIMENSIONES CORRECTAS")

            # Variables
            vars = set(ds.variables)
            vars_profe = set(ds_profe.variables)

            if vars != vars_profe:
                correcto = False
                print("ERROR: VARIABLES DIFERENTES")
                print("  Solo tuyas:  ", sorted(vars - vars_profe))
                print("  Solo profe:  ", sorted(vars_profe - vars))
            else:
                print("VARIABLES CORRECTAS")

            # Compare common variables
            for var in sorted(vars & vars_profe):

                a = ds[var].values
                b = ds_profe[var].values

                if ds[var].dims != ds_profe[var].dims:
                    correcto = False
                    print(f"ERROR: dimensiones de '{var}' diferentes")
                    continue

                if a.shape != b.shape:
                    correcto = False
                    print(f"ERROR: shape de '{var}' diferente")
                    continue

                if np.issubdtype(a.dtype, np.number) and \
                   np.issubdtype(b.dtype, np.number):

                    mask = ~np.isclose(
                        a, b,
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

                        print(f"ERROR: valores diferentes en '{var}'")
                        print(f"  Diferencias: {ndiff}/{n}")
                        print(f"  Porcentaje: {100*ndiff/n:.6f}%" )
                        print( f"  Error máximo: {np.nanmax(diff)}")
                        print(f"  Error medio: {np.nanmean(diff)}")

                else:
                    if np.array_equal(a, b):
                        print(f"OK: {var}")
                    else:
                        correcto = False
                        print(f"ERROR: '{var}' diferente")

    except Exception as exc:
        correcto = False
        print(f"ERROR leyendo/comparando: {exc}")

    if correcto:
        print(f"RESULTADO: {nombre} -> COINCIDE")
    else:
        print(f"RESULTADO: {nombre} -> TIENE DIFERENCIAS")

    return correcto



# CROSS-VALIDATION

def cross_validate():

    print("=" * 80)
    print("CROSS-VALIDATION DE LOS OUTPUTS L1B")
    print("=" * 80)

    print("Carpeta outputs equalized:", output)
    print("Carpeta outputs no equalized:", output_noteq)
    print("Carpeta profesora:", output_profe)

    resultados = {}

    # Four equalized products
    for band in range(4):

        nombre_eq = f"l1b_toa_eq_VNIR-{band}.nc"
        ruta_eq = os.path.join(output, nombre_eq)
        profe_eq = os.path.join(output_profe, nombre_eq)

        if os.path.isfile(ruta_eq) and os.path.isfile(profe_eq):
            resultados[nombre_eq] = comparar_archivos(ruta_eq,profe_eq)
        else:
            resultados[nombre_eq] = False
            print(f"\nFALTA: {nombre_eq}")

        # Four final L1B radiance products
        nombre = f"l1b_toa_VNIR-{band}.nc"
        ruta = os.path.join(output, nombre)
        profe = os.path.join(output_profe, nombre)

        if os.path.isfile(ruta) and os.path.isfile(profe):
            resultados[nombre] = comparar_archivos(ruta, profe)
        else:
            resultados[nombre] = False
            print(f"\nFALTA: {nombre}")

    print("\n" + "=" * 80)
    print("RESUMEN FINAL")
    print("=" * 80)

    for nombre, ok in resultados.items():
        print(f"{nombre}: {'COINCIDE' if ok else 'TIENE DIFERENCIAS'}")


    return all(resultados.values())


# PLOT

def leer_perfil(ruta, nalt=50):

    with xr.open_dataset(ruta) as ds:

        if "toa" not in ds:
            raise ValueError(f"No existe la variable 'toa' en {ruta}")

        toa = np.asarray(ds["toa"].values)

        if toa.shape != (100, 150):
            raise ValueError(f"Shape inesperado en {ruta}: {toa.shape}")

        return toa[nalt, :]


def plot_figure():

    band = "VNIR-0"
    nalt = 50
    
    ruta_eq = os.path.join(output,f"l1b_toa_{band}.nc")
    ruta_no_eq = os.path.join(output_noteq,f"l1b_toa_{band}.nc")
    ruta_truth = os.path.join(input_truth,f"ism_toa_isrf_{band}.nc")

    for ruta in (ruta_eq, ruta_no_eq, ruta_truth):
        if not os.path.isfile(ruta):
            raise FileNotFoundError(ruta)

    toa_eq = leer_perfil(ruta_eq, nalt)
    toa_no_eq = leer_perfil(ruta_no_eq, nalt)
    toa_truth = leer_perfil(ruta_truth, nalt)

    act = np.arange(toa_truth.size)

    plt.figure(figsize=(12, 6))

    # Do not change the data: all three profiles come directly
    # from the corresponding NetCDF products.
    plt.plot(act,toa_eq,linewidth=1.5,label="TOA L1B with eq")
    plt.plot(act,toa_no_eq,linewidth=1.2,label="TOA L1B no eq")
    plt.plot(act,toa_truth,linewidth=1.5,label="TOA after the ISRF")

    plt.title("Effect of the Equalization for VNIR-0")
    plt.xlabel("ACT pixel [-]")
    plt.ylabel(r"TOA [mW/m$^2$/sr]")
    plt.grid(True, alpha=0.5)
    plt.legend()
    plt.tight_layout()

    output_png = os.path.join(output,"Effect of the Equalization for VNIR-0.png")
    plt.savefig(output_png,dpi=300,bbox_inches="tight")

    plt.show()
    plt.close()

    print("\nGráfica guardada en:")
    print(output_png)



# MAIN

if __name__ == "__main__":
    cross_validate()
    plot_figure()
