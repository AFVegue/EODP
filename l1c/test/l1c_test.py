

# =============================================================================
# LEVEL-1C TEST
#
# Tests:
#   1. Plot projection on ground:
#        - L1B footprint in black
#        - L1C MGRS grid in red
#   2. Plot spatial sampling distance [HAVERSINE]
#      for the central row of the L1B geometry
#
# =============================================================================

import os

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt

from common.io.readGeodetic import readGeodetic


# =============================================================================
# PATHS
# =============================================================================

BASE = r"C:\Users\aleja\OneDrive\Escritorio\EODP"

TER = os.path.join(
    BASE,
    r"EODP_TER_2021\EODP_TER_2021\EODP-TS-L1C"
)

# L1B geolocation
GEODIR = os.path.join(
    TER,
    r"input\gm_alt100_act_150"
)

GEODATA = "geolocation.nc"

# Our L1C output
OUTPUT = os.path.join(
    TER,
    "myout"
)


# =============================================================================
# READ L1B GEOLOCATION
# =============================================================================

def read_l1b_geolocation():
    """
    Read L1B latitude and longitude using the same function
    used by the L1C processing module.
    """

    lat, lon = readGeodetic(
        GEODIR,
        GEODATA
    )

    lat = np.asarray(lat)
    lon = np.asarray(lon)

    print("L1B geolocation:")
    print("  lat shape:", lat.shape)
    print("  lon shape:", lon.shape)

    return lat, lon


# =============================================================================
# READ L1C PRODUCT
# =============================================================================

def read_l1c(band):
    """
    Read L1C latitude and longitude from the generated NetCDF.
    """

    filename = f"l1c_toa_{band}.nc"

    filepath = os.path.join(
        OUTPUT,
        filename
    )

    if not os.path.isfile(filepath):
        raise FileNotFoundError(
            f"No se encuentra el archivo:\n{filepath}"
        )

    with xr.open_dataset(filepath) as ds:

        if "lat" not in ds:
            raise ValueError(
                f"No existe la variable 'lat' en {filepath}"
            )

        if "lon" not in ds:
            raise ValueError(
                f"No existe la variable 'lon' en {filepath}"
            )

        lat_l1c = np.asarray(
            ds["lat"].values
        )

        lon_l1c = np.asarray(
            ds["lon"].values
        )

    print(f"\nL1C {band}:")
    print("  lat shape:", lat_l1c.shape)
    print("  lon shape:", lon_l1c.shape)

    return lat_l1c, lon_l1c


# =============================================================================
# L1B FOOTPRINT
# =============================================================================

def get_l1b_footprint(lat, lon):
    """
    Extract the perimeter of the L1B geometry.

    The L1B geometry is a 2D matrix. The footprint is obtained
    from the four borders of the matrix.
    """

    # Top edge
    lat_top = lat[0, :]
    lon_top = lon[0, :]

    # Right edge
    lat_right = lat[1:, -1]
    lon_right = lon[1:, -1]

    # Bottom edge, reversed
    lat_bottom = lat[-1, -2::-1]
    lon_bottom = lon[-1, -2::-1]

    # Left edge, reversed
    lat_left = lat[-2:0:-1, 0]
    lon_left = lon[-2:0:-1, 0]

    lat_boundary = np.concatenate([
        lat_top,
        lat_right,
        lat_bottom,
        lat_left
    ])

    lon_boundary = np.concatenate([
        lon_top,
        lon_right,
        lon_bottom,
        lon_left
    ])

    # Close the polygon
    lat_boundary = np.append(
        lat_boundary,
        lat_boundary[0]
    )

    lon_boundary = np.append(
        lon_boundary,
        lon_boundary[0]
    )

    return lat_boundary, lon_boundary

# =============================================================================
# 1. PROJECTION ON GROUND
# =============================================================================

