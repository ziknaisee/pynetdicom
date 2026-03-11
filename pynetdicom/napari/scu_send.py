from pynetdicom import AE
from pynetdicom.sop_class import Verification
from pydicom import dcmread
from pydicom.uid import ImplicitVRLittleEndian, ExplicitVRLittleEndian, ExplicitVRBigEndian

SCP_IP = "127.0.0.1"
SCP_PORT = 11112
SCP_AE_TITLE = "ANY-SCP"

# Load DICOM
ds = dcmread("ctaxial.dcm")
sop_class = ds.SOPClassUID

ae = AE(ae_title="MY-SCU")
ae.add_requested_context(Verification)

# Use the transfer syntax of the file (most common 3)
ae.add_requested_context(sop_class, [
    ImplicitVRLittleEndian,
    ExplicitVRLittleEndian,
    ExplicitVRBigEndian
])

assoc = ae.associate(SCP_IP, SCP_PORT, ae_title=SCP_AE_TITLE)

if assoc.is_established:
    print("Connected to SCP")

    status = assoc.send_c_echo()
    print(f"C-ECHO {'succeeded' if status else 'failed'}")

    # C-STORE
    status = assoc.send_c_store(ds)
    print(f"C-STORE {'succeeded' if status else 'failed'}")

    assoc.release()
else:
    print("Association failed")