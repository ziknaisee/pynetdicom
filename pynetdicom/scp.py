import os
import logging
import threading
import queue
import pydicom
import matplotlib.pyplot as plt

from pynetdicom import AE, evt, AllStoragePresentationContexts
from pynetdicom.sop_class import Verification

# -----------------------------
# Logging
# -----------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pynetdicom_scp")

SAVE_FOLDER = "received_dicom"
os.makedirs(SAVE_FOLDER, exist_ok=True)

# Queue to pass images to viewer
display_queue = queue.Queue()

# -----------------------------
# C-ECHO
# -----------------------------
def handle_echo(event):
    requestor = event.assoc.requestor
    logger.info(f"C-ECHO from {requestor.address}:{requestor.port}")
    return 0x0000


# -----------------------------
# C-STORE
# -----------------------------
def handle_store(event):

    ds = event.dataset
    ds.file_meta = event.file_meta

    filename = f"{ds.SOPInstanceUID}.dcm"
    filepath = os.path.join(SAVE_FOLDER, filename)

    ds.save_as(filepath, enforce_file_format=True)

    logger.info(f"DICOM saved: {filepath}")

    # Send to viewer
    display_queue.put(filepath)

    return 0x0000


handlers = [
    (evt.EVT_C_ECHO, handle_echo),
    (evt.EVT_C_STORE, handle_store)
]

# -----------------------------
# Start SCP in background thread
# -----------------------------
def start_scp():

    ae = AE(ae_title="MY_XRAY_SCP")

    ae.add_supported_context(Verification)

    for context in AllStoragePresentationContexts:
        ae.add_supported_context(context.abstract_syntax)

    print("DICOM SCP Server running on port 11112...")

    ae.start_server(("0.0.0.0", 11112), evt_handlers=handlers)


scp_thread = threading.Thread(target=start_scp, daemon=True)
scp_thread.start()

# -----------------------------
# Main thread viewer loop
# -----------------------------
plt.ion()

while True:

    filepath = display_queue.get()

    try:
        ds = pydicom.dcmread(filepath)

        if "PixelData" in ds:

            plt.figure("DICOM Viewer")

            plt.imshow(ds.pixel_array, cmap="gray")

            patient = getattr(ds, "PatientName", "Unknown")

            plt.title(f"Patient: {patient}")

            plt.axis("off")

            plt.show()
            plt.pause(0.001)

    except Exception as e:
        print("Viewer error:", e)