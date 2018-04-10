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
from syned.beamline.shape import *

from wofry.propagator.propagator import PropagationManager, PropagationElements, PropagationParameters
from wofry.propagator.wavefront1D.generic_wavefront import GenericWavefront1D
from wofry.propagator.propagators1D.fresnel import Fresnel1D
from wofry.propagator.propagators1D.fresnel_convolution import FresnelConvolution1D
from wofry.propagator.propagators1D.fraunhofer import Fraunhofer1D
from wofry.propagator.propagators1D.integral import Integral1D
from wofry.propagator.propagators1D.fresnel_zoom import FresnelZoom1D

from orangecontrib.wofry.widgets.gui.ow_wofry_widget import WofryWidget

def initialize_default_propagator_1D():
    propagator = PropagationManager.Instance()

    propagator.add_propagator(Fraunhofer1D())
    propagator.add_propagator(Fresnel1D())
    propagator.add_propagator(FresnelConvolution1D())
    propagator.add_propagator(Integral1D())
    propagator.add_propagator(FresnelZoom1D())

try:
    initialize_default_propagator_1D()
except:
    pass

class OWWOOpticalElement1D(WofryWidget, WidgetDecorator):

    maintainer = "Luca Rebuffi"
    maintainer_email = "luca.rebuffi(@at@)elettra.eu"
    keywords = ["data", "file", "load", "read"]
    category = "Wofry Optical Elements"

    outputs = [{"name":"GenericWavefront1D",
                "type":GenericWavefront1D,
                "doc":"GenericWavefront1D",
                "id":"GenericWavefront1D"}]

    inputs = [("GenericWavefront1D", GenericWavefront1D, "set_input"),
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

    propagators_list = ["Fresnel", "Fresnel (Convolution)", "Fraunhofer", "Integral", "Fresnel Zoom"]
    plot_titles = ["Wavefront 1D Intensity", "Wavefront 1D Phase","Wavefront Real(Amplitude)","Wavefront Imag(Amplitude)"]

    propagator = Setting(4)
    magnification_x = Setting(1.0) # For Fresnel Zoom & Integral
    magnification_N = Setting(1.0) # For Integral

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

        self.tabs_setting = oasysgui.tabWidget(self.controlArea)
        self.tabs_setting.setFixedHeight(self.TABS_AREA_HEIGHT)
        self.tabs_setting.setFixedWidth(self.CONTROL_AREA_WIDTH-5)


        self.tab_bas = oasysgui.createTabPage(self.tabs_setting, "O.E. Setting")
        self.tab_pro = oasysgui.createTabPage(self.tabs_setting, "Propagation Setting")

        oasysgui.lineEdit(self.tab_bas, self, "oe_name", "O.E. Name", labelWidth=260, valueType=str, orientation="horizontal")

        self.coordinates_box = oasysgui.widgetBox(self.tab_bas, "Coordinates", addSpace=True, orientation="vertical")

        oasysgui.lineEdit(self.coordinates_box, self, "p", "Distance from previous Continuation Plane [m]", labelWidth=280, valueType=float, orientation="horizontal")
        oasysgui.lineEdit(self.coordinates_box, self, "q", "Distance to next Continuation Plane [m]", labelWidth=280, valueType=float, orientation="horizontal")
        # Commented srio (not yet implemented) TODO: implement it!
        # oasysgui.lineEdit(self.coordinates_box, self, "angle_radial", "Incident Angle (to normal) [deg]", labelWidth=280, valueType=float, orientation="horizontal")
        # oasysgui.lineEdit(self.coordinates_box, self, "angle_azimuthal", "Rotation along Beam Axis [deg]", labelWidth=280, valueType=float, orientation="horizontal")

        self.draw_specific_box()

        gui.comboBox(self.tab_pro, self, "propagator", label="Propagator", labelWidth=260,
                     items=self.propagators_list,
                     callback=self.set_Propagator,
                     sendSelectedValue=False, orientation="horizontal")

        # Fresnel
        self.fresnel_box = oasysgui.widgetBox(self.tab_pro, "", addSpace=False, orientation="vertical", height=90)

        # Fraunhoffer
        self.fraunhofer_box = oasysgui.widgetBox(self.tab_pro, "", addSpace=False, orientation="vertical", height=90)

        # Integral
        self.integral_box = oasysgui.widgetBox(self.tab_pro, "", addSpace=False, orientation="vertical", height=90)


        oasysgui.lineEdit(self.integral_box, self, "magnification_x", "Magnification Factor for interval",
                          labelWidth=260, valueType=float, orientation="horizontal")
        oasysgui.lineEdit(self.integral_box, self, "magnification_N", "Magnification Factor for N points",
                          labelWidth=260, valueType=float, orientation="horizontal")

        # Fresnel zoom
        self.zoom_box = oasysgui.widgetBox(self.tab_pro, "", addSpace=False, orientation="vertical", height=90)

        oasysgui.lineEdit(self.zoom_box, self, "magnification_x", "Magnification Factor for interval",
                          labelWidth=260, valueType=float, orientation="horizontal")


        self.set_Propagator()


    def set_Propagator(self):
        self.fresnel_box.setVisible(self.propagator <= 1)
        self.fraunhofer_box.setVisible(self.propagator == 2)
        self.integral_box.setVisible(self.propagator == 3)
        self.zoom_box.setVisible(self.propagator == 4)

    def draw_specific_box(self):
        # raise NotImplementedError()
        pass

    def check_data(self):
        congruence.checkNumber(self.p, "Distance from previous Continuation Plane")
        congruence.checkNumber(self.q, "Distance to next Continuation Plane")
        congruence.checkAngle(self.angle_radial, "Incident Angle (to normal)")
        congruence.checkAngle(self.angle_azimuthal, "Rotation along Beam Axis")

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

            self.send("GenericWavefront1D", output_wavefront)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e.args[0]), QMessageBox.Ok)

            self.setStatusMessage("")
            self.progressBarFinished()

            raise e

    def get_handler_name(self):
        if self.propagator == 0:
            return Fresnel1D.HANDLER_NAME
        elif self.propagator == 1:
            return FresnelConvolution1D.HANDLER_NAME
        elif self.propagator == 2:
            return Fraunhofer1D.HANDLER_NAME
        elif self.propagator == 3:
            return Integral1D.HANDLER_NAME
        elif self.propagator == 4:
            return FresnelZoom1D.HANDLER_NAME

    def set_additional_parameters(self, propagation_parameters):
        if self.propagator <= 2:
            pass
        elif self.propagator == 3:
            propagation_parameters.set_additional_parameters("magnification_x", self.magnification_x)
            propagation_parameters.set_additional_parameters("magnification_N", self.magnification_N)
        elif self.propagator == 4:
            propagation_parameters.set_additional_parameters("magnification_x", self.magnification_x)

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

        self.tab = []
        self.plot_canvas = []

        for index in range(0, len(self.plot_titles)):
            self.tab.append(gui.createTabPage(self.tabs, self.plot_titles[index]))
            self.plot_canvas.append(None)

        for tab in self.tab:
            tab.setFixedHeight(self.IMAGE_HEIGHT)
            tab.setFixedWidth(self.IMAGE_WIDTH)

    def do_plot_results(self, progressBarValue=80):

        if not self.wavefront_to_plot is None:

            self.progressBarSet(progressBarValue)

            self.plot_data1D(x=1e6*self.wavefront_to_plot.get_abscissas(),
                             y=self.wavefront_to_plot.get_intensity(),
                             progressBarValue=progressBarValue,
                             tabs_canvas_index=0,
                             plot_canvas_index=0,
                             title=self.plot_titles[0],
                             xtitle="Spatial Coordinate [$\mu$m]",
                             ytitle="Intensity")


            self.plot_data1D(x=1e6*self.wavefront_to_plot.get_abscissas(),
                             y=self.wavefront_to_plot.get_phase(from_minimum_intensity=0.1,unwrap=1),
                             progressBarValue=progressBarValue + 10,
                             tabs_canvas_index=1,
                             plot_canvas_index=1,
                             title=self.plot_titles[1],
                             xtitle="Spatial Coordinate [$\mu$m]",
                             ytitle="Phase [unwrapped, for intensity > 10% of peak] (rad)")

            self.plot_data1D(x=1e6*self.wavefront_to_plot.get_abscissas(),
                             y=numpy.real(self.wavefront_to_plot.get_complex_amplitude()),
                             progressBarValue=progressBarValue + 10,
                             tabs_canvas_index=2,
                             plot_canvas_index=2,
                             title=self.plot_titles[2],
                             xtitle="Spatial Coordinate [$\mu$m]",
                             ytitle="Real(Amplitude)")

            self.plot_data1D(x=1e6*self.wavefront_to_plot.get_abscissas(),
                             y=numpy.imag(self.wavefront_to_plot.get_complex_amplitude()),
                             progressBarValue=progressBarValue + 10,
                             tabs_canvas_index=3,
                             plot_canvas_index=3,
                             title=self.plot_titles[3],
                             xtitle="Spatial Coordinate [$\mu$m]",
                             ytitle="Imag(Amplitude)")


            for i in range(len(self.plot_titles)):
                self.plot_canvas[i].resetZoom()

            self.progressBarFinished()

    def receive_syned_data(self, data):
        if not data is None:
            beamline_element = data.get_beamline_element_at(-1)

            if not beamline_element is None:
                self.oe_name = beamline_element._optical_element._name
                self.p = beamline_element._coordinates._p
                self.q = beamline_element._coordinates._q
                self.angle_azimuthal = round(numpy.degrees(beamline_element._coordinates._angle_azimuthal), 6)
                self.angle_radial = round(numpy.degrees(beamline_element._coordinates._angle_radial), 6)

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




