import numpy

from orangewidget import gui
from orangewidget.settings import Setting
from oasys.widgets import gui as oasysgui
from oasys.widgets import congruence

from orangecontrib.wofry.widgets.gui.ow_optical_element import OWWOOpticalElementWithBoundaryShape

from syned.beamline.optical_elements.absorbers.slit import Slit
from syned.beamline.shape import Rectangle, Ellipse

from wofry.beamline.optical_elements.absorbers.slit import WOSlit

class OWWOSlit(OWWOOpticalElementWithBoundaryShape):

    name = "Slit"
    description = "Wofry: Slit"
    icon = "icons/slit.png"
    priority = 2

    horizontal_shift = Setting(0.0)
    vertical_shift = Setting(0.0)

    width = Setting(0.0)
    height = Setting(0.0)

    def __init__(self):
        super().__init__()

    def get_optical_element(self):
        return WOSlit(boundary_shape=self.get_boundary_shape())

    def check_syned_instance(self, optical_element):
        if not isinstance(optical_element, Slit):
            raise Exception("Syned Data not correct: Optical Element is not a Slit")
