import pdfquery
import ast
from pdfquery.cache import FileCache
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import glob

class ECGData:

    # Locations are based on PDF 'user' units
    # An A4 page is 595.3 x 841.9 starting bottom left corner
    # This class variable stores the locations of each ECG lead
    # Store as X and Y

    # The height of the plot area is 149.94mm = 30 big squares = 15mV = 424.92 PDF units
    # The width of the plot area is 260.01 = 52 big squares = 10.4s = 737.04 PDF units

    VERBOSE = False

    PDF_UNITS_PER_mm = 424.92 / 149.94 #mm as in voltage (1 mm = 10mV)
    PDF_UNITS_PER_ms = 737.04/(10.4*1000)

    FIRST_COLUMN_LEFT,FIRST_COLUMN_RIGHT = 40,200
    SECOND_COLUMN_LEFT,SECOND_COLUMN_RIGHT = 200,350
    THIRD_COLUMN_LEFT,THIRD_COLUMN_RIGHT = 350,500
    FOURTH_COLUMN_LEFT, FOURTH_COLUMN_RIGHT = 500, 650

    FIRST_ROW_BOT,FIRST_ROW_TOP = 360,460
    SECOND_ROW_BOT, SECOND_ROW_TOP = 250, 380
    THIRD_ROW_BOT,THIRD_ROW_TOP = 160,260

    locations = {'I':   [FIRST_COLUMN_LEFT,FIRST_ROW_BOT,FIRST_COLUMN_RIGHT,FIRST_ROW_TOP],
                 'aVR': [SECOND_COLUMN_LEFT,FIRST_ROW_BOT,SECOND_COLUMN_RIGHT,FIRST_ROW_TOP],
                 'V1':  [THIRD_COLUMN_LEFT,FIRST_ROW_BOT,THIRD_COLUMN_RIGHT,FIRST_ROW_TOP],
                 'V4':  [FOURTH_COLUMN_LEFT,FIRST_ROW_BOT,FOURTH_COLUMN_RIGHT,FIRST_ROW_TOP],
                 'II':  [FIRST_COLUMN_LEFT,SECOND_ROW_BOT,FIRST_COLUMN_RIGHT,SECOND_ROW_TOP],
                 'aVL': [SECOND_COLUMN_LEFT,SECOND_ROW_BOT,SECOND_COLUMN_RIGHT,SECOND_ROW_TOP],
                 'V2':  [THIRD_COLUMN_LEFT,SECOND_ROW_BOT,THIRD_COLUMN_RIGHT,SECOND_ROW_TOP],
                 'V5':  [FOURTH_COLUMN_LEFT,SECOND_ROW_BOT,FOURTH_COLUMN_RIGHT,SECOND_ROW_TOP],
                 'III': [FIRST_COLUMN_LEFT,THIRD_ROW_BOT,FIRST_COLUMN_RIGHT,THIRD_ROW_TOP],
                 'aVF': [SECOND_COLUMN_LEFT,THIRD_ROW_BOT,SECOND_COLUMN_RIGHT,THIRD_ROW_TOP],
                 'V3':  [THIRD_COLUMN_LEFT,THIRD_ROW_BOT,THIRD_COLUMN_RIGHT,THIRD_ROW_TOP],
                 'V6':  [FOURTH_COLUMN_LEFT,THIRD_ROW_BOT,FOURTH_COLUMN_RIGHT,THIRD_ROW_TOP]}

    def __init__(self, patient):

        self.patient = patient

        self.file_list = self.getFileList(self.patient)

        self.leads_by_file = self.extractLeadsFromFileList(self.patient,self.file_list)

    def getFileList(self,patient):
        return glob.glob("./input/{}/*.pdf".format(patient))

    def extractLeadsFromFileList(self,patient,file_list):
        filedict = {}
        for i,file in enumerate(file_list):
            print("Loading file {} of {}...".format(i+1,len(file_list)))
            pdf = pdfquery.PDFQuery(file,parse_tree_cacher=FileCache("./output/tmp/"))
            pdf.load(0)
            print("Loaded!")

            leads={}
            for lead, location in ECGData.locations.items():
                leads[lead] = pdf.pq('LTRect:in_bbox("{}, {}, {}, {}")'.format(
                    location[0],
                    location[1],
                    location[2],
                    location[3]))

            for lead,imagelist in leads.items():
                points = []
                for i,image in enumerate(imagelist):

                    for line_or_curve in image.getchildren():
                        try:
                            stringtolist = ast.literal_eval(line_or_curve.attrib['pts'])
                        except KeyError:
                            break
                        points.append(stringtolist[1])
                    x = [point[0] for point in points]
                    y = [point[1] for point in points]
                    x = [point-min(x)+20 for point in x]
                    y = [point-min(y)+20 for point in y]
                    x_sorted = [X/ECGData.PDF_UNITS_PER_ms for X, Y in sorted(zip(x, y))]
                    y_sorted = [Y/ECGData.PDF_UNITS_PER_mm for X, Y in sorted(zip(x, y))]
                leads[lead] = {'x':x_sorted,'y':y_sorted}
            filedict[file] = leads
        return filedict

    def plot(self):

        pg.setConfigOptions(antialias=True)
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')

        for filename,leads in self.leads_by_file.items():
            app = QtGui.QApplication([])
            win = pg.GraphicsWindow(title="ETT: File {}".format(filename))
            win.setWindowTitle('ETT: File {}'.format(filename))

            colcount = 0

            for lead,lead_data in leads.items():
                if colcount == 4:
                    win.nextRow()
                    colcount = 0
                plot = win.addPlot(title=lead, x=lead_data['x'], y=lead_data['y'], pen='b')
                plot.setYRange(0, 35, padding=0)
                colcount += 1

            app.instance().exec_()
            del app