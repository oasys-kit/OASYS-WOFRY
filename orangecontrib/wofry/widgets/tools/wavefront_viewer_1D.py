__author__ = 'labx'

import numpy

from PyQt5.QtGui import QPalette, QColor, QFont
from PyQt5.QtWidgets import QMessageBox
from orangewidget import gui
from orangewidget import widget
from orangewidget.settings import Setting
from oasys.widgets import gui as oasysgui
from oasys.widgets import congruence

from wofry.propagator.wavefront1D.generic_wavefront import GenericWavefront1D

from orangecontrib.wofry.widgets.gui.ow_wofry_widget import WofryWidget

class WavefrontViewer1D(WofryWidget):

    name = "Wavefront Viewer 1D"
    id = "WavefrontViewer1D"
    description = "Wavefront Viewer 1D"
    icon = "icons/wv1d.png"
    priority = 1

    category = "Wofry Tools"
    keywords = ["data", "file", "load", "read"]

    inputs = [("GenericWavefront1D", GenericWavefront1D, "set_input")]

    wavefront1D = None
    phase_unwrap = Setting(0)
    titles = ["Wavefront 1D Intensity", "Wavefront 1D Phase","Wavefront Real(Amplitude)","Wavefront Imag(Amplitude)"]

    def __init__(self):
        super().__init__(is_automatic=False, show_view_options=False)

        gui.separator(self.controlArea)

        button_box = oasysgui.widgetBox(self.controlArea, "", addSpace=False, orientation="horizontal")

        button = gui.button(button_box, self, "Refresh", callback=self.refresh)
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
        tabs_setting.setFixedHeight(self.TABS_AREA_HEIGHT + 50)
        tabs_setting.setFixedWidth(self.CONTROL_AREA_WIDTH-5)

        self.tab_sou = oasysgui.createTabPage(tabs_setting, "Wavefront Viewer Settings")

        gui.comboBox(self.tab_sou, self, "phase_unwrap",
                    label="Phase unwrap ", addSpace=False,
                    items=['No','Yes'],
                    valueType=int, orientation="horizontal", callback=self.refresh)

    def initializeTabs(self):
        size = len(self.tab)
        indexes = range(0, size)

        for index in indexes:
            self.tabs.removeTab(size-1-index)

        self.tab = []
        self.plot_canvas = []

        for index in range(0, len(self.titles)):
            self.tab.append(gui.createTabPage(self.tabs, self.titles[index]))
            self.plot_canvas.append(None)

        for tab in self.tab:
            tab.setFixedHeight(self.IMAGE_HEIGHT)
            tab.setFixedWidth(self.IMAGE_WIDTH)


    def set_input(self, wavefront1D):
        if not wavefront1D is None:
            self.wavefront1D = wavefront1D

            self.refresh()

    def refresh(self):
        self.progressBarInit()

        try:
            if self.wavefront1D is not None:
                current_index = self.tabs.currentIndex()
                self.initializeTabs()
                self.plot_results()
                self.tabs.setCurrentIndex(current_index)
        except Exception as exception:
            QMessageBox.critical(self, "Error", str(exception), QMessageBox.Ok)


    def do_plot_results(self, progressBarValue):
        if self.wavefront1D is not None:

            self.progressBarSet(progressBarValue)

            self.plot_data1D(x=1e6*self.wavefront1D.get_abscissas(),
                             y=self.wavefront1D.get_intensity(),
                             progressBarValue=progressBarValue + 10,
                             tabs_canvas_index=0,
                             plot_canvas_index=0,
                             title=self.titles[0],
                             xtitle="Spatial Coordinate [$\mu$m]",
                             ytitle="Intensity")

            self.plot_data1D(x=1e6*self.wavefront1D.get_abscissas(),
                             y=self.wavefront1D.get_phase(from_minimum_intensity=0.1,unwrap=self.phase_unwrap),
                             progressBarValue=progressBarValue + 10,
                             tabs_canvas_index=1,
                             plot_canvas_index=1,
                             title=self.titles[1],
                             xtitle="Spatial Coordinate [$\mu$m]",
                             ytitle="Phase (rad)")

            self.plot_data1D(x=1e6*self.wavefront1D.get_abscissas(),
                             y=numpy.real(self.wavefront1D.get_complex_amplitude()),
                             progressBarValue=progressBarValue + 10,
                             tabs_canvas_index=2,
                             plot_canvas_index=2,
                             title=self.titles[2],
                             xtitle="Spatial Coordinate [$\mu$m]",
                             ytitle="Real(Amplitude)")

            self.plot_data1D(x=1e6*self.wavefront1D.get_abscissas(),
                             y=numpy.imag(self.wavefront1D.get_complex_amplitude()),
                             progressBarValue=progressBarValue + 10,
                             tabs_canvas_index=3,
                             plot_canvas_index=3,
                             title=self.titles[3],
                             xtitle="Spatial Coordinate [$\mu$m]",
                             ytitle="Imag(Amplitude)")


            self.progressBarFinished()


if __name__ == '__main__':

    from wofry.propagator.wavefront1D.generic_wavefront import GenericWavefront1D
    from PyQt5.QtWidgets import QApplication

    app = QApplication([])
    ow = WavefrontViewer1D()


    # filename_np = "/users/srio/COMSYLD/comsyl/comsyl/calculations/septest_cm_new_u18_2m_1h_s2.5.npz"
    # af = CompactAFReader.initialize_from_file(filename_np)
    wf = GenericWavefront1D.initialize_wavefront_from_arrays(numpy.linspace(-1e-3,1e-3,300),
                                                             numpy.linspace(-1e-3,1e-3,300)**2 )

    ow.set_input(wf)
    ow.show()
    app.exec_()
    ow.saveSettings()