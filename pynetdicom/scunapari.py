# scu_send_test.py
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
# Create Application Entity
# -----------------------------
ae = AE(ae_title='TEST_SCU')

# Add requested presentation contexts
ae.add_requested_context(Verification)
ae.add_requested_context(CTImageStorage)
ae.add_requested_context(MRImageStorage)
ae.add_requested_context(SecondaryCaptureImageStorage)

# -----------------------------
# SCP Connection
# -----------------------------
scp_ip = "127.0.0.1"
scp_port = 11112

assoc = ae.associate(scp_ip, scp_port, ae_title="MY_XRAY_SCP")

if assoc.is_established:
    logger.info("Connected to SCP")

    # Send C-ECHO first
    status = assoc.send_c_echo()
    if status:
        logger.info(f"C-ECHO Response: 0x{status.Status:04x}")

    # -----------------------------
    # Send DICOM file
    # -----------------------------
    dicom_file = "test.dcm"

    ds = dcmread(dicom_file)

    logger.info(f"Sending DICOM: {dicom_file}")
    logger.info(f"SOP Class UID: {ds.SOPClassUID}")

    status = assoc.send_c_store(ds)

    if status:
        logger.info(f"C-STORE Response: 0x{status.Status:04x}")
    else:
        logger.error("C-STORE failed")

    assoc.release()
    logger.info("Association released")

else:
    logger.error("Could not connect to SCP")