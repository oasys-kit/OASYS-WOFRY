from orangewidget.settings import Setting
from orangecontrib.wofry.widgets.gui.ow_optical_element import OWWOOpticalElementWithDoubleBoundaryShape

from syned.beamline.optical_elements.absorbers.slit import Slit

from wofry.beamline.optical_elements.absorbers.slit import WOSlit

class OWWODoubleSlit(OWWOOpticalElementWithDoubleBoundaryShape):

    name = "DoubleSlit"
    description = "Wofry: DoubleSlit"
    icon = "icons/double_slit.png"
    priority = 42

    # horizontal_shift = Setting(0.0)
    # vertical_shift = Setting(0.0)
    #
    # width = Setting(1e-3)
    # height = Setting(1e-4)

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
    import numpy
    import sys
    from PyQt5.QtWidgets import QApplication
    from wofry.propagator.wavefront2D.generic_wavefront import GenericWavefront2D

    a = QApplication(sys.argv)
    ow = OWWODoubleSlit()
    ow.input_wavefront = GenericWavefront2D.initialize_wavefront_from_range(-0.0003,0.0003,-0.0001,0.0001,(1000,500))
    ca = numpy.ones(ow.input_wavefront.size())
    ow.input_wavefront.set_complex_amplitude(ca+0j)


    ow.horizontal_shift = -50e-6
    ow.vertical_shift = -25e-6

    ow.width = 5e-6
    ow.height = 5e-6

    ow.radius = 5e-6

    ow.min_ax = 5e-6
    ow.maj_ax = 5e-6

    # the same for patch 2
    ow.horizontal_shift2 = 50e-6
    ow.vertical_shift2 = 25e-6

    ow.width2 = 5e-6
    ow.height2 = 5e-6

    ow.radius2 = 5e-6

    ow.min_ax2 = 5e-6
    ow.maj_ax2 = 5e-6

    # from srxraylib.plot.gol import plot_image
    # plot_image(ow.input_wavefront.get_intensity())

    ow.show()
    a.exec_()
    ow.saveSettings()