def plot_footprint(
    lat_l1b,
    lon_l1b,
    lat_l1c,
    lon_l1c,
    band
):
    """
    Plot the L1B and L1C grids on ground.

    L1B:
        Original L1B geolocation grid.

    L1C:
        MGRS grid obtained after reprojection.
    """

    plt.figure(figsize=(12, 8))

    # -------------------------------------------------------------------------
    # L1B grid
    # -------------------------------------------------------------------------

    plt.scatter(
        lon_l1b,
        lat_l1b,
        color="red",
        s=4,
        label="L1B"
    )

    # -------------------------------------------------------------------------
    # L1C MGRS grid
    # -------------------------------------------------------------------------

    plt.scatter(
        lon_l1c,
        lat_l1c,
        color="blue",
        s=8,
        label="L1C MGRS"
    )

    # -------------------------------------------------------------------------
    # Labels
    # -------------------------------------------------------------------------

    plt.title(
        "Projection on ground"
    )

    plt.xlabel(
        "Longitude [deg]"
    )

    plt.ylabel(
        "Latitude [deg]"
    )

    plt.grid(
        True,
        alpha=0.5
    )

    plt.legend()

    plt.tight_layout()

    # -------------------------------------------------------------------------
    # Save
    # -------------------------------------------------------------------------

    filename = f"footprint_{band}.png"

    filepath = os.path.join(
        OUTPUT,
        filename
    )

    plt.savefig(
        filepath,
        dpi=300,
        bbox_inches="tight"
    )

    plt.show()

    plt.close()

    print(
        f"\nFootprint {band} guardado en:"
    )

    print(filepath)


# =============================================================================
# HAVERSINE
# =============================================================================

def haversine(
    lat1,
    lon1,
    lat2,
    lon2
):
    """
    Calculate the great-circle distance between two points.

    Input coordinates:
        latitude  [degrees]
        longitude [degrees]

    Output:
        distance [m]
    """

    # Earth radius [m]
    R = 6371000.0

    # Convert degrees to radians
    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)

    lat2 = np.radians(lat2)
    lon2 = np.radians(lon2)

    # Differences
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Haversine formula
    a = (
        np.sin(dlat / 2.0) ** 2
        +
        np.cos(lat1)
        *
        np.cos(lat2)
        *
        np.sin(dlon / 2.0) ** 2
    )

    c = 2.0 * np.arcsin(
        np.sqrt(a)
    )

    return R * c


# =============================================================================
# 2. SPATIAL SAMPLING DISTANCE
# =============================================================================

def plot_spatial_sampling_distance(lat, lon):
    """
    Calculate and plot the spatial sampling distance using
    the central row of the L1B geometry.
    """

    # Central row
    central_row = lat.shape[0] // 2

    lat_row = lat[central_row, :]
    lon_row = lon[central_row, :]

    # Distance between consecutive pixels
    distances = haversine(
        lat_row[:-1],
        lon_row[:-1],
        lat_row[1:],
        lon_row[1:]
    )

    # Pixel index
    pixel = np.arange(
        len(distances)
    )

    # -------------------------------------------------------------------------
    # Plot
    # -------------------------------------------------------------------------

    plt.figure(figsize=(12, 6))

    plt.plot(
        pixel,
        distances,
        linewidth=1.5
    )

    plt.xlabel(
        "ACT pixel [-]"
    )

    plt.ylabel(
        "Spatial sampling distance [m]"
    )

    plt.title(
        f"Spatial Sampling Distance - "
        f"L1B central row (row={central_row})"
    )

    # Avoid scientific notation / offset notation
    plt.ticklabel_format(
        axis="y",
        style="plain",
        useOffset=False
    )

    plt.grid(
        True,
        alpha=0.5
    )

    plt.tight_layout()



    # -------------------------------------------------------------------------
    # Save
    # -------------------------------------------------------------------------

    filename = (
        "L1B_spatial_sampling_distance_central_row.png"
    )

    filepath = os.path.join(
        OUTPUT,
        filename
    )

    plt.savefig(
        filepath,
        dpi=300,
        bbox_inches="tight"
    )

    plt.show()

    plt.close()

    # -------------------------------------------------------------------------
    # Statistics
    # -------------------------------------------------------------------------

    print(
        "\nSpatial Sampling Distance:"
    )

    print(
        f"  Central row: {central_row}"
    )

    print(
        f"  Mean: {np.mean(distances):.3f} m"
    )

    print(
        f"  Min:  {np.min(distances):.3f} m"
    )

    print(
        f"  Max:  {np.max(distances):.3f} m"
    )

    print(
        f"\nSpatial Sampling Distance plot guardado en:"
    )

    print(filepath)


