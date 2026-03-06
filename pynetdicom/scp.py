# scp_server_full.py
import os
import logging
from datetime import datetime
import pydicom
import matplotlib.pyplot as plt

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
# Create folder to save received images
# -----------------------------
SAVE_FOLDER = 'received_dicom'
os.makedirs(SAVE_FOLDER, exist_ok=True)

# -----------------------------
# Function to display DICOM
# -----------------------------
def show_dicom(filepath):
    """Open and display DICOM image"""
    try:
        ds = pydicom.dcmread(filepath)

        if "PixelData" in ds:
            plt.imshow(ds.pixel_array, cmap="gray")
            plt.title(f"DICOM Viewer\nPatient: {getattr(ds,'PatientName','Unknown')}")
            plt.axis("off")
            plt.show()
        else:
            print("No image data found in this DICOM file")

    except Exception as e:
        print("Error displaying DICOM:", e)


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

    # Automatically display the image
    show_dicom(filepath)

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
# Start SCP server
# -----------------------------
print("DICOM SCP Server running on port 11112...")
ae.start_server(("localhost", 11112), evt_handlers=handlers, block=True)