#--------------------------------------------------------------

class OWWOOpticalElementWithBoundaryShape1D(OWWOOpticalElement1D):
    # BOUNDARY

    vertical_shift = Setting(0.0)

    height = Setting(0.0)


    def draw_specific_box(self):
        self.shape_box = oasysgui.widgetBox(self.tab_bas, "Boundary Shape", addSpace=True, orientation="vertical")

        # gui.comboBox(self.shape_box, self, "shape", label="Boundary Shape", labelWidth=350,
        #              items=["Rectangle"],
        #              callback=self.set_Shape,
        #              sendSelectedValue=False, orientation="horizontal")

        oasysgui.lineEdit(self.shape_box, self, "vertical_shift", "Shift [m]", labelWidth=260, valueType=float, orientation="horizontal")

        self.rectangle_box = oasysgui.widgetBox(self.shape_box, "", addSpace=False, orientation="vertical", height=60)

        oasysgui.lineEdit(self.rectangle_box, self, "height", "Aperture [m]", labelWidth=260, valueType=float, orientation="horizontal")

        self.circle_box = oasysgui.widgetBox(self.shape_box, "", addSpace=False, orientation="vertical", height=60)

        self.set_Shape()

    def set_Shape(self):
        self.rectangle_box.setVisible(True)
        # self.rectangle_box.setVisible(self.shape == 0)

    def get_boundary_shape(self):
        if self.shape == 0:
            # note that wavefront 1d will be clipped using the first two coordinates!
            boundary_shape = Rectangle(x_left=-0.5*self.height + self.vertical_shift,
                                       x_right=0.5*self.height + self.vertical_shift,
                                       y_bottom=-0.5*self.height + self.vertical_shift,
                                       y_top=0.5*self.height + self.vertical_shift)

        return boundary_shape

    def check_data(self):
        super().check_data()

        congruence.checkNumber(self.vertical_shift, "Vertical Shift")
        if self.shape == 0:
            congruence.checkStrictlyPositiveNumber(self.height, "Height")


    def receive_specific_syned_data(self, optical_element):
        if not optical_element is None:
            self.check_syned_instance(optical_element)

            if not optical_element._boundary_shape is None:

                left, right, bottom, top = optical_element._boundary_shape.get_boundaries()

                self.vertical_shift = round(((top + bottom) / 2), 6)

                if isinstance(optical_element._boundary_shape, Rectangle):
                    self.shape = 0

                self.set_Shape()
        else:
            raise Exception("Syned Data not correct: Empty Optical Element")

