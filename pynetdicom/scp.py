# scp_server_full.py
import os
import logging
from datetime import datetime
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
# Handlers
# -----------------------------
def handle_echo(event):
    """C-ECHO request handler"""
    requestor = event.assoc.requestor
    timestamp = event.timestamp.strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"C-ECHO from {requestor.address}:{requestor.port} at {timestamp}")
    return 0x0000  # Success

def handle_store(event):
    """C-STORE request handler"""
    ds = event.dataset
    ds.file_meta = event.file_meta
    filename = f"{ds.SOPInstanceUID}.dcm"
    filepath = os.path.join(SAVE_FOLDER, filename)
    ds.save_as(filepath, write_like_original=False)
    logger.info(f"Received and saved DICOM file: {filepath}")
    return 0x0000  # Success

# -----------------------------
# Create AE (Application Entity)
# -----------------------------
ae = AE(ae_title='MY_XRAY_SCP')

# Add supported contexts (what this SCP can handle)
ae.add_supported_context(Verification)                 # C-ECHO
ae.add_supported_context(CTImageStorage)               # C-STORE CT
ae.add_supported_context(MRImageStorage)               # C-STORE MR
ae.add_supported_context(SecondaryCaptureImageStorage) # C-STORE SC

# Bind handlers
handlers = [
    (evt.EVT_C_ECHO, handle_echo),
    (evt.EVT_C_STORE, handle_store)
]

# -----------------------------
# Start SCP server (blocking)
# -----------------------------
ae.start_server(("localhost", 11112), evt_handlers=handlers, block=True)