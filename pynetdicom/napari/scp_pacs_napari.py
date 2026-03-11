import os
import queue
import threading
from pynetdicom import AE, evt
from pynetdicom.sop_class import Verification
from pynetdicom.presentation import AllStoragePresentationContexts
from pydicom import dcmread
import napari
from qtpy.QtCore import QTimer

# Folder to save incoming DICOM files
SAVE_DIR = "received"
os.makedirs(SAVE_DIR, exist_ok=True)

# Thread-safe queue for napari updates
image_queue = queue.Queue()

# Napari viewer in main thread
viewer = napari.Viewer(title="DICOM SCP Viewer")

# C-STORE handler
def handle_store(event):
    ds = event.dataset
    ds.file_meta = event.file_meta

    # Save file
    filename = os.path.join(SAVE_DIR, f"{ds.SOPInstanceUID}.dcm")
    ds.save_as(filename, write_like_original=False)
    print(f"Saved file: {filename}")

    # Put pixel array into queue for GUI thread
    try:
        image_queue.put((ds.SOPInstanceUID, ds.pixel_array))
    except Exception as e:
        print(f"Cannot enqueue image: {e}")

    return 0x0000  # Success

# SCP server function
def start_scp():
    ae = AE()
    for context in AllStoragePresentationContexts:
        ae.add_supported_context(context.abstract_syntax)
    ae.add_supported_context(Verification)

    handlers = [(evt.EVT_C_STORE, handle_store)]
    print("DICOM SCP running on port 11112")
    ae.start_server(('', 11112), evt_handlers=handlers)

# Run SCP in a background thread
threading.Thread(target=start_scp, daemon=True).start()

# Qt timer to poll the queue safely in main thread
def poll_queue():
    while not image_queue.empty():
        uid, pixels = image_queue.get()
        viewer.add_image(pixels, name=uid, colormap='gray')

timer = QTimer()
timer.timeout.connect(poll_queue)
timer.start(200)  # check every 200 ms

# Run napari in main thread
napari.run()