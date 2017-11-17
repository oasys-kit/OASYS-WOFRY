import numpy

from orangewidget import gui
from orangewidget.settings import Setting
from oasys.widgets import gui as oasysgui
from oasys.widgets import congruence

from orangecontrib.wofry.widgets.gui.ow_optical_element_1d import OWWOOpticalElementWithBoundaryShape1D
from orangecontrib.wofry.widgets.gui.ow_optical_element_1d import OWWOOpticalElement1D
from syned.beamline.optical_elements.absorbers.slit import Slit
from syned.beamline.shape import Rectangle, Ellipse

from wofry.beamline.optical_elements.absorbers.slit import WOSlit1D

class OWWOSlit1D(OWWOOpticalElementWithBoundaryShape1D):

    name = "Slit 1D"
    description = "Wofry: Slit 1D"
    icon = "icons/slit1d.png"
    priority = 3

    vertical_shift = Setting(0.0)

    height = Setting(0.0)
    radius = Setting(0.0)

    def __init__(self):
        super().__init__()

    def get_optical_element(self):
        return WOSlit1D(boundary_shape=self.get_boundary_shape())

    def check_syned_instance(self, optical_element):
        if not isinstance(optical_element, Slit):
            raise Exception("Syned Data not correct: Optical Element is not a Slit")

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    a = QApplication(sys.argv)
    ow = OWWOSlit1D()

    ow.show()
    a.exec_()
    ow.saveSettings()