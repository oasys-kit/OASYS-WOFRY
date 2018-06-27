from orangewidget.settings import Setting
from orangecontrib.wofry.widgets.gui.ow_optical_element import OWWOOpticalElementWithBoundaryShape

from syned.beamline.optical_elements.absorbers.slit import Slit

from wofry.beamline.optical_elements.absorbers.slit import WOSlit

class OWWOSlit(OWWOOpticalElementWithBoundaryShape):

    name = "Slit"
    description = "Wofry: Slit"
    icon = "icons/slit.png"
    priority = 41

    horizontal_shift = Setting(0.0)
    vertical_shift = Setting(0.0)

    width = Setting(1.0)
    height = Setting(1.0)

    def __init__(self):
        super().__init__()

    def get_optical_element(self):
        return WOSlit(boundary_shape=self.get_boundary_shape())

    def get_optical_element_python_code(self):
        txt = self.get_boundary_shape_python_code()
        txt += "\n"
        txt += "from wofry.beamline.optical_elements.absorbers.slit import WOSlit"
        txt += "\n"
        txt += "optical_element = WOSlit(boundary_shape=boundary_shape)"
        txt += "\n"
        return txt


    def check_syned_instance(self, optical_element):
        if not isinstance(optical_element, Slit):
            raise Exception("Syned Data not correct: Optical Element is not a Slit")


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    from wofry.propagator.wavefront2D.generic_wavefront import GenericWavefront2D

    a = QApplication(sys.argv)
    ow = OWWOSlit()
    ow.input_wavefront = GenericWavefront2D.initialize_wavefront_from_range(-0.002,0.002,-0.001,0.001,(200,200))

    ow.show()
    a.exec_()
    ow.saveSettings()