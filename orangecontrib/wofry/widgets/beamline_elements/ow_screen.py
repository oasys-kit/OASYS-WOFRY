from orangewidget.settings import Setting

from orangecontrib.wofry.widgets.gui.ow_optical_element import OWWOOpticalElement

from syned.beamline.optical_elements.ideal_elements.screen import Screen

from wofry.beamline.optical_elements.ideal_elements.screen import WOScreen

class OWWOScreen(OWWOOpticalElement):

    name = "Screen"
    description = "Wofry: Slit"
    icon = "icons/screen.png"
    priority = 40

    horizontal_shift = Setting(0.0)
    vertical_shift = Setting(0.0)

    width = Setting(0.0)
    height = Setting(0.0)

    def __init__(self):
        super().__init__()

    def get_optical_element(self):
        return WOScreen()

    def get_optical_element_python_code(self):
        txt  = ""
        txt += "\nfrom wofry.beamline.optical_elements.ideal_elements.screen import WOScreen"
        txt += "\n"
        txt += "\noptical_element = WOScreen()"
        txt += "\n"
        return txt

    def check_syned_instance(self, optical_element):
        if not isinstance(optical_element, Screen):
            raise Exception("Syned Data not correct: Optical Element is not a Screen")

    def receive_specific_syned_data(self, optical_element):
        pass