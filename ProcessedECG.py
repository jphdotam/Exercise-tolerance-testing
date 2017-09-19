from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
from LeadPlot import LeadPlot

class ProcessedECG(): #Receives an ECGData object which contains a self.patient, self.file_list, and self.leads_from_files which is a dict (filenames) of dicts (leads)

    J_POINT_OFFSET = 10 #ms from J point that ST segment should be measured
    PLOT_DERIVATIVE = False


    def __init__(self, ecg_data):
        self.ecg_data = ecg_data
        self.qrsd, self.st = {}, {}

    def plot(self):

        def calculate_qrsd():
            pass

        def calculate_st():
            self.st[file_name] = {}
            for lead, data, slider_st_height, slider_iso_height in zip(file_data.keys(), file_data.values(),
                                                                       st_segment_horizontal_markers.values(),
                                                                       isoelectric_horizontal_markers.values()):
                iso_height = slider_iso_height.value()
                st_height = slider_st_height.value()
                self.st[file_name][lead] = st_height - iso_height
            update_results()

        def update_results():
            label_results_left.setText(
                "   RESULTS   <br>QRSd\t%0.f<br>I\t%0.1f mm<br>II\t%0.1f mm<br>III\t%0.1f mm<br>aVR\t%0.1f mm<br>aVL\t%0.1f mm<br>aVF\t%0.1f mm" % (
                self.qrsd[file_name], self.st[file_name]['I'], self.st[file_name]['II'], self.st[file_name]['III'],
                self.st[file_name]['aVR'], self.st[file_name]['aVL'], self.st[file_name]['aVF']))
            label_results_right.setText(
                "   RESULTS   <br><br>V1\t%0.1f mm<br>V2\t%0.1f mm<br>V3\t%0.1f mm<br>V4\t%0.1f mm<br>V5\t%0.1f mm<br>V6\t%0.1f mm" % (
                self.st[file_name]['V1'], self.st[file_name]['V2'], self.st[file_name]['V3'], self.st[file_name]['V4'],
                self.st[file_name]['V5'], self.st[file_name]['V6']))

        for file_name,file_data in self.ecg_data.leads_by_file.items():
            print("Processing file {} ({} of {})".format(file_name,list(self.ecg_data.leads_by_file.keys()).index(file_name)+1,len(self.ecg_data.leads_by_file.items())))

            pg.setConfigOptions(antialias=True)
            pg.setConfigOption('background', 'w')
            pg.setConfigOption('foreground', 'k')
            app = QtGui.QApplication([])
            win = pg.GraphicsWindow(title="Processed ETT: {}".format(file_name))

            win.setWindowTitle("Processed ETT: {}".format(file_name))

            colcount,derivatives,lead_plots,qrs_regions,st_segment_horizontal_markers,st_segment_vertical_markers,isoelectric_horizontal_markers,isoelectric_vertical_markers = 0,{},{},{},{},{},{},{}

            for lead,lead_data in file_data.items():
                if colcount == 4:
                    win.nextRow()
                    colcount = 0

                lead_plots[lead] = LeadPlot(lead_name=lead, lead_data=lead_data)
                win.addItem(lead_plots[lead], row=None, col=None, rowspan=1, colspan=1)

                #isoelectric_horizontal_markers[lead] = lead_plots[lead].isoelectric_horizontal_marker
                #isoelectric_vertical_markers[lead] = lead_plots[lead].isoelectric_vertical_marker
                #st_segment_horizontal_markers[lead] = lead_plots[lead].st_segment_horizontal_marker
                #st_segment_vertical_markers[lead] = lead_plots[lead].st_segment_vertical_marker

                colcount += 1

            win.nextRow()

            label_results_left = pg.LabelItem(text="   RESULTS   <br>QRSd\t<br>I\t mm<br>II\t mm<br>III\t mm<br>aVL\t mm<br>aVR\t mm<br>aVF\ mm",justify='left')
            win.addItem(label_results_left)

            label_results_right = pg.LabelItem(text="   RESULTS   <br><br>V1\t mm<br>V2\t mm<br>V3\t mm<br>V4\t mm<br>V5\t mm<br>V6\ mm", justify='left')
            win.addItem(label_results_right)

            app.instance().exec_()
            del app
        return (self.qrsd,self.st)