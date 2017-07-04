import numpy

from PyQt5.QtGui import QPalette, QColor, QFont
from PyQt5.QtWidgets import QMessageBox, QApplication
from PyQt5.QtCore import QRect

from orangewidget import gui
from orangewidget import widget
from orangewidget.settings import Setting
from oasys.widgets import gui as oasysgui
from oasys.widgets import congruence
from oasys.widgets.gui import ConfirmDialog

from syned.widget.widget_decorator import WidgetDecorator
from syned.beamline.element_coordinates import ElementCoordinates
from syned.beamline.beamline_element import BeamlineElement

from wofry.propagator.propagator import PropagationManager, PropagationElements, PropagationParameters
from wofry.propagator.wavefront2D.generic_wavefront import GenericWavefront2D
from wofry.propagator.propagators2D.fresnel import Fresnel2D, FresnelConvolution2D
from wofry.propagator.propagators2D.fraunhofer import Fraunhofer2D
from wofry.propagator.propagators2D.integral import Integral2D

from orangecontrib.wofry.widgets.gui.ow_wofry_widget import WofryWidget

def initialize_default_propagator_2D():
    propagator = PropagationManager.Instance()

    propagator.add_propagator(Fraunhofer2D())
    propagator.add_propagator(Fresnel2D())
    propagator.add_propagator(FresnelConvolution2D())
    propagator.add_propagator(Integral2D())

try:
    initialize_default_propagator_2D()
except:
    pass

