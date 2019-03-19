from orangecontrib.wofry.widgets.gui.ow_optical_element_1d import OWWOOpticalElement1D
from syned.beamline.optical_elements.ideal_elements.screen import Screen


from wofry.beamline.optical_elements.ideal_elements.screen import WOScreen1D

class OWWOScreen1D(OWWOOpticalElement1D):

    name = "Screen 1D"
    description = "Wofry: Screen 1D"
    icon = "icons/screen1d.png"
    priority = 20


    def __init__(self):
        super().__init__()

    def get_optical_element(self):
        return WOScreen1D()

    def get_optical_element_python_code(self):
        txt  = ""
        txt += "\nfrom wofry.beamline.optical_elements.ideal_elements.screen import WOScreen1D"
        txt += "\n"
        txt += "\noptical_element = WOScreen1D()"
        txt += "\n"
        return txt

    def check_syned_instance(self, optical_element):
        if not isinstance(optical_element, Screen):
            raise Exception("Syned Data not correct: Optical Element is not a Screen")

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    from wofry.propagator.wavefront1D.generic_wavefront import GenericWavefront1D

    a = QApplication(sys.argv)
    ow = OWWOScreen1D()
    ow.input_wavefront = GenericWavefront1D.initialize_wavefront_from_range(-0.001,0.001,500)
    ow.show()
    a.exec_()
    ow.saveSettings()