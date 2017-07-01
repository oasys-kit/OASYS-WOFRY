import numpy

from orangewidget import gui
from orangewidget.settings import Setting
from oasys.widgets import gui as oasysgui
from oasys.widgets import congruence

from orangecontrib.wofry.widgets.gui.ow_optical_element import OWWOOpticalElement

from syned.beamline.optical_elements.absorbers.slit import Slit
from syned.beamline.shape import Rectangle, Ellipse

from wofry.elements.optical_elements.absorbers.slit import WOSlit

class OWWOSlit(OWWOOpticalElement):

    name = "Slit"
    description = "Wofry: Slit"
    icon = "icons/slit.png"
    priority = 2

    horizontal_shift = Setting(0.0)
    vertical_shift = Setting(0.0)

    width = Setting(0.0)
    height = Setting(0.0)
    radius = Setting(0.0)

    def __init__(self):
        super().__init__()


    def draw_specific_box(self):

        self.shape_box = oasysgui.widgetBox(self.tab_bas, "Shape", addSpace=True, orientation="vertical")

        gui.comboBox(self.shape_box, self, "shape", label="Slit Shape", labelWidth=350,
                     items=["Rectangle", "Circle"],
                     callback=self.set_Shape,
                     sendSelectedValue=False, orientation="horizontal")

        oasysgui.lineEdit(self.shape_box, self, "horizontal_shift", "Horizontal Shift [m]", labelWidth=260, valueType=float, orientation="horizontal")
        oasysgui.lineEdit(self.shape_box, self, "vertical_shift", "Vertical Shift [m]", labelWidth=260, valueType=float, orientation="horizontal")

        self.rectangle_box = oasysgui.widgetBox(self.shape_box, "", addSpace=False, orientation="vertical", height=60)

        oasysgui.lineEdit(self.rectangle_box, self, "width", "Width [m]", labelWidth=260, valueType=float, orientation="horizontal")
        oasysgui.lineEdit(self.rectangle_box, self, "height", "Height [m]", labelWidth=260, valueType=float, orientation="horizontal")

        self.circle_box = oasysgui.widgetBox(self.shape_box, "", addSpace=False, orientation="vertical", height=60)

        oasysgui.lineEdit(self.circle_box, self, "radius", "Radius [m]", labelWidth=260, valueType=float, orientation="horizontal")

        self.set_Shape()

    def set_Shape(self):
        self.rectangle_box.setVisible(self.shape == 0)
        self.circle_box.setVisible(self.shape == 1)

    def get_optical_element(self):

        if self.shape == 0:
            boundary_shape = Rectangle(x_left=-0.5*self.width + self.horizontal_shift,
                                       x_right=0.5*self.width + self.horizontal_shift,
                                       y_bottom=-0.5*self.height + self.vertical_shift,
                                       y_top=0.5*self.height + self.vertical_shift)

        elif self.shape == 1:
            boundary_shape = Ellipse(min_ax_left=-0.5*self.radius + self.horizontal_shift,
                                     min_ax_right=0.5*self.radius + self.horizontal_shift,
                                     maj_ax_left=-0.5*self.radius + self.vertical_shift,
                                     maj_ax_right=0.5*self.radius + self.vertical_shift)

        return WOSlit(boundary_shape=boundary_shape)

    def check_data(self):
        super().check_data()

        congruence.checkNumber(self.horizontal_shift, "Horizontal Shift")
        congruence.checkNumber(self.vertical_shift, "Vertical Shift")

        if self.shape == 0:
            congruence.checkStrictlyPositiveNumber(self.width, "Width")
            congruence.checkStrictlyPositiveNumber(self.height, "Height")
        elif self.shape == 1:
            congruence.checkStrictlyPositiveNumber(self.radius, "Radius")


    def receive_specific_syned_data(self, optical_element):
        if not optical_element is None:
            if isinstance(optical_element, Slit):
                if isinstance(optical_element._boundary_shape, Rectangle):
                    self.shape = 0

                    self.width  = numpy.abs(optical_element._boundary_shape._x_right - optical_element._boundary_shape._x_left)
                    self.height = numpy.abs(optical_element._boundary_shape._y_top - optical_element._boundary_shape._y_bottom)
                    self.horizontal_shift = optical_element._boundary_shape._x_left + 0.5*self.width
                    self.vertical_shift = optical_element._boundary_shape._y_bottom + 0.5*self.height

                if isinstance(optical_element._boundary_shape, Ellipse):
                    self.shape = 1

                    self.radius  = 0.5*(numpy.abs(optical_element._boundary_shape._min_ax_right - optical_element._boundary_shape._min_ax_left) +
                                        numpy.abs(optical_element._boundary_shape._maj_ax_top - optical_element._boundary_shape._maj_ax_bottom))

                    self.horizontal_shift = optical_element._boundary_shape._min_ax_left + 0.5*self.radius
                    self.vertical_shift = optical_element._boundary_shape._maj_ax_bottom + 0.5*self.radius

            else:
                raise Exception("Syned Data not correct: Optical Element is not a Slit")
        else:
            raise Exception("Syned Data not correct: Empty Optical Element")