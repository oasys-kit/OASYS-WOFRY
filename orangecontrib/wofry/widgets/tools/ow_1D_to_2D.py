__author__ = 'labx'

from PyQt5.QtGui import QPalette, QColor, QFont
from PyQt5.QtWidgets import QMessageBox
from orangewidget import gui
from orangewidget import widget
from orangewidget.settings import Setting
from oasys.widgets import gui as oasysgui
from oasys.widgets import congruence

from wofry.propagator.wavefront1D.generic_wavefront import GenericWavefront1D
from wofry.propagator.wavefront2D.generic_wavefront import GenericWavefront2D

from orangecontrib.wofry.widgets.gui.ow_wofry_widget import WofryWidget

class OW2Dto1D(WofryWidget):

    name = "Wavefronts 1D to 2D"
    id = "Wavefronts1Dto2D"
    description = "Wavefronts 1D to 2D"
    icon = "icons/1d_to_2d.png"
    priority = 3

    category = "Wofry Tools"
    keywords = ["data", "file", "load", "read"]

    inputs = [("Horizontal Wavefront", GenericWavefront1D, "set_input_h"),
              ("Vertical Wavefront", GenericWavefront1D, "set_input_v")]

    outputs = [{"name":"GenericWavefront2D",
                "type":GenericWavefront2D,
                "doc":"GenericWavefront2D",
                "id":"GenericWavefront2D"}]

    normalize_to = Setting(0)

    wavefront2D = None

    wavefront1D_h = None
    wavefront1D_v = None

    def __init__(self):
        super().__init__(is_automatic=True)

        self.runaction = widget.OWAction("Send Data", self)
        self.runaction.triggered.connect(self.send_data)
        self.addAction(self.runaction)

        button_box = oasysgui.widgetBox(self.controlArea, "", addSpace=False, orientation="horizontal")

        button = gui.button(button_box, self, "Send Data", callback=self.send_data)
        font = QFont(button.font())
        font.setBold(True)
        button.setFont(font)
        palette = QPalette(button.palette()) # make a copy of the palette
        palette.setColor(QPalette.ButtonText, QColor('Dark Blue'))
        button.setPalette(palette) # assign new palette
        button.setFixedHeight(45)

        gui.separator(self.controlArea)

        self.controlArea.setFixedWidth(self.CONTROL_AREA_WIDTH)

        tabs_setting = oasysgui.tabWidget(self.controlArea)
        tabs_setting.setFixedHeight(self.TABS_AREA_HEIGHT)
        tabs_setting.setFixedWidth(self.CONTROL_AREA_WIDTH-5)

        self.tab_sou = oasysgui.createTabPage(tabs_setting, "Wavefronts Combination Setting")

        gui.comboBox(self.tab_sou, self, "normalize_to", label="Normalize to", labelWidth=220,
                     items=["Horizontal", "Vertical", "None"],
                     sendSelectedValue=False, orientation="horizontal")

    def initializeTabs(self):
        size = len(self.tab)
        indexes = range(0, size)

        for index in indexes:
            self.tabs.removeTab(size-1-index)

        titles = ["Wavefront 1D (H)", "Wavefront 1D (V)", "Wavefront 2D"]
        self.tab = []
        self.plot_canvas = []

        for index in range(0, len(titles)):
            self.tab.append(gui.createTabPage(self.tabs, titles[index]))
            self.plot_canvas.append(None)

        for tab in self.tab:
            tab.setFixedHeight(self.IMAGE_HEIGHT)
            tab.setFixedWidth(self.IMAGE_WIDTH)

    def set_input_h(self, wavefront1D):
        if not wavefront1D is None:
            self.wavefront1D_h = wavefront1D

            if self.is_automatic_execution:
                self.send_data()

    def set_input_v(self, wavefront1D):
        if not wavefront1D is None:
            self.wavefront1D_v = wavefront1D

            if self.is_automatic_execution:
                self.send_data()

    def send_data(self):
        if not self.wavefront1D_h is None and not self.wavefront1D_v is None:
            self.progressBarInit()

            self.wavefront2D = GenericWavefront2D.combine_1D_wavefronts_into_2D(self.wavefront1D_h,
                                                                                self.wavefront1D_v,
                                                                                normalize_to=self.normalize_to)

            self.plot_results(progressBarValue=50)

            self.progressBarFinished()

            self.send("GenericWavefront2D", self.wavefront2D)

    def do_plot_results(self, progressBarValue):
        if not self.wavefront2D is None and not self.wavefront1D_h is None and not self.wavefront1D_v is None:

            self.progressBarSet(progressBarValue)

            titles = ["Wavefront 1D (H) Intensity", "Wavefront 1D (V) Intensity", "Wavefront 2D Intensity"]

            self.plot_data1D(x=self.wavefront1D_h.get_abscissas(),
                             y=self.wavefront1D_h.get_intensity(),
                             progressBarValue=progressBarValue + 12,
                             tabs_canvas_index=0,
                             plot_canvas_index=0,
                             title=titles[0],
                             xtitle="Horizontal Coordinate",
                             ytitle="Intensity")

            self.plot_data1D(x=self.wavefront1D_v.get_abscissas(),
                             y=self.wavefront1D_v.get_intensity(),
                             progressBarValue=progressBarValue + 12,
                             tabs_canvas_index=1,
                             plot_canvas_index=1,
                             title=titles[1],
                             xtitle="Vertical Coordinate",
                             ytitle="Intensity")

            self.plot_data2D(data2D=self.wavefront2D.get_intensity(),
                             dataX=self.wavefront2D.get_coordinate_x(),
                             dataY=self.wavefront2D.get_coordinate_y(),
                             progressBarValue=progressBarValue + 26,
                             tabs_canvas_index=2,
                             plot_canvas_index=2,
                             title=titles[2],
                             xtitle="Horizontal Coordinate",
                             ytitle="Vertical Coordinate")




