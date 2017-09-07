from ECGdata import ECGData
from ProcessedECG import ProcessedECG
import pickle

patient = "ORBITA21386"

ecg_data = ECGData(patient)
processed_ecg = ProcessedECG(ecg_data)
qrsd,st = processed_ecg.calculate()

print("QRSd: {}".format(qrsd))
print("ST: {}".format(st))