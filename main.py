from ECGdata import ECGData
from ProcessedECG import ProcessedECG

patient = "ORBITA21386"

ecg_data = ECGData(patient)
processed_ecg = ProcessedECG(ecg_data)
qrsd,st = processed_ecg.plot()

print("QRSd: {}".format(qrsd))
print("ST: {}".format(st))