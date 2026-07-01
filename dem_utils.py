# dem_utils.py
"""Shared utilities for UAV-lidar DEM terrain analysis (EPSG:25832)."""
import numpy as np
import rasterio
from rasterio.crs import CRS

TARGET_CRS = CRS.from_epsg(25832)  # ETRS89 / UTM zone 32N


def read_dem(path, band=1):
    """Read a single-band DEM. Returns (array, profile, (res_x, res_y)).

    NoData cells are converted to np.nan.
    """
    with rasterio.open(path) as src:
        arr = src.read(band).astype("float64")
        profile = src.profile.copy()
        nodata = src.nodata
        res_x, res_y = src.res  # (pixel width, pixel height)

        if src.crs is None:
            print("WARNING: DEM has no CRS. Assuming EPSG:25832.")
        elif src.crs.to_epsg() != 25832:
            print(f"WARNING: DEM CRS is {src.crs}. Expected EPSG:25832.")

    if nodata is not None:
        arr[arr == nodata] = np.nan
    return arr, profile, (res_x, res_y)


def write_raster(path, array, profile, nodata=-9999.0, dtype="float32"):
    """Write a single-band raster using an input profile as a template."""
    out = array.astype(dtype)
    out = np.where(np.isnan(out), nodata, out)

    profile = profile.copy()
    profile.update(
        dtype=dtype,
        count=1,
        nodata=nodata,
        crs=TARGET_CRS,
        compress="lzw",
    )
    with rasterio.open(path, "w", **profile) as dst:
        dst.write(out, 1)
    print(f"Saved: {path}")
    