import logging
from pydicom import dcmread

from pynetdicom import AE
from pynetdicom.sop_class import (
    Verification,
    CTImageStorage,
    MRImageStorage,
    SecondaryCaptureImageStorage
)

logging.basicConfig(level=logging.INFO)

ae = AE(ae_title="MY_XRAY_SCU")

ae.add_requested_context(Verification)
ae.add_requested_context(CTImageStorage)
ae.add_requested_context(MRImageStorage)
ae.add_requested_context(SecondaryCaptureImageStorage)

SCP_IP = "127.0.0.1"
SCP_PORT = 11112

assoc = ae.associate(SCP_IP, SCP_PORT)

if assoc.is_established:

    print("Connected to SCP")

    status = assoc.send_c_echo()
    print("C-ECHO:", hex(status.Status))

    ds = dcmread("test.dcm")

    print("Sending DICOM...")
    status = assoc.send_c_store(ds)

    print("C-STORE:", hex(status.Status))

    assoc.release()

else:
    print("Association failed")