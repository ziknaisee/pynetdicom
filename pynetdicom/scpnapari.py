# scp_server_napari.py
import os
import logging
from datetime import datetime
import pydicom
import numpy as np
import napari

from pynetdicom import AE, evt
from pynetdicom.sop_class import (
    Verification,
    CTImageStorage,
    MRImageStorage,
    SecondaryCaptureImageStorage
)

# -----------------------------
# Setup logging
# -----------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('pynetdicom_scp')

# -----------------------------
# Folder to save received DICOMs
# -----------------------------
SAVE_FOLDER = 'received_dicom'
os.makedirs(SAVE_FOLDER, exist_ok=True)

# -----------------------------
# Napari viewer setup (single viewer for all files)
# -----------------------------
viewer = napari.Viewer(title="DICOM Viewer")
image_stack = []

# -----------------------------
# Function to add DICOM to Napari
# -----------------------------
def add_to_napari(ds):
    """Add DICOM pixel array to Napari viewer"""
    if "PixelData" not in ds:
        logger.warning("DICOM file has no image data")
        return
    
    img = ds.pixel_array
    if img.ndim == 3:  # multi-frame DICOM
        for i in range(img.shape[0]):
            image_stack.append(img[i])
    else:
        image_stack.append(img)

    # Update Napari layer
    viewer.layers.clear()
    viewer.add_image(np.array(image_stack), name="DICOM Stack", colormap='gray')

# -----------------------------
# Handlers
# -----------------------------
def handle_echo(event):
    """C-ECHO request handler"""
    requestor = event.assoc.requestor
    timestamp = event.timestamp.strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"C-ECHO from {requestor.address}:{requestor.port} at {timestamp}")
    return 0x0000

def handle_store(event):
    """C-STORE request handler"""
    ds = event.dataset
    ds.file_meta = event.file_meta

    filename = f"{ds.SOPInstanceUID}.dcm"
    filepath = os.path.join(SAVE_FOLDER, filename)

    ds.save_as(filepath, write_like_original=False)
    logger.info(f"Received and saved DICOM file: {filepath}")

    # Add to Napari viewer
    add_to_napari(ds)

    return 0x0000

# -----------------------------
# Create AE
# -----------------------------
ae = AE(ae_title='MY_XRAY_SCP')

ae.add_supported_context(Verification)
ae.add_supported_context(CTImageStorage)
ae.add_supported_context(MRImageStorage)
ae.add_supported_context(SecondaryCaptureImageStorage)

handlers = [
    (evt.EVT_C_ECHO, handle_echo),
    (evt.EVT_C_STORE, handle_store)
]

# -----------------------------
# Start SCP server (blocking)
# -----------------------------
import threading

def run_scp():
    print("DICOM SCP Server running on port 11112...")
    ae.start_server(("localhost", 11112), evt_handlers=handlers, block=True)

# Run SCP in a separate thread so Napari can also run
scp_thread = threading.Thread(target=run_scp, daemon=True)
scp_thread.start()

# Run Napari GUI
napari.run()