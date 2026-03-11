import pydicom

ds = pydicom.dcmread("test.dcm")
print("PixelData exists?" , "PixelData" in ds)
print("Shape:", getattr(ds, "pixel_array", "No pixel array"))