# --------------------------------------------------------------
#
# class OWWOOpticalElementWithSurfaceShape1D(OWWOOpticalElementWithBoundaryShape):
#
#     # SURFACE
#
#     convexity = Setting(0)
#     is_cylinder = Setting(1)
#     cylinder_direction = Setting(0)
#
#     p_surface = Setting(0.0)
#     q_surface = Setting(0.0)
#
#     calculate_sphere_parameter = Setting(0)
#     calculate_ellipsoid_parameter = Setting(0)
#     calculate_paraboloid_parameter = Setting(0)
#     calculate_hyperboloid_parameter = Setting(0)
#     calculate_torus_parameter = Setting(0)
#
#
#     # SPHERE
#     radius_surface = Setting(0.0)
#
#     # ELLIPSOID/HYPERBOLOID
#     min_ax_surface = Setting(0.0)
#     maj_ax_surface = Setting(0.0)
#
#     # PARABOLOID
#     parabola_parameter_surface = Setting(0.0)
#     at_infinty_surface = Setting(0.0)
#
#     # TORUS
#     min_radius_surface = Setting(0.0)
#     maj_radius_surface = Setting(0.0)
#
#     def draw_specific_box(self, tab_oe):
#
#         super().draw_specific_box()
#
#         self.surface_shape_box = oasysgui.widgetBox(tab_oe, "Surface Shape", addSpace=True, orientation="vertical", height=190)
#
#         gui.comboBox(self.surface_shape_box, self, "surface_shape", label="Surface Shape", labelWidth=350,
#                      items=["Plane", "Sphere", "Ellipsoid", "Paraboloid", "Hyperboloid", "Toroidal"],
#                      callback=self.set_SurfaceParameters,
#                      sendSelectedValue=False, orientation="horizontal")
#
#
#         self.plane_box = oasysgui.widgetBox(self.surface_shape_box, "", addSpace=False, orientation="vertical", height=90)
#
#         self.sphere_box = oasysgui.widgetBox(self.surface_shape_box, "", addSpace=False, orientation="vertical", height=90)
#         self.ellipsoid_box = oasysgui.widgetBox(self.surface_shape_box, "", addSpace=False, orientation="vertical", height=90)
#         self.paraboloid_box = oasysgui.widgetBox(self.surface_shape_box, "", addSpace=False, orientation="vertical", height=115)
#         self.hyperboloid_box = oasysgui.widgetBox(self.surface_shape_box, "", addSpace=False, orientation="vertical", height=90)
#         self.torus_box = oasysgui.widgetBox(self.surface_shape_box, "", addSpace=False, orientation="vertical", height=90)
#
#         # SPHERE --------------------------
#
#         gui.comboBox(self.sphere_box, self, "calculate_sphere_parameter", label="Sphere Shape", labelWidth=350,
#                      items=["Manual", "Automatic"],
#                      callback=self.set_SphereShape,
#                      sendSelectedValue=False, orientation="horizontal")
#
#         self.sphere_box_1 = oasysgui.widgetBox(self.sphere_box, "", addSpace=False, orientation="vertical", height=60)
#         self.sphere_box_2 = oasysgui.widgetBox(self.sphere_box, "", addSpace=False, orientation="vertical", height=60)
#
#         oasysgui.lineEdit(self.sphere_box_1, self, "radius_surface", "Radius [m]", labelWidth=260, valueType=float, orientation="horizontal")
#
#         oasysgui.lineEdit(self.sphere_box_2, self, "p_surface", "First Focus to O.E. Center (P) [m]", labelWidth=260, valueType=float, orientation="horizontal")
#         oasysgui.lineEdit(self.sphere_box_2, self, "q_surface", "O.E. Center to Second Focus (Q) [m]", labelWidth=260, valueType=float, orientation="horizontal")
#
#
#         # ELLIPSOID --------------------------
#
#         gui.comboBox(self.ellipsoid_box, self, "calculate_ellipsoid_parameter", label="Ellipsoid Shape", labelWidth=350,
#                      items=["Manual", "Automatic"],
#                      callback=self.set_EllipsoidShape,
#                      sendSelectedValue=False, orientation="horizontal")
#
#         self.ellipsoid_box_1 = oasysgui.widgetBox(self.ellipsoid_box, "", addSpace=False, orientation="vertical", height=60)
#         self.ellipsoid_box_2 = oasysgui.widgetBox(self.ellipsoid_box, "", addSpace=False, orientation="vertical", height=60)
#
#         oasysgui.lineEdit(self.ellipsoid_box_1, self, "min_ax_surface", "Minor Axis [m]", labelWidth=260, valueType=float, orientation="horizontal")
#         oasysgui.lineEdit(self.ellipsoid_box_1, self, "maj_ax_surface", "Major Axis [m]", labelWidth=260, valueType=float, orientation="horizontal")
#
#         oasysgui.lineEdit(self.ellipsoid_box_2, self, "p_surface", "First Focus to O.E. Center (P) [m]", labelWidth=260, valueType=float, orientation="horizontal")
#         oasysgui.lineEdit(self.ellipsoid_box_2, self, "q_surface", "O.E. Center to Second Focus (Q) [m]", labelWidth=260, valueType=float, orientation="horizontal")
#
#
#         # PARABOLOID --------------------------
#
#         gui.comboBox(self.paraboloid_box, self, "calculate_paraboloid_parameter", label="Sphere Shape", labelWidth=350,
#                      items=["Manual", "Automatic"],
#                      callback=self.set_ParaboloidShape,
#                      sendSelectedValue=False, orientation="horizontal")
#
#         self.paraboloid_box_1 = oasysgui.widgetBox(self.paraboloid_box, "", addSpace=False, orientation="vertical", height=85)
#         self.paraboloid_box_2 = oasysgui.widgetBox(self.paraboloid_box, "", addSpace=False, orientation="vertical", height=85)
#
#         oasysgui.lineEdit(self.paraboloid_box_1, self, "parabola_parameter_surface", "Parabola Parameter [m]", labelWidth=260, valueType=float, orientation="horizontal")
#
#         oasysgui.lineEdit(self.paraboloid_box_2, self, "p_surface", "First Focus to O.E. Center (P) [m]", labelWidth=260, valueType=float, orientation="horizontal")
#         oasysgui.lineEdit(self.paraboloid_box_2, self, "q_surface", "O.E. Center to Second Focus (Q) [m]", labelWidth=260, valueType=float, orientation="horizontal")
#
#         gui.comboBox(self.paraboloid_box_2, self, "at_infinty_surface", label="At infinity", labelWidth=350,
#                      items=["Source", "Image"],
#                      sendSelectedValue=False, orientation="horizontal")
#
#
#         # HYPERBOLOID --------------------------
#
#         gui.comboBox(self.hyperboloid_box, self, "calculate_hyperboloid_parameter", label="Hyperboloid Shape", labelWidth=350,
#                      items=["Manual", "Automatic"],
#                      callback=self.set_HyperboloidShape,
#                      sendSelectedValue=False, orientation="horizontal")
#
#         self.hyperboloid_box_1 = oasysgui.widgetBox(self.hyperboloid_box, "", addSpace=False, orientation="vertical", height=60)
#         self.hyperboloid_box_2 = oasysgui.widgetBox(self.hyperboloid_box, "", addSpace=False, orientation="vertical", height=60)
#
#         oasysgui.lineEdit(self.hyperboloid_box_1, self, "min_ax_surface", "Minor Axis [m]", labelWidth=260, valueType=float, orientation="horizontal")
#         oasysgui.lineEdit(self.hyperboloid_box_1, self, "maj_ax_surface", "Major Axis [m]", labelWidth=260, valueType=float, orientation="horizontal")
#
#         oasysgui.lineEdit(self.hyperboloid_box_2, self, "p_surface", "First Focus to O.E. Center (P) [m]", labelWidth=260, valueType=float, orientation="horizontal")
#         oasysgui.lineEdit(self.hyperboloid_box_2, self, "q_surface", "O.E. Center to Second Focus (Q) [m]", labelWidth=260, valueType=float, orientation="horizontal")
#
#
#         # TORUS --------------------------
#
#         gui.comboBox(self.torus_box, self, "calculate_torus_parameter", label="Torus Shape", labelWidth=350,
#                      items=["Manual", "Automatic"],
#                      callback=self.set_TorusShape,
#                      sendSelectedValue=False, orientation="horizontal")
#
#         self.torus_box_1 = oasysgui.widgetBox(self.torus_box, "", addSpace=False, orientation="vertical", height=60)
#         self.torus_box_2 = oasysgui.widgetBox(self.torus_box, "", addSpace=False, orientation="vertical", height=60)
#
#         oasysgui.lineEdit(self.torus_box_1, self, "min_radius_surface", "Minor radius [m]", labelWidth=260, valueType=float, orientation="horizontal")
#         oasysgui.lineEdit(self.torus_box_1, self, "maj_radius_surface", "Major radius [m]", labelWidth=260, valueType=float, orientation="horizontal")
#
#         oasysgui.lineEdit(self.torus_box_2, self, "p_surface", "First Focus to O.E. Center (P) [m]", labelWidth=260, valueType=float, orientation="horizontal")
#         oasysgui.lineEdit(self.torus_box_2, self, "q_surface", "O.E. Center to Second Focus (Q) [m]", labelWidth=260, valueType=float, orientation="horizontal")
#
#         # -----------------------------------------------------
#         # -----------------------------------------------------
#
#         self.surface_orientation_box = oasysgui.widgetBox(tab_oe, "Surface Orientation", addSpace=False, orientation="vertical")
#
#         gui.comboBox(self.surface_orientation_box, self, "convexity", label="Convexity", labelWidth=350,
#                      items=["Upward", "Downward"],
#                      sendSelectedValue=False, orientation="horizontal")
#
#         gui.comboBox(self.surface_orientation_box, self, "is_cylinder", label="Cylinder", labelWidth=350,
#                      items=["No", "Yes"], callback=self.set_Cylinder,
#                      sendSelectedValue=False, orientation="horizontal")
#
#         self.cylinder_box_1 = oasysgui.widgetBox(self.surface_orientation_box, "", addSpace=False, orientation="vertical", height=25)
#         self.cylinder_box_2 = oasysgui.widgetBox(self.surface_orientation_box, "", addSpace=False, orientation="vertical", height=25)
#
#         gui.comboBox(self.cylinder_box_1, self, "cylinder_direction", label="Cylinder Direction", labelWidth=350,
#                      items=["Tangential", "Sagittal"],
#                      sendSelectedValue=False, orientation="horizontal")
#
#         self.set_SurfaceParameters()
#
#     def set_SphereShape(self):
#         self.sphere_box_1.setVisible(self.calculate_sphere_parameter==0)
#         self.sphere_box_2.setVisible(self.calculate_sphere_parameter==1)
#
#     def set_EllipsoidShape(self):
#         self.ellipsoid_box_1.setVisible(self.calculate_ellipsoid_parameter==0)
#         self.ellipsoid_box_2.setVisible(self.calculate_ellipsoid_parameter==1)
#
#     def set_ParaboloidShape(self):
#         self.paraboloid_box_1.setVisible(self.calculate_paraboloid_parameter==0)
#         self.paraboloid_box_2.setVisible(self.calculate_paraboloid_parameter==1)
#
#     def set_HyperboloidShape(self):
#         self.hyperboloid_box_1.setVisible(self.calculate_hyperboloid_parameter==0)
#         self.hyperboloid_box_2.setVisible(self.calculate_hyperboloid_parameter==1)
#
#     def set_TorusShape(self):
#         self.torus_box_1.setVisible(self.calculate_torus_parameter==0)
#         self.torus_box_2.setVisible(self.calculate_torus_parameter==1)
#
#
#     def set_Cylinder(self):
#         self.cylinder_box_1.setVisible(self.is_cylinder==1)
#         self.cylinder_box_2.setVisible(self.is_cylinder==0)
#
#     def set_SurfaceParameters(self):
#         self.plane_box.setVisible(self.surface_shape == 0)
#
#         if self.surface_shape == 1 :
#             self.sphere_box.setVisible(True)
#             self.set_SphereShape()
#         else:
#             self.sphere_box.setVisible(False)
#
#         if self.surface_shape == 2 :
#             self.ellipsoid_box.setVisible(True)
#             self.set_EllipsoidShape()
#         else:
#             self.ellipsoid_box.setVisible(False)
#
#         if self.surface_shape == 3 :
#             self.paraboloid_box.setVisible(True)
#             self.set_ParaboloidShape()
#         else:
#             self.paraboloid_box.setVisible(False)
#
#         if self.surface_shape == 4 :
#             self.hyperboloid_box.setVisible(True)
#             self.set_HyperboloidShape()
#         else:
#             self.hyperboloid_box.setVisible(False)
#
#         if self.surface_shape == 5 :
#             self.torus_box.setVisible(True)
#             self.set_TorusShape()
#         else:
#             self.torus_box.setVisible(False)
#
#         if self.surface_shape in (1,2,3,4):
#             self.surface_orientation_box.setVisible(True)
#             self.set_Cylinder()
#         else:
#             self.surface_orientation_box.setVisible(False)
#
#     def get_surface_shape(self):
#         if self.surface_shape == 0:
#             surface_shape = Plane()
#
#         # SPHERE --------------------------
#         elif self.surface_shape == 1:
#             if self.calculate_sphere_parameter == 0:
#                 if self.is_cylinder == 0:
#                     surface_shape = Sphere(radius=self.radius_surface,
#                                            convexity=self.convexity)
#                 else:
#                     surface_shape = SphericalCylinder(radius=self.radius_surface,
#                                                       convexity=self.convexity,
#                                                       cylinder_direction=self.cylinder_direction)
#             elif self.calculate_sphere_parameter == 1:
#                 if self.is_cylinder == 0:
#                     surface_shape = Sphere(convexity=self.convexity)
#                 else:
#                     surface_shape = SphericalCylinder(convexity=self.convexity,
#                                                       cylinder_direction=self.cylinder_direction)
#
#                 surface_shape.initialize_from_p_q(self.p_surface, self.q_surface, numpy.radians(90-self.angle_radial))
#
#                 self.radius_surface = round(surface_shape.get_radius(), 6)
#
#         # ELLIPSOID --------------------------
#         elif self.surface_shape == 2:
#             if self.calculate_ellipsoid_parameter == 0:
#                 if self.is_cylinder == 0:
#                     surface_shape = Ellipsoid(min_axis=self.min_ax_surface,
#                                               maj_axis=self.maj_ax_surface,
#                                               convexity=self.convexity)
#                 else:
#                     surface_shape = EllipticalCylinder(min_axis=self.min_ax_surface,
#                                                        maj_axis=self.maj_ax_surface,
#                                                        convexity=self.convexity,
#                                                        cylinder_direction=self.cylinder_direction)
#             elif self.calculate_ellipsoid_parameter == 1:
#                 if self.is_cylinder == 0:
#                     surface_shape = Ellipsoid(convexity=self.convexity)
#                 else:
#                     surface_shape = EllipticalCylinder(convexity=self.convexity,
#                                                        cylinder_direction=self.cylinder_direction)
#
#                 surface_shape.initialize_from_p_q(self.p_surface, self.q_surface, numpy.radians(90-self.angle_radial))
#
#                 self.min_ax_surface = round(surface_shape._min_axis, 6)
#                 self.maj_ax_surface = round(surface_shape._maj_axis, 6)
#
#         # PARABOLOID --------------------------
#         elif self.surface_shape == 3:
#             if self.calculate_paraboloid_parameter == 0:
#                 if self.is_cylinder == 0:
#                     surface_shape = Paraboloid(parabola_parameter=self.parabola_parameter_surface,
#                                                convexity=self.convexity)
#                 else:
#                     surface_shape = ParabolicCylinder(parabola_parameter=self.parabola_parameter_surface,
#                                                       convexity=self.convexity,
#                                                       cylinder_direction=self.cylinder_direction)
#             elif self.calculate_paraboloid_parameter == 1:
#                 if self.is_cylinder == 0:
#                     surface_shape = Paraboloid(convexity=self.convexity)
#                 else:
#                     surface_shape = ParabolicCylinder(convexity=self.convexity,
#                                                     cylinder_direction=self.cylinder_direction)
#
#                 surface_shape.initialize_from_p_q(self.p_surface, self.q_surface, numpy.radians(90-self.angle_radial), at_infinity=self.at_infinty_surface)
#
#                 self.parabola_parameter_surface = round(surface_shape._parabola_parameter, 6)
#
#         # HYPERBOLOID --------------------------
#         elif self.surface_shape == 4:
#             if self.calculate_hyperboloid_parameter == 0:
#                 if self.is_cylinder == 0:
#                     surface_shape = Hyperboloid(min_axis=self.min_ax_surface,
#                                                 maj_axis=self.maj_ax_surface,
#                                                 convexity=self.convexity)
#                 else:
#                     surface_shape = HyperbolicCylinder(min_axis=self.min_ax_surface,
#                                                        maj_axis=self.maj_ax_surface,
#                                                        convexity=self.convexity,
#                                                        cylinder_direction=self.cylinder_direction)
#             elif self.calculate_ellipsoid_parameter == 1:
#                 raise NotImplementedError("HYPERBOLOID, you should not be here!")
#
#         # TORUS --------------------------
#         elif self.surface_shape == 5:
#             if self.calculate_torus_parameter == 0:
#                 surface_shape = Toroidal(min_radius=self.min_radius_surface,
#                                       maj_radius=self.maj_radius_surface)
#             elif self.calculate_torus_parameter == 1:
#                 surface_shape = Toroidal()
#
#                 surface_shape.initialize_from_p_q(self.p_surface, self.q_surface, numpy.radians(90-self.angle_radial))
#
#                 self.min_radius_surface = round(surface_shape._min_radius, 6)
#                 self.maj_radius_surface = round(surface_shape._maj_radius, 6)
#
#
#         return surface_shape
#
#     def check_data(self):
#         super().check_data()
#
#         if self.surface_shape == 1: # SPHERE
#             if self.calculate_sphere_parameter == 0:
#                 congruence.checkStrictlyPositiveNumber(self.radius_surface, "(Surface) Radius")
#             elif self.calculate_sphere_parameter == 1:
#                 congruence.checkStrictlyPositiveNumber(self.p_surface, "(Surface) P")
#
#         if self.surface_shape == 2: # ELLIPSOID
#             if self.calculate_ellipsoid_parameter == 0:
#                 congruence.checkStrictlyPositiveNumber(self.min_ax_surface, "(Surface) Minor Axis")
#                 congruence.checkStrictlyPositiveNumber(self.maj_ax_surface, "(Surface) Major Axis")
#             elif self.calculate_ellipsoid_parameter == 1:
#                 congruence.checkStrictlyPositiveNumber(self.p_surface, "(Surface) P")
#                 congruence.checkStrictlyPositiveNumber(self.q_surface, "(Surface) Q")
#
#                 if self.is_cylinder and self.cylinder_direction == Direction.SAGITTAL:
#                     raise NotImplementedError("Sagittal automatic calculation is not supported, yet")
#
#         if self.surface_shape == 3: # PARABOLOID
#             if self.calculate_paraboloid_parameter == 0:
#                 congruence.checkStrictlyPositiveNumber(self.parabola_parameter_surface, "(Surface) Parabola Parameter")
#             elif self.calculate_paraboloid_parameter == 1:
#                 congruence.checkStrictlyPositiveNumber(self.p_surface, "(Surface) P")
#                 congruence.checkStrictlyPositiveNumber(self.q_surface, "(Surface) Q")
#
#                 if self.is_cylinder and self.cylinder_direction == Direction.SAGITTAL:
#                     raise NotImplementedError("Sagittal automatic calculation is not supported, yet")
#
#         if self.surface_shape == 4: # HYPERBOLOID
#             if self.calculate_hyperboloid_parameter == 0:
#                 congruence.checkStrictlyPositiveNumber(self.min_ax_surface, "(Surface) Minor Axis")
#                 congruence.checkStrictlyPositiveNumber(self.maj_ax_surface, "(Surface) Major Axis")
#             elif self.calculate_hyperboloid_parameter == 1:
#                 raise NotImplementedError("Automatic calculation is not supported, yet")
#
#         if self.surface_shape == 5: # TORUS
#             if self.calculate_torus_parameter == 0:
#                 congruence.checkStrictlyPositiveNumber(self.min_radius_surface, "(Surface) Minor Radius")
#                 congruence.checkStrictlyPositiveNumber(self.maj_radius_surface, "(Surface) Major Radius")
#             elif self.calculate_torus_parameter == 1:
#                 congruence.checkStrictlyPositiveNumber(self.p_surface, "(Surface) P")
#                 congruence.checkStrictlyPositiveNumber(self.q_surface, "(Surface) Q")
#
#     def receive_specific_syned_data(self, optical_element):
#         super().receive_specific_syned_data(optical_element)
#
#         #TODO: check and passage of shapes
#
#         raise NotImplementedError()

