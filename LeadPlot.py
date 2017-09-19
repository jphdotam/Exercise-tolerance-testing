from pyqtgraph.graphicsItems.PlotItem.PlotItem import PlotItem
import numpy as np
import pyqtgraph as pg
from scipy.signal import savgol_filter

class LeadPlot(PlotItem):

    AXIS_PEN = (231, 84, 128)
    PLOT_SAVGOL = True
    AUTO_SCALE_Y = False
    QRS_ONSET_WINDOW = (-10,0) # How many datapoints to look back from peak QRS when finding onset/offset
    J_POINT_OFFSET = 10


    def format(self):
        self.showGrid(x=True, y=True)
        self.getAxis('left').setPen(LeadPlot.AXIS_PEN)
        self.getAxis('bottom').setPen(LeadPlot.AXIS_PEN)
        self.getAxis('left').setStyle(showValues=False)
        self.getAxis('bottom').setStyle(showValues=False)

        if not LeadPlot.AUTO_SCALE_Y: self.setYRange(-10, 20, padding=0)


    def calculate_savgol(self):
        savgol = savgol_filter(x=self.lead_data['y'], window_length=9, polyorder=2, deriv=1)
        max_savgol = max(savgol)

        x_range_qrs = (np.nanargmax(np.abs(self.lead_data['y'])) - 20,
                       np.nanargmax(np.abs(self.lead_data['y'])) + 20)

        windowed_x = self.lead_data['x'][x_range_qrs[0]:x_range_qrs[1]]
        windowed_savgol = np.abs(savgol[x_range_qrs[0]:x_range_qrs[1]])

        if LeadPlot.PLOT_SAVGOL:
            self.plot(x=self.lead_data['x'], y=savgol, pen='g')
            self.plot(x=windowed_x, y=windowed_savgol, pen='b')

        qrs_onset = (np.argwhere(windowed_savgol > 0.15 * max_savgol) + np.nanargmax(np.abs(self.lead_data['y'])) - 20)[0][0]
        qrs_offset = (np.argwhere(windowed_savgol > 0.15 * max_savgol) + np.nanargmax(np.abs(self.lead_data['y'])) - 20)[-1][0]

        return windowed_savgol,qrs_onset,qrs_offset


    def setup_markers(self):

        self.marker_qrs_onset = pg.InfiniteLine(pos=self.lead_data['x'][self.qrs_onset], angle=90, movable=False, pen='g')
        self.addItem(self.marker_qrs_onset, ignoreBounds=True)
        self.marker_qrs_offset = pg.InfiniteLine(pos=self.lead_data['x'][self.qrs_offset], angle=90, movable=False, pen='b')
        self.addItem(self.marker_qrs_offset, ignoreBounds=True)

        self.st_segment_vertical_marker = pg.InfiniteLine(pos=self.lead_data['x'][self.qrs_offset]+10, angle=90, movable=False, pen='r')
        self.addItem(self.st_segment_vertical_marker, ignoreBounds=True)

        self.st_segment_horizontal_marker = pg.InfiniteLine(pos=np.interp(self.marker_qrs_offset.value()+LeadPlot.J_POINT_OFFSET,self.lead_data['x'],self.lead_data['y']), angle=0, movable=False, pen='r')
        self.addItem(self.st_segment_horizontal_marker, ignoreBounds=True)

        #self.isoelectric_vertical_marker = pg.InfiniteLine(angle=90, movable=False, pen='r')
        #self.isoelectric_horizontal_marker = pg.InfiniteLine(pos=200, angle=0, movable=False, pen='r')

        #self.addItem(self.isoelectric_vertical_marker, ignoreBounds=True)
        #self.addItem(self.isoelectric_horizontal_marker, ignoreBounds=True)


    def __init__(self, parent=None, name=None, labels=None, title=None, viewBox=None, axisItems=None, enableMenu=True, *, lead_name, lead_data):
        self.lead_name = lead_name
        self.lead_data = lead_data

        # Set the voltage at 400ms to be 0mV
        self.lead_data['y'][:] = \
            [y - np.interp(400, lead_data['x'], lead_data['y']) for y in lead_data['y']]

        super().__init__(parent=parent, name=name, labels=labels, viewBox=viewBox, axisItems=axisItems, enableMenu=enableMenu, x=lead_data['x'], y=lead_data['y'], title=lead_name)

        self.format()
        self.savgol,self.qrs_onset, self.qrs_offset = self.calculate_savgol()

        self.setup_markers()