from pyqtgraph.Qt import QtGui, QtCore
import scipy.signal
import numpy as np
import pyqtgraph as pg

class ProcessedECG(): #Receives an ECGData object which contains a self.patient, self.file_list, and self.leads_from_files which is a dict (filenames) of dicts (leads)

    J_POINT_OFFSET = 10 #ms from J point that ST segment should be measured
    PLOT_DERIVATIVE = False
    N_DERIV = 1 # The order derivative used to accentuate the QRS etc.

    def __init__(self, ecg_data):
        self.ecg_data = ecg_data
        self.qrsd, self.st = {}, {}

    def calculate(self):

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

                lead_data['y'][:] = [y - np.interp(400, lead_data['x'], lead_data['y']) for y in lead_data['y']] #Set the voltage at 400ms to be 0mV
                lead_plots[lead] = win.addPlot(title=lead, x=lead_data['x'], y=lead_data['y'], pen='b')
                lead_plots[lead].showGrid(x=True,y=True)
                lead_plots[lead].getAxis('left').setPen((231, 84, 128))
                lead_plots[lead].getAxis('bottom').setPen(231, 84, 128)
                lead_plots[lead].getAxis('left').setStyle(showValues=False)
                lead_plots[lead].getAxis('bottom').setStyle(showValues=False)

                derivative = np.append(np.array([0]*ProcessedECG.N_DERIV),np.diff(lead_data['y'],n=ProcessedECG.N_DERIV))
                derivatives[lead] = derivative
                lead_plots[lead].setYRange(-10, 20, padding=0)

                if ProcessedECG.PLOT_DERIVATIVE: lead_plots[lead].plot(x=lead_data['x'], y=derivative,pen='r')

                qrs_regions[lead] = pg.LinearRegionItem(movable=False)
                lead_plots[lead].addItem(qrs_regions[lead], ignoreBounds=True)

                isoelectric_horizontal_markers[lead] = pg.InfiniteLine(pos=200, angle=0, movable=False, pen='g')
                isoelectric_vertical_markers[lead] = pg.InfiniteLine(angle=90, movable=False, pen='g')
                st_segment_horizontal_markers[lead] = pg.InfiniteLine(pos=200,angle=0, movable=False, pen='r')
                st_segment_vertical_markers[lead] = pg.InfiniteLine(angle=90, movable=False, pen='r')

                lead_plots[lead].addItem(isoelectric_vertical_markers[lead], ignoreBounds=True)
                lead_plots[lead].addItem(isoelectric_horizontal_markers[lead], ignoreBounds=True)
                lead_plots[lead].addItem(st_segment_horizontal_markers[lead], ignoreBounds=True)
                lead_plots[lead].addItem(st_segment_vertical_markers[lead], ignoreBounds=True)

                colcount += 1

            shortest_derivative_length = min([len(d) for d in derivatives.values()])
            shortest_derivative_index = [len(d) for d in derivatives.values()].index(shortest_derivative_length)
            shortest_derivative_x = list(file_data.values())[shortest_derivative_index]['x']
            derivatives['summed'] = [0] * shortest_derivative_length
            for lead,d in derivatives.items():
                derivatives['summed'] = derivatives['summed'] + d[:shortest_derivative_length]

            win.nextRow()

            plot_derivative = win.addPlot(title='Summed derivative', x=shortest_derivative_x, y=derivatives['summed'], pen='b', colspan=2)

            def calculate_qrsd():
                self.qrsd[file_name] = slider_qrs_end.value() - slider_qrs_start.value()

            def calculate_st():
                self.st[file_name] = {}
                for lead,data,slider_st_height,slider_iso_height in zip(file_data.keys(),file_data.values(),st_segment_horizontal_markers.values(),isoelectric_horizontal_markers.values()):
                    iso_height = slider_iso_height.value()
                    st_height = slider_st_height.value()
                    self.st[file_name][lead] = st_height - iso_height
                update_results()

            def update_isoelectric():
                iso = slider_isoelectric.value()
                for iso_horizontal,iso_vertical,lead_data in zip(isoelectric_horizontal_markers.values(),isoelectric_vertical_markers.values(),file_data.values()):
                    iso_horizontal.setValue(np.interp(iso, lead_data['x'], lead_data['y']))
                    iso_vertical.setValue(iso)
                calculate_qrsd()
                calculate_st()
                update_results()

            def update_qrs():
                start = slider_qrs_start.value()
                end = slider_qrs_end.value()
                for region in qrs_regions.values():
                    region.setRegion([start, end])
                for st_horizontal,st_vertical,lead_data in zip(st_segment_horizontal_markers.values(),st_segment_vertical_markers.values(),file_data.values()):
                    st_horizontal.setValue(np.interp(end+ProcessedECG.J_POINT_OFFSET,lead_data['x'],lead_data['y']))
                    st_vertical.setValue(end+ProcessedECG.J_POINT_OFFSET)
                calculate_qrsd()
                calculate_st()
                update_results()

            def update_results():
                label_results_left.setText("   RESULTS   <br>QRSd\t%0.f<br>I\t%0.1f mm<br>II\t%0.1f mm<br>III\t%0.1f mm<br>aVR\t%0.1f mm<br>aVL\t%0.1f mm<br>aVF\t%0.1f mm" % (self.qrsd[file_name],self.st[file_name]['I'],self.st[file_name]['II'],self.st[file_name]['III'],self.st[file_name]['aVR'],self.st[file_name]['aVL'],self.st[file_name]['aVF']))
                label_results_right.setText("   RESULTS   <br><br>V1\t%0.1f mm<br>V2\t%0.1f mm<br>V3\t%0.1f mm<br>V4\t%0.1f mm<br>V5\t%0.1f mm<br>V6\t%0.1f mm" % (self.st[file_name]['V1'],self.st[file_name]['V2'],self.st[file_name]['V3'],self.st[file_name]['V4'],self.st[file_name]['V5'],self.st[file_name]['V6']))

            slider_isoelectric = pg.InfiniteLine(pos=400, angle=90, movable=True)
            slider_qrs_start = pg.InfiniteLine(pos=600, angle=90, movable=True)
            slider_qrs_end = pg.InfiniteLine(pos=700, angle=90, movable=True)

            plot_derivative.addItem(slider_isoelectric, ignoreBounds=True)
            plot_derivative.addItem(slider_qrs_start, ignoreBounds=True)
            plot_derivative.addItem(slider_qrs_end, ignoreBounds=True)

            slider_isoelectric.sigPositionChanged.connect(update_isoelectric)
            slider_qrs_start.sigPositionChanged.connect(update_qrs)
            slider_qrs_end.sigPositionChanged.connect(update_qrs)

            label_results_left = pg.LabelItem(text="   RESULTS   <br>QRSd\t<br>I\t mm<br>II\t mm<br>III\t mm<br>aVL\t mm<br>aVR\t mm<br>aVF\ mm",justify='left')
            win.addItem(label_results_left)

            label_results_right = pg.LabelItem(text="   RESULTS   <br><br>V1\t mm<br>V2\t mm<br>V3\t mm<br>V4\t mm<br>V5\t mm<br>V6\ mm", justify='left')
            win.addItem(label_results_right)

            app.instance().exec_()
            del app
        return (self.qrsd,self.st)