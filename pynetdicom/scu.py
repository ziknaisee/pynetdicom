# scu_client_full.py
import logging
from pydicom import dcmread
from pynetdicom import AE
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
logger = logging.getLogger('pynetdicom_scu')

# -----------------------------
# Create AE (SCU)
# -----------------------------
ae = AE(ae_title='MY_XRAY_SCU')

# Add requested contexts (what SCU wants to send)
ae.add_requested_context(Verification)                 # C-ECHO
ae.add_requested_context(CTImageStorage)               # C-STORE CT
ae.add_requested_context(MRImageStorage)               # C-STORE MR
ae.add_requested_context(SecondaryCaptureImageStorage) # C-STORE SC

# -----------------------------
# Associate with SCP
# -----------------------------
scp_address = 'localhost'
scp_port = 11112
assoc = ae.associate(scp_address, scp_port)

if assoc.is_established:
    logger.info("Association established with SCP")

    # 1️⃣ C-ECHO (ping)
    status = assoc.send_c_echo()
    if status:
        logger.info(f"C-ECHO Response: 0x{status.Status:04x}")

    # 2️⃣ C-STORE (send DICOM file)
    dicom_file = 'test.dcm'  # Replace with your test DICOM file
    ds = dcmread(dicom_file)
    print(f"SOP Class UID of file: {ds.SOPClassUID}")  # Show SOP class for debug

    status = assoc.send_c_store(ds)
    if status:
        logger.info(f"C-STORE Response: 0x{status.Status:04x}")

    # Release association
    assoc.release()
    logger.info("Association released")
else:
    logger.error("Failed to associate with SCP")