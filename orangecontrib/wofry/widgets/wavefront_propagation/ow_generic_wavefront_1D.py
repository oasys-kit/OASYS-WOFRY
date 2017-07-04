from PyQt5.QtGui import QPalette, QColor, QFont
from PyQt5.QtWidgets import QMessageBox
from orangewidget import gui
from orangewidget import widget
from orangewidget.settings import Setting
from oasys.widgets import gui as oasysgui
from oasys.widgets import congruence

from wofry.propagator.wavefront1D.generic_wavefront import GenericWavefront1D

from orangecontrib.wofry.widgets.gui.ow_wofry_widget import WofryWidget

class OWGenericWavefront1D(WofryWidget):

    name = "Generic Wavefront 1D"
    id = "GenericWavefront1D"
    description = "Generic Wavefront 1D"
    icon = "icons/gw1d.png"
    priority = 1

    category = "Wofry Wavefront Propagation"
    keywords = ["data", "file", "load", "read"]

    outputs = [{"name":"GenericWavefront1D",
                "type":GenericWavefront1D,
                "doc":"GenericWavefront1D",
                "id":"GenericWavefront1D"}]

    units = Setting(1)
    energy = Setting(1000.0)
    wavelength = Setting(1e-10)
    number_of_points = Setting(1000)
    initialize_from = Setting(0)
    range_from = Setting(0.0)
    range_to = Setting(0.0)
    steps_start = Setting(0.0)
    steps_step = Setting(0.0)

    kind_of_wave = Setting(0)

    initialize_amplitude = Setting(0)
    complex_amplitude_re = Setting(1.0)
    complex_amplitude_im = Setting(0.0)
    radius = Setting(0.0)

    amplitude = Setting(1.0)
    phase = Setting(0.0)

    wavefront1D = None

    def __init__(self):
        super().__init__(is_automatic=False, show_view_options=False)

        self.runaction = widget.OWAction("Generate Wavefront", self)
        self.runaction.triggered.connect(self.generate)
        self.addAction(self.runaction)


        gui.separator(self.controlArea)

        button_box = oasysgui.widgetBox(self.controlArea, "", addSpace=False, orientation="horizontal")

        button = gui.button(button_box, self, "Generate", callback=self.generate)
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

        self.tab_sou = oasysgui.createTabPage(tabs_setting, "Generic Wavefront 1D Settings")

        box_energy = oasysgui.widgetBox(self.tab_sou, "Energy Settings", addSpace=False, orientation="vertical")

        gui.comboBox(box_energy, self, "units", label="Units in use", labelWidth=350,
                     items=["Electron Volts", "Meters"],
                     callback=self.set_Units,
                     sendSelectedValue=False, orientation="horizontal")

        self.units_box_1 = oasysgui.widgetBox(box_energy, "", addSpace=False, orientation="vertical")

        oasysgui.lineEdit(self.units_box_1, self, "energy", "Photon Energy [eV]",
                          labelWidth=300, valueType=float, orientation="horizontal")

        self.units_box_2 = oasysgui.widgetBox(box_energy, "", addSpace=False, orientation="vertical")

        oasysgui.lineEdit(self.units_box_2, self, "wavelength", "Photon Wavelength [m]",
                          labelWidth=300, valueType=float, orientation="horizontal")

        self.set_Units()

        box_space = oasysgui.widgetBox(self.tab_sou, "Space Settings", addSpace=False, orientation="vertical")

        oasysgui.lineEdit(box_space, self, "number_of_points", "Number of Points",
                          labelWidth=300, valueType=int, orientation="horizontal")

        gui.comboBox(box_space, self, "initialize_from", label="Space Initialization", labelWidth=350,
                     items=["From Range", "From Steps"],
                     callback=self.set_Initialization,
                     sendSelectedValue=False, orientation="horizontal")

        self.initialization_box_1 = oasysgui.widgetBox(box_space, "", addSpace=False, orientation="vertical")

        oasysgui.lineEdit(self.initialization_box_1, self, "range_from", "From  [m]",
                          labelWidth=300, valueType=float, orientation="horizontal")

        oasysgui.lineEdit(self.initialization_box_1, self, "range_to", "To [m]",
                          labelWidth=300, valueType=float, orientation="horizontal")

        self.initialization_box_2 = oasysgui.widgetBox(box_space, "", addSpace=False, orientation="vertical")

        oasysgui.lineEdit(self.initialization_box_2, self, "steps_start", "Start [m]",
                          labelWidth=300, valueType=float, orientation="horizontal")

        oasysgui.lineEdit(self.initialization_box_2, self, "steps_step", "Step [m]",
                          labelWidth=300, valueType=float, orientation="horizontal")

        self.set_Initialization()

        box_amplitude = oasysgui.widgetBox(self.tab_sou, "Amplitude Settings", addSpace=False, orientation="vertical")

        gui.comboBox(box_amplitude, self, "kind_of_wave", label="Kind of Wave", labelWidth=350,
                     items=["Plane", "Spherical"],
                     callback=self.set_KindOfWave,
                     sendSelectedValue=False, orientation="horizontal")


        self.plane_box = oasysgui.widgetBox(box_amplitude, "", addSpace=False, orientation="vertical", height=90)
        self.spherical_box = oasysgui.widgetBox(box_amplitude, "", addSpace=False, orientation="vertical", height=90)

        gui.comboBox(self.plane_box, self, "initialize_amplitude", label="Amplitude Initialization", labelWidth=350,
                     items=["Complex", "Real"],
                     callback=self.set_Amplitude,
                     sendSelectedValue=False, orientation="horizontal")

        self.amplitude_box_1 = oasysgui.widgetBox(self.plane_box, "", addSpace=False, orientation="horizontal", height=50)

        oasysgui.lineEdit(self.amplitude_box_1, self, "complex_amplitude_re", "Complex Amplitude ",
                          labelWidth=250, valueType=float, orientation="horizontal")

        oasysgui.lineEdit(self.amplitude_box_1, self, "complex_amplitude_im", " + ",
                          valueType=float, orientation="horizontal")

        oasysgui.widgetLabel(self.amplitude_box_1, "i", labelWidth=15)

        self.amplitude_box_2 = oasysgui.widgetBox(self.plane_box, "", addSpace=False, orientation="vertical", height=50)

        oasysgui.lineEdit(self.amplitude_box_2, self, "amplitude", "Amplitude",
                          labelWidth=300, valueType=float, orientation="horizontal")

        oasysgui.lineEdit(self.amplitude_box_2, self, "phase", "Phase",
                          labelWidth=300, valueType=float, orientation="horizontal")

        self.set_Amplitude()


        oasysgui.lineEdit(self.spherical_box, self, "radius", "Radius [m]",
                          labelWidth=300, valueType=float, orientation="horizontal")

        amplitude_box_3 = oasysgui.widgetBox(self.spherical_box, "", addSpace=False, orientation="horizontal", height=50)

        oasysgui.lineEdit(amplitude_box_3, self, "complex_amplitude_re", "Complex Amplitude ",
                          labelWidth=250, valueType=float, orientation="horizontal")

        oasysgui.lineEdit(amplitude_box_3, self, "complex_amplitude_im", " + ",
                          valueType=float, orientation="horizontal")

        oasysgui.widgetLabel(amplitude_box_3, "i", labelWidth=15)

        self.set_KindOfWave()


    def set_Units(self):
        self.units_box_1.setVisible(self.units == 0)
        self.units_box_2.setVisible(self.units == 1)

    def set_Initialization(self):
        self.initialization_box_1.setVisible(self.initialize_from == 0)
        self.initialization_box_2.setVisible(self.initialize_from == 1)

    def set_Amplitude(self):
        self.amplitude_box_1.setVisible(self.initialize_amplitude == 0)
        self.amplitude_box_2.setVisible(self.initialize_amplitude == 1)

    def set_KindOfWave(self):
        self.plane_box.setVisible(self.kind_of_wave == 0)
        self.spherical_box.setVisible(self.kind_of_wave == 1)

    def initializeTabs(self):
        size = len(self.tab)
        indexes = range(0, size)

        for index in indexes:
            self.tabs.removeTab(size-1-index)

        titles = ["Wavefront 1D"]
        self.tab = []
        self.plot_canvas = []

        for index in range(0, len(titles)):
            self.tab.append(gui.createTabPage(self.tabs, titles[index]))
            self.plot_canvas.append(None)

        for tab in self.tab:
            tab.setFixedHeight(self.IMAGE_HEIGHT)
            tab.setFixedWidth(self.IMAGE_WIDTH)


    def check_fields(self):
        if self.units == 0:
            congruence.checkStrictlyPositiveNumber(self.energy, "Energy")
        else:
            congruence.checkStrictlyPositiveNumber(self.wavelength, "Wavelength")
        congruence.checkStrictlyPositiveNumber(self.number_of_points, "Number of Points")

        if self.initialize_from == 0:
            congruence.checkGreaterThan(self.range_to, self.range_from, "Range To", "Range From")
        else:
            congruence.checkStrictlyPositiveNumber(self.steps_step, "Step")

        if self.kind_of_wave == 1:
            congruence.checkStrictlyPositiveNumber(self.radius, "Radius")

    def generate(self):
        try:
            self.progressBarInit()

            self.check_fields()

            if self.initialize_from == 0:
                self.wavefront1D = GenericWavefront1D.initialize_wavefront_from_range(x_min=self.range_from, x_max=self.range_to, number_of_points=self.number_of_points)
            else:
                self.wavefront1D = GenericWavefront1D.initialize_wavefront_from_steps(x_start=self.steps_start, x_step=self.steps_step, number_of_points=self.number_of_points)

            if self.units == 0:
                self.wavefront1D.set_photon_energy(self.energy)
            else:
                self.wavefront1D.set_wavelength(self.wavelength)

            if self.kind_of_wave == 0: #plane

                if self.initialize_amplitude == 0:
                    self.wavefront1D.set_plane_wave_from_complex_amplitude(complex_amplitude=complex(self.complex_amplitude_re, self.complex_amplitude_im))
                else:
                    self.wavefront1D.set_plane_wave_from_amplitude_and_phase(amplitude=self.amplitude, phase=self.phase)

            else:
                self.wavefront1D.set_spherical_wave(radius=self.radius, complex_amplitude=complex(self.complex_amplitude_re, self.complex_amplitude_im))

            self.initializeTabs()
            self.plot_results()

            self.send("GenericWavefront1D", self.wavefront1D)
        except Exception as exception:
            QMessageBox.critical(self, "Error", str(exception), QMessageBox.Ok)

            #raise exception

            self.progressBarFinished()

    def do_plot_results(self, progressBarValue=80):
        if not self.wavefront1D is None:

            self.progressBarSet(progressBarValue)

            titles = ["Wavefront 1D Intensity"]

            self.plot_data1D(x=self.wavefront1D.get_abscissas(),
                             y=self.wavefront1D.get_intensity(),
                             progressBarValue=progressBarValue,
                             tabs_canvas_index=0,
                             plot_canvas_index=0,
                             title=titles[0],
                             xtitle="Spatial Coordinate",
                             ytitle="Intensity")


            self.plot_canvas[0].resetZoom()

            self.progressBarFinished()
