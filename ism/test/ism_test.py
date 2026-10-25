import os
import numpy as np
import xarray as xr

from auxiliary.constants import constants

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




# ============================================================
# ANALYTICAL vs READ VALUES AT PIXEL [50,75] - ISM
# ============================================================

import os
import h5py
import numpy as np

# ------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------

OUTPUT_DIR = (
    r"C:\Users\aleja\OneDrive\Escritorio\EODP"
    r"\EODP_TER_2021\EODP_TER_2021"
    r"\EODP-TS-ISM\myoutput"
)

PIXEL = (50, 75)

# ISM configuration parameters
PIX_SIZE = 30e-6
T_INT = 0.00672
D = 0.150
F = 0.5262
TR = 0.99

WAVELENGTHS = np.array([0.490, 0.665, 0.865, 0.945]) * 1e-6

QE = 0.8
FWC = 420000
OCF = 5.4e-6
ADC_GAIN = 0.56
BIT_DEPTH = 12
V_MIN = 0.0
V_MAX = 0.86

H_PLANCK = 6.62607004e-34
C_LIGHT = 299792458

PIXEL_AREA = PIX_SIZE**2
ADC_MAX = 2**BIT_DEPTH - 1


# ------------------------------------------------------------
# READ NETCDF / HDF5 DATA
# ------------------------------------------------------------

def read_toa(filename, pixel=PIXEL):
    """Read the toa variable at the requested pixel."""
    path = os.path.join(OUTPUT_DIR, filename)

    if not os.path.isfile(path):
        raise FileNotFoundError(
            f"File not found: {path}"
        )

    with h5py.File(path, "r") as f:
        if "toa" not in f:
            raise KeyError(
                f"Variable 'toa' not found in {filename}. "
                f"Available variables: {list(f.keys())}"
            )

        data = np.asarray(f["toa"])

    if data.ndim < 2:
        raise ValueError(
            f"Expected a 2D or higher-dimensional 'toa' array "
            f"in {filename}; got shape {data.shape}."
        )

    return float(data[pixel])


# ------------------------------------------------------------
# ANALYTICAL CALCULATION
# ------------------------------------------------------------

def calculate_analytical_values(band, pixel=PIXEL):
    """
    Calculate the radiometric conversion from the stored optical
    irradiance, then reproduce the voltage-to-DN conversion from
    the stored detection-phase output.

    PRNU and dark signal are read from their saved intermediate
    products; they are not independently simulated here.
    """

    band = int(band)
    if band not in range(4):
        raise ValueError("band must be 0, 1, 2, or 3")

    # 1. Radiance after spectral integration (ISRF)
    radiance = read_toa(
        f"ism_toa_isrf_VNIR-{band}.nc", pixel
    )

    # 2. Irradiance after optical phase, including System MTF
    irradiance = read_toa(
        f"ism_toa_optical_VNIR-{band}.nc", pixel
    )

    # 3. Irradiance -> photons
    # Assumes irradiance is expressed in mW/m^2,
    # pixel area in m^2, time in seconds, and wavelength in metres.
    optical_energy = (
        irradiance * 1e-3 * PIXEL_AREA * T_INT
    )

    photon_energy = (
        H_PLANCK * C_LIGHT / WAVELENGTHS[band]
    )

    photons = optical_energy / photon_energy

    # 4. Photons -> electrons, limited by full-well capacity
    electrons_analytical = min(
        photons * QE,
        FWC
    )

    electrons_stored = read_toa(
        f"ism_toa_e_VNIR-{band}.nc", pixel
    )

    # 5. Read saved detection-stage intermediate products
    electrons_prnu = read_toa(
        f"ism_toa_prnu_VNIR-{band}.nc", pixel
    )

    electrons_dark = read_toa(
        f"ism_toa_ds_VNIR-{band}.nc", pixel
    )

    electrons_detection = read_toa(
        f"ism_toa_detection_VNIR-{band}.nc", pixel
    )

    # 6. Electrons -> voltage
    voltage = electrons_detection * OCF * ADC_GAIN

    # 7. Voltage -> DN
    # This assumes the ISM uses the same linear mapping,
    # clipping limits, and rounding convention.
    dn_analytical = np.rint(
        (voltage - V_MIN) / (V_MAX - V_MIN) * ADC_MAX
    )

    dn_analytical = int(
        np.clip(dn_analytical, 0, ADC_MAX)
    )

    dn_stored = read_toa(
        f"ism_toa_VNIR-{band}.nc", pixel
    )

    return {
        "Radiance": radiance,
        "Irradiance after MTF": irradiance,
        "Photons analytical": photons,
        "Electrons analytical": electrons_analytical,
        "Electrons stored": electrons_stored,
        "Electrons after PRNU": electrons_prnu,
        "Electrons after dark signal": electrons_dark,
        "Electrons after detection": electrons_detection,
        "Voltage analytical": voltage,
        "DN analytical": dn_analytical,
        "DN stored": dn_stored,
        "DN difference": dn_analytical - dn_stored,
    }


# ------------------------------------------------------------
# PRINT COMPARISON TABLE
# ------------------------------------------------------------

def print_comparison(band, pixel=PIXEL):
    """Print analytical and stored values for one VNIR band."""

    values = calculate_analytical_values(band, pixel)

    files = {
        "Radiance": f"ism_toa_isrf_VNIR-{band}.nc",
        "Irradiance after MTF": f"ism_toa_optical_VNIR-{band}.nc",
        "Electrons": f"ism_toa_e_VNIR-{band}.nc",
        "After PRNU": f"ism_toa_prnu_VNIR-{band}.nc",
        "After dark signal": f"ism_toa_ds_VNIR-{band}.nc",
        "Detection": f"ism_toa_detection_VNIR-{band}.nc",
        "DN": f"ism_toa_VNIR-{band}.nc",
    }

    analytical_keys = {
        "Radiance": "Radiance",
        "Irradiance after MTF": "Irradiance after MTF",
        "Electrons": "Electrons analytical",
        "DN": "DN analytical",
    }

    print("\n" + "=" * 94)
    print(f"VNIR-{band} | Pixel {pixel}")
    print("=" * 94)
    print(
        f"{'Stage':<27}"
        f"{'Analytical':>22}"
        f"{'Read value':>22}"
        f"{'Difference':>22}"
    )
    print("-" * 94)

    for stage, filename in files.items():
        read_value = read_toa(filename, pixel)

        if stage in analytical_keys:
            analytical_value = values[analytical_keys[stage]]
            difference = analytical_value - read_value

            print(
                f"{stage:<27}"
                f"{analytical_value:>22.6f}"
                f"{read_value:>22.6f}"
                f"{difference:>22.6f}"
            )
        else:
            # These stages depend on the implemented detector
            # effects and are shown as stored values only.
            print(
                f"{stage:<27}"
                f"{'N/A':>22}"
                f"{read_value:>22.6f}"
                f"{'N/A':>22}"
            )

    print("-" * 94)
    print(f"{'Voltage analytical':<27}{values['Voltage analytical']:>22.6f}")
    print(f"{'DN analytical':<27}{values['DN analytical']:>22}")
    print(f"{'DN stored':<27}{values['DN stored']:>22.6f}")
    print(f"{'DN difference':<27}{values['DN difference']:>22.6f}")


# ------------------------------------------------------------
# RUN ALL FOUR VNIR BANDS
# ------------------------------------------------------------

if __name__ == "__main__":
    cross_validate()
    for band in range(4):
        print_comparison(band)


