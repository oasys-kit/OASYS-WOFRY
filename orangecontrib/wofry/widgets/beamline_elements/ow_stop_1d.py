import numpy

from orangewidget import gui
from orangewidget.settings import Setting
from oasys.widgets import gui as oasysgui
from oasys.widgets import congruence

from orangecontrib.wofry.widgets.gui.ow_optical_element_1d import OWWOOpticalElementWithBoundaryShape1D
from orangecontrib.wofry.widgets.gui.ow_optical_element_1d import OWWOOpticalElement1D
from syned.beamline.optical_elements.absorbers.beam_stopper import BeamStopper
from syned.beamline.shape import Rectangle, Ellipse

from wofry.beamline.optical_elements.absorbers.beam_stopper import WOBeamStopper1D

class OWWOStop1D(OWWOOpticalElementWithBoundaryShape1D):

    name = "BeamStopper 1D"
    description = "Wofry: BeamStopper 1D"
    icon = "icons/stop1d.png"
    priority = 22

    vertical_shift = Setting(0.0)

    height = Setting(0.0001)

    def __init__(self):
        super().__init__()

    def get_optical_element(self):
        return WOBeamStopper1D(boundary_shape=self.get_boundary_shape())

    def check_syned_instance(self, optical_element):
        if not isinstance(optical_element, BeamStopper):
            raise Exception("Syned Data not correct: Optical Element is not a BeamStopper")


    # overwrite this method to adapt labels
    def draw_specific_box(self):
        self.shape_box = oasysgui.widgetBox(self.tab_bas, "Boundary Shape", addSpace=True, orientation="vertical")

        oasysgui.lineEdit(self.shape_box, self, "vertical_shift", "Shift [m]", labelWidth=260, valueType=float, orientation="horizontal")

        self.rectangle_box = oasysgui.widgetBox(self.shape_box, "", addSpace=False, orientation="vertical", height=60)

        oasysgui.lineEdit(self.rectangle_box, self, "height", "Obstruction [m]", labelWidth=260, valueType=float, orientation="horizontal")

        self.circle_box = oasysgui.widgetBox(self.shape_box, "", addSpace=False, orientation="vertical", height=60)

        self.set_Shape()

    def get_optical_element(self):
        return WOBeamStopper1D(boundary_shape=self.get_boundary_shape())

    def get_optical_element_python_code(self):
        txt = self.get_boundary_shape_python_code()
        txt += "\n"
        txt += "from wofry.beamline.optical_elements.absorbers.beam_stopper import WOBeamStopper1D"
        txt += "\n"
        txt += "optical_element = WOBeamStopper1D(boundary_shape=boundary_shape)"
        txt += "\n"
        return txt

    def check_syned_instance(self, optical_element):
        if not isinstance(optical_element, BeamStopper):
            raise Exception("Syned Data not correct: Optical Element is not a BeamStopper")

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    from wofry.propagator.wavefront1D.generic_wavefront import GenericWavefront1D

    a = QApplication(sys.argv)
    ow = OWWOStop1D()
    ow.input_wavefront = GenericWavefront1D.initialize_wavefront_from_range(-0.001,0.001,5000)
    ow.input_wavefront.set_spherical_wave(-50.0)

    ow.show()
    a.exec_()
    ow.saveSettings()