class OWWOOpticalElement(WofryWidget, WidgetDecorator):

    maintainer = "Luca Rebuffi"
    maintainer_email = "luca.rebuffi(@at@)elettra.eu"
    keywords = ["data", "file", "load", "read"]
    category = "Wofry Optical Elements"

    outputs = [{"name":"GenericWavefront2D",
                "type":GenericWavefront2D,
                "doc":"GenericWavefront2D",
                "id":"GenericWavefront2D"}]

    inputs = [("GenericWavefront2D", GenericWavefront2D, "set_input"),
              WidgetDecorator.syned_input_data()[0]]

    oe_name         = Setting("")
    p               = Setting(0.0)
    q               = Setting(0.0)
    angle_radial    = Setting(0.0)
    angle_azimuthal = Setting(0.0)

    shape = Setting(0)
    surface_shape = Setting(0)

    input_wavefront = None
    wavefront_to_plot = None

    propagators_list = ["Fresnel", "Fresnel (Convolution)", "Fraunhofer", "Integral"]

    propagator = Setting(0)
    shift_half_pixel = Setting(1)

    shuffle_interval = Setting(0)
    calculate_grid_only = Setting(1)

    def __init__(self):
        super().__init__()

        self.runaction = widget.OWAction("Propagate Wavefront", self)
        self.runaction.triggered.connect(self.propagate_wavefront)
        self.addAction(self.runaction)

        button_box = oasysgui.widgetBox(self.controlArea, "", addSpace=False, orientation="horizontal")

        button = gui.button(button_box, self, "Propagate Wavefront", callback=self.propagate_wavefront)
        font = QFont(button.font())
        font.setBold(True)
        button.setFont(font)
        palette = QPalette(button.palette()) # make a copy of the palette
        palette.setColor(QPalette.ButtonText, QColor('Dark Blue'))
        button.setPalette(palette) # assign new palette
        button.setFixedHeight(45)

        button = gui.button(button_box, self, "Reset Fields", callback=self.callResetSettings)
        font = QFont(button.font())
        font.setItalic(True)
        button.setFont(font)
        palette = QPalette(button.palette()) # make a copy of the palette
        palette.setColor(QPalette.ButtonText, QColor('Dark Red'))
        button.setPalette(palette) # assign new palette
        button.setFixedHeight(45)
        button.setFixedWidth(150)

        gui.separator(self.controlArea)

        geom = QApplication.desktop().availableGeometry()
        self.setGeometry(QRect(round(geom.width()*0.05),
                               round(geom.height()*0.05),
                               round(min(geom.width()*0.98, self.MAX_WIDTH)),
                               round(min(geom.height()*0.95, self.MAX_HEIGHT))))

        self.setMaximumHeight(self.geometry().height())
        self.setMaximumWidth(self.geometry().width())

        self.controlArea.setFixedWidth(self.CONTROL_AREA_WIDTH)

        self.tabs_setting = oasysgui.tabWidget(self.controlArea)
        self.tabs_setting.setFixedHeight(self.TABS_AREA_HEIGHT)
        self.tabs_setting.setFixedWidth(self.CONTROL_AREA_WIDTH-5)

        self.tab_bas = oasysgui.createTabPage(self.tabs_setting, "O.E. Setting")
        self.tab_pro = oasysgui.createTabPage(self.tabs_setting, "Propagation Setting")

        oasysgui.lineEdit(self.tab_bas, self, "oe_name", "O.E. Name", labelWidth=260, valueType=str, orientation="horizontal")

        self.coordinates_box = oasysgui.widgetBox(self.tab_bas, "Coordinates", addSpace=True, orientation="vertical")

        oasysgui.lineEdit(self.coordinates_box, self, "p", "Distance from previous Continuation Plane [m]", labelWidth=280, valueType=float, orientation="horizontal")
        oasysgui.lineEdit(self.coordinates_box, self, "q", "Distance to next Continuation Plane [m]", labelWidth=280, valueType=float, orientation="horizontal")
        oasysgui.lineEdit(self.coordinates_box, self, "angle_radial", "Incident Angle (to normal) [deg]", labelWidth=280, valueType=float, orientation="horizontal")
        oasysgui.lineEdit(self.coordinates_box, self, "angle_azimuthal", "Rotation along Beam Axis [deg]", labelWidth=280, valueType=float, orientation="horizontal")

        self.draw_specific_box()

        gui.comboBox(self.tab_pro, self, "propagator", label="Propagator", labelWidth=260,
                     items=self.propagators_list,
                     callback=self.set_Propagator,
                     sendSelectedValue=False, orientation="horizontal")

        self.fresnel_box = oasysgui.widgetBox(self.tab_pro, "", addSpace=False, orientation="vertical", height=90)

        gui.comboBox(self.fresnel_box, self, "shift_half_pixel", label="Shift Half Pixel", labelWidth=260,
                     items=["No", "Yes"],
                     sendSelectedValue=False, orientation="horizontal")

        self.fraunhofer_box = oasysgui.widgetBox(self.tab_pro, "", addSpace=False, orientation="vertical", height=90)

        gui.comboBox(self.fraunhofer_box, self, "shift_half_pixel", label="Shift Half Pixel", labelWidth=260,
                     items=["No", "Yes"],
                     sendSelectedValue=False, orientation="horizontal")

        self.integral_box = oasysgui.widgetBox(self.tab_pro, "", addSpace=False, orientation="vertical", height=90)


        oasysgui.lineEdit(self.integral_box, self, "shuffle_interval", "Shuffle Interval (0=no shift) [m]", labelWidth=260, valueType=float, orientation="horizontal")

        gui.comboBox(self.integral_box, self, "calculate_grid_only", label="Calculate Grid Only", labelWidth=260,
                     items=["No", "Yes"],
                     sendSelectedValue=False, orientation="horizontal")

        self.set_Propagator()


    def set_Propagator(self):
        self.fresnel_box.setVisible(self.propagator <= 1)
        self.fraunhofer_box.setVisible(self.propagator == 2)
        self.integral_box.setVisible(self.propagator == 3)

    def draw_specific_box(self):
        raise NotImplementedError()

    def check_data(self):
        congruence.checkPositiveNumber(self.p, "Distance from previous Continuation Plane")
        congruence.checkPositiveNumber(self.q, "Distance to next Continuation Plane")
        congruence.checkPositiveAngle(self.angle_radial, "Incident Angle (to normal)")
        congruence.checkPositiveAngle(self.angle_azimuthal, "Rotation along Beam Axis")

    def propagate_wavefront(self):
        try:
            self.progressBarInit()

            if self.input_wavefront is None: raise Exception("No Input Wavefront")

            self.check_data()

            # propagation to o.e.

            propagation_elements = PropagationElements()

            beamline_element = BeamlineElement(optical_element=self.get_optical_element(),
                                               coordinates=ElementCoordinates(p=self.p,
                                                                              q=self.q,
                                                                              angle_radial=numpy.radians(self.angle_radial),
                                                                              angle_azimuthal=numpy.radians(self.angle_azimuthal)))

            propagation_elements.add_beamline_element(beamline_element)

            propagation_parameters = PropagationParameters(wavefront=self.input_wavefront.duplicate(),
                                                           propagation_elements = propagation_elements)

            self.set_additional_parameters(propagation_parameters)

            propagator = PropagationManager.Instance()

            output_wavefront = propagator.do_propagation(propagation_parameters=propagation_parameters,
                                                         handler_name=self.get_handler_name())


            self.wavefront_to_plot = output_wavefront

            self.initializeTabs()
            self.do_plot_results()
            self.progressBarFinished()

            self.send("GenericWavefront2D", output_wavefront)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e.args[0]), QMessageBox.Ok)

            self.setStatusMessage("")
            self.progressBarFinished()

            raise e

    def get_handler_name(self):
        if self.propagator == 0:
            return Fresnel2D.HANDLER_NAME
        elif self.propagator == 1:
            return FresnelConvolution2D.HANDLER_NAME
        elif self.propagator == 2:
            return Fraunhofer2D.HANDLER_NAME
        elif self.propagator == 3:
            return Integral2D.HANDLER_NAME

    def set_additional_parameters(self, propagation_parameters):
        if self.propagator <= 2:
            propagation_parameters.set_additional_parameters("shift_half_pixel", self.shift_half_pixel==1)
        elif self.propagator == 3:
            propagation_parameters.set_additional_parameters("shuffle_interval", self.shuffle_interval)
            propagation_parameters.set_additional_parameters("calculate_grid_only", self.calculate_grid_only)


    def get_optical_element(self):
        raise NotImplementedError()

    def set_input(self, wavefront):
        if not wavefront is None:
            self.input_wavefront = wavefront

            if self.is_automatic_execution:
                self.propagate_wavefront()

    def initializeTabs(self):
        size = len(self.tab)
        indexes = range(0, size)

        for index in indexes:
            self.tabs.removeTab(size-1-index)

        titles = ["Wavefront 2D"]
        self.tab = []
        self.plot_canvas = []

        for index in range(0, len(titles)):
            self.tab.append(gui.createTabPage(self.tabs, titles[index]))
            self.plot_canvas.append(None)

        for tab in self.tab:
            tab.setFixedHeight(self.IMAGE_HEIGHT)
            tab.setFixedWidth(self.IMAGE_WIDTH)

    def do_plot_results(self, progressBarValue=80):
        if not self.wavefront_to_plot is None:

            self.progressBarSet(progressBarValue)

            titles = ["Wavefront 2D Intensity"]

            self.plot_data2D(data2D=self.wavefront_to_plot.get_intensity(),
                             dataX=self.wavefront_to_plot.get_coordinate_x(),
                             dataY=self.wavefront_to_plot.get_coordinate_y(),
                             progressBarValue=progressBarValue,
                             tabs_canvas_index=0,
                             plot_canvas_index=0,
                             title=titles[0],
                             xtitle="Horizontal Coordinate",
                             ytitle="Vertical Coordinate")


            self.progressBarFinished()

    def receive_syned_data(self, data):
        if not data is None:
            beamline_element = data.get_beamline_element_at(-1)

            if not beamline_element is None:
                self.oe_name = beamline_element._optical_element._name
                self.p = beamline_element._coordinates._p
                self.q = beamline_element._coordinates._q
                self.angle_azimuthal = beamline_element._coordinates._angle_azimuthal
                self.angle_radial = beamline_element._coordinates._angle_radial

                self.receive_specific_syned_data(beamline_element._optical_element)
            else:
                raise Exception("Syned Data not correct: Empty Beamline Element")

    def receive_specific_syned_data(self, optical_element):
        raise NotImplementedError()

    def callResetSettings(self):
        if ConfirmDialog.confirmed(parent=self, message="Confirm Reset of the Fields?"):
            try:
                self.resetSettings()
            except:
                pass




