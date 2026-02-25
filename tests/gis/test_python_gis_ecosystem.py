import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import rasterio
import numpy as np
import os

def test_vector_operations():
    print("Testing vector operations...")
    # 1. Load Well Locations from CSV
    data = {
        "well_name": ["Well-A", "Well-B"],
        "latitude": [57.0, 58.0],
        "longitude": [-1.5, 0.5]
    }
    df = pd.DataFrame(data)
    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df["longitude"], df["latitude"]),
        crs="EPSG:4326"
    )
    assert len(gdf) == 2
    assert gdf.crs.to_epsg() == 4326
    print("Vector load: OK")

    # 2. CRS Transform
    gdf_utm = gdf.to_crs("EPSG:32631")
    assert gdf_utm.crs.to_epsg() == 32631
    print("CRS transform: OK")

    # 3. Buffer
    gdf_utm["geometry_buffer"] = gdf_utm.geometry.buffer(500)
    assert gdf_utm["geometry_buffer"].iloc[0].area > 0
    print("Buffer operation: OK")

def test_raster_operations():
    print("\nTesting raster operations...")
    # 1. Create a dummy GeoTIFF
    width, height = 10, 10
    arr = np.random.rand(height, width).astype('float32')
    from rasterio.transform import from_bounds
    transform = from_bounds(-2.0, 56.0, 1.0, 59.0, width, height)
    
    with rasterio.open(
        'test_bathy.tif', 'w',
        driver='GTiff', height=height, width=width,
        count=1, dtype='float32',
        crs='EPSG:4326', transform=transform
    ) as dst:
        dst.write(arr, 1)
    
    # 2. Read and Sample
    with rasterio.open('test_bathy.tif') as src:
        assert src.crs.to_epsg() == 4326
        # Sample at center
        coord = ((-0.5, 57.5),)
        sampled = list(src.sample(coord))
        assert len(sampled) == 1
    
    print("Raster write/read/sample: OK")
    os.remove('test_bathy.tif')

if __name__ == "__main__":
    try:
        test_vector_operations()
        test_raster_operations()
        print("\nAll Python GIS Ecosystem tests passed!")
    except Exception as e:
        print(f"\nTest failed: {e}")
        exit(1)