# =============================================================================
# 3. SPATIAL SAMPLING DISTANCE - CENTRAL COLUMN
# =============================================================================

def plot_spatial_sampling_distance_central_column(lat, lon):
    """
    Calculate and plot the spatial sampling distance using
    the central column of the L1B geometry.
    """

    # Central column
    central_column = lon.shape[1] // 2

    lat_column = lat[:, central_column]
    lon_column = lon[:, central_column]

    # Distance between consecutive pixels
    distances = haversine(
        lat_column[:-1],
        lon_column[:-1],
        lat_column[1:],
        lon_column[1:]
    )

    # Pixel index
    pixel = np.arange(
        len(distances)
    )

    # -------------------------------------------------------------------------
    # Plot
    # -------------------------------------------------------------------------

    plt.figure(figsize=(12, 6))

    plt.plot(
        pixel,
        distances,
        linewidth=1.5
    )

    plt.xlabel(
        "ALT pixel [-]"
    )

    plt.ylabel(
        "Spatial sampling distance [m]"
    )

    plt.title(
        f"Spatial Sampling Distance - "
        f"L1B central column (column={central_column})"
    )

    # Avoid scientific notation / offset notation
    plt.ticklabel_format(
        axis="y",
        style="plain",
        useOffset=False
    )

    plt.grid(
        True,
        alpha=0.5
    )

    plt.tight_layout()

    # -------------------------------------------------------------------------
    # Save
    # -------------------------------------------------------------------------

    filename = (
        "L1B_spatial_sampling_distance_central_column.png"
    )

    filepath = os.path.join(
        OUTPUT,
        filename
    )

    plt.savefig(
        filepath,
        dpi=300,
        bbox_inches="tight"
    )

    plt.show()

    plt.close()

    # -------------------------------------------------------------------------
    # Statistics
    # -------------------------------------------------------------------------

    print(
        "\nSpatial Sampling Distance - Central Column:"
    )

    print(
        f"  Central column: {central_column}"
    )

    print(
        f"  Mean: {np.mean(distances):.3f} m"
    )

    print(
        f"  Min:  {np.min(distances):.3f} m"
    )

    print(
        f"  Max:  {np.max(distances):.3f} m"
    )

    print(
        "\nSpatial Sampling Distance central column plot "
        "guardado en:"
    )

    print(filepath)

# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":

    print("=" * 80)
    print("L1C TEST")
    print("=" * 80)

    # -------------------------------------------------------------------------
    # Read L1B geometry
    # -------------------------------------------------------------------------

    lat_l1b, lon_l1b = read_l1b_geolocation()

    # -------------------------------------------------------------------------
    # Plot footprint for every band
    # -------------------------------------------------------------------------

    bands = [
        "VNIR-0",
        "VNIR-1",
        "VNIR-2",
        "VNIR-3"
    ]

    for band in bands:

        lat_l1c, lon_l1c = read_l1c(
            band
        )

        plot_footprint(
            lat_l1b,
            lon_l1b,
            lat_l1c,
            lon_l1c,
            band
        )

    # -------------------------------------------------------------------------
    # Spatial sampling distance
    # -------------------------------------------------------------------------

    plot_spatial_sampling_distance(
        lat_l1b,
        lon_l1b
    )

    plot_spatial_sampling_distance_central_column(
        lat_l1b,
        lon_l1b
    )

    print("\n" + "=" * 80)
    print("L1C TEST FINISHED")
    print("=" * 80)