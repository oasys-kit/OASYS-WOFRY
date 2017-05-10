import numpy

from silx.gui.plot import PlotWindow, Plot2D

from PyQt4 import QtGui

from orangewidget import gui
from orangewidget.settings import Setting
from oasys.widgets import gui as oasysgui

from oasys.widgets.widget import AutomaticWidget

class WofryWidget(AutomaticWidget):
    maintainer = "Luca Rebuffi"
    maintainer_email = "luca.rebuffi(@at@)elettra.eu"

    IMAGE_WIDTH = 760
    IMAGE_HEIGHT = 545
    MAX_WIDTH = 1320
    MAX_HEIGHT = 700
    CONTROL_AREA_WIDTH = 405
    TABS_AREA_HEIGHT = 560

    want_main_area = 1

    view_type=Setting(1)

    def __init__(self, is_automatic=True):
        super().__init__(is_automatic)

        self.main_tabs = gui.tabWidget(self.mainArea)
        plot_tab = gui.createTabPage(self.main_tabs, "Results")
        out_tab = gui.createTabPage(self.main_tabs, "Output")

        view_box = oasysgui.widgetBox(plot_tab, "Results Options", addSpace=False, orientation="horizontal")
        view_box_1 = oasysgui.widgetBox(view_box, "", addSpace=False, orientation="vertical", width=350)

        self.view_type_combo = gui.comboBox(view_box_1, self, "view_type", label="View Results",
                                            labelWidth=220,
                                            items=["No", "Yes"],
                                            callback=self.set_ViewType, sendSelectedValue=False, orientation="horizontal")

        self.tab = []
        self.tabs = gui.tabWidget(plot_tab)

        self.initializeTabs()

        self.wofry_output = QtGui.QTextEdit()
        self.wofry_output.setReadOnly(True)

        out_box = gui.widgetBox(out_tab, "System Output", addSpace=True, orientation="horizontal")
        out_box.layout().addWidget(self.wofry_output)

        self.wofry_output.setFixedHeight(600)
        self.wofry_output.setFixedWidth(600)

        gui.rubber(self.mainArea)


    def initializeTabs(self):
        raise NotImplementedError()

    def set_ViewType(self):
        self.progressBarInit()

        try:
            self.initializeTabs()

            self.plot_results()
        except Exception as exception:
            QtGui.QMessageBox.critical(self, "Error",
                                       str(exception),
                QtGui.QMessageBox.Ok)

        self.progressBarFinished()

    def plot_results(self, progressBarValue=80):
        if not self.view_type == 0:
            self.do_plot_results(progressBarValue)


    def do_plot_results(self, progressBarValue):
        raise NotImplementedError()

    def plot_data1D(self, x, y, progressBarValue, tabs_canvas_index, plot_canvas_index, title="", xtitle="", ytitle="",
                   log_x=False, log_y=False, color='blue', replace=True, control=False):

        if self.plot_canvas[plot_canvas_index] is None:
            self.plot_canvas[plot_canvas_index] = PlotWindow(parent=None,
                                                             backend=None,
                                                             resetzoom=True,
                                                             autoScale=False,
                                                             logScale=True,
                                                             grid=True,
                                                             curveStyle=True,
                                                             colormap=False,
                                                             aspectRatio=False,
                                                             yInverted=False,
                                                             copy=True,
                                                             save=True,
                                                             print_=True,
                                                             control=control,
                                                             position=True,
                                                             roi=False,
                                                             mask=False,
                                                             fit=False)


            self.plot_canvas[plot_canvas_index].setDefaultPlotLines(True)
            self.plot_canvas[plot_canvas_index].setActiveCurveColor(color='darkblue')
            self.plot_canvas[plot_canvas_index].setGraphXLabel(xtitle)
            self.plot_canvas[plot_canvas_index].setGraphYLabel(ytitle)

            self.tab[tabs_canvas_index].layout().addWidget(self.plot_canvas[plot_canvas_index])

        WofryWidget.plot_histo(self.plot_canvas[plot_canvas_index], x, y, title, xtitle, ytitle, color, replace)

        self.plot_canvas[plot_canvas_index].setXAxisLogarithmic(log_x)
        self.plot_canvas[plot_canvas_index].setYAxisLogarithmic(log_y)

        if min(y) < 0:
            if log_y:
                self.plot_canvas[plot_canvas_index].setGraphYLimits(min(y)*1.2, max(y)*1.2)
            else:
                self.plot_canvas[plot_canvas_index].setGraphYLimits(min(y)*1.01, max(y)*1.01)
        else:
            if log_y:
                self.plot_canvas[plot_canvas_index].setGraphYLimits(min(y), max(y)*1.2)
            else:
                self.plot_canvas[plot_canvas_index].setGraphYLimits(min(y), max(y)*1.01)

        self.progressBarSet(progressBarValue)

    def plot_data2D(self, data2D, dataX, dataY, progressBarValue, tabs_canvas_index, plot_canvas_index, title="", xtitle="", ytitle=""):

        self.tab[tabs_canvas_index].layout().removeItem(self.tab[tabs_canvas_index].layout().itemAt(0))

        xmin = numpy.min(dataX)
        xmax = numpy.max(dataX)
        ymin = numpy.min(dataY)
        ymax = numpy.max(dataY)

        origin = (xmin, ymin)
        scale = (abs((xmax-xmin)/len(dataX)), abs((ymax-ymin)/len(dataY)))

        data_to_plot = data2D.T

        colormap = {"name":"temperature", "normalization":"linear", "autoscale":True, "vmin":0, "vmax":0, "colors":256}

        self.plot_canvas[plot_canvas_index] = Plot2D()

        self.plot_canvas[plot_canvas_index].resetZoom()
        self.plot_canvas[plot_canvas_index].setXAxisAutoScale(True)
        self.plot_canvas[plot_canvas_index].setYAxisAutoScale(True)
        self.plot_canvas[plot_canvas_index].setGraphGrid(False)
        self.plot_canvas[plot_canvas_index].setKeepDataAspectRatio(True)
        self.plot_canvas[plot_canvas_index].yAxisInvertedAction.setVisible(False)

        self.plot_canvas[plot_canvas_index].setXAxisLogarithmic(False)
        self.plot_canvas[plot_canvas_index].setYAxisLogarithmic(False)
        #silx 0.4.0
        self.plot_canvas[plot_canvas_index].getMaskAction().setVisible(False)
        self.plot_canvas[plot_canvas_index].getRoiAction().setVisible(False)
        self.plot_canvas[plot_canvas_index].getColormapAction().setVisible(False)
        self.plot_canvas[plot_canvas_index].setKeepDataAspectRatio(False)

        self.plot_canvas[plot_canvas_index].addImage(numpy.array(data_to_plot),
                                                     legend="zio billy",
                                                     scale=scale,
                                                     origin=origin,
                                                     colormap=colormap,
                                                     replace=True)

        self.plot_canvas[plot_canvas_index].setActiveImage("zio billy")

        from matplotlib.image import AxesImage
        image = AxesImage(self.plot_canvas[plot_canvas_index]._backend.ax)
        image.set_data(numpy.array(data_to_plot))

        self.plot_canvas[plot_canvas_index]._backend.fig.colorbar(image, ax=self.plot_canvas[plot_canvas_index]._backend.ax)

        self.plot_canvas[plot_canvas_index].setGraphXLabel(xtitle)
        self.plot_canvas[plot_canvas_index].setGraphYLabel(ytitle)
        self.plot_canvas[plot_canvas_index].setGraphTitle(title)

        self.tab[tabs_canvas_index].layout().addWidget(self.plot_canvas[plot_canvas_index])

        self.progressBarSet(progressBarValue)

    @classmethod
    def plot_histo(cls, plot_window, x, y, title, xtitle, ytitle, color='blue', replace=True):
        import matplotlib
        matplotlib.rcParams['axes.formatter.useoffset']='False'

        plot_window.addCurve(x, y, title, symbol='', color=color, xlabel=xtitle, ylabel=ytitle, replace=replace) #'+', '^', ','

        if not xtitle is None: plot_window.setGraphXLabel(xtitle)
        if not ytitle is None: plot_window.setGraphYLabel(ytitle)
        if not title is None: plot_window.setGraphTitle(title)

        plot_window.setDrawModeEnabled(True, 'rectangle')
        plot_window.setZoomModeEnabled(True)
        plot_window.resetZoom()
        plot_window.replot()

        plot_window.setActiveCurve(title)