import numpy

from orangewidget import gui
from orangewidget.settings import Setting
from oasys.widgets import gui as oasysgui
from oasys.widgets import congruence

from orangecontrib.wofry.widgets.gui.ow_optical_element import OWWOOpticalElementWithBoundaryShape

from syned.beamline.optical_elements.absorbers.beam_stopper import BeamStopper
from syned.beamline.shape import Rectangle, Ellipse

from wofry.beamline.optical_elements.absorbers.beam_stopper import WOBeamStopper

class OWWOStop(OWWOOpticalElementWithBoundaryShape):

    name = "BeamStopper"
    description = "Wofry: BeamStopper"
    icon = "icons/stop.png"
    priority = 42

    horizontal_shift = Setting(0.0)
    vertical_shift = Setting(0.0)

    width = Setting(0.0002)
    height = Setting(0.0001)

    def __init__(self):
        super().__init__()

    def get_optical_element(self):
        return WOBeamStopper(boundary_shape=self.get_boundary_shape())

    def get_optical_element_python_code(self):
        txt = self.get_boundary_shape_python_code()
        txt += "\n"
        txt += "from wofry.beamline.optical_elements.absorbers.beam_stopper import WOBeamStopper"
        txt += "\n"
        txt += "optical_element = WOBeamStopper(boundary_shape=boundary_shape)"
        txt += "\n"
        return txt


    def check_syned_instance(self, optical_element):
        if not isinstance(optical_element, BeamStopper):
            raise Exception("Syned Data not correct: Optical Element is not a BeamStopper")


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    from wofry.propagator.wavefront2D.generic_wavefront import GenericWavefront2D

    a = QApplication(sys.argv)
    ow = OWWOStop()
    ow.input_wavefront = GenericWavefront2D.initialize_wavefront_from_range(-0.002,0.002,-0.001,0.001,(200,200))

    ow.show()
    a.exec_()
    ow.saveSettings()
