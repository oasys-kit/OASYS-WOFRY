from orangewidget.settings import Setting
from oasys.widgets import gui as oasysgui
from oasys.widgets import congruence

from syned.beamline.optical_elements.ideal_elements.lens import IdealLens

from wofry.beamline.optical_elements.ideal_elements.lens import WOIdealLens

from orangecontrib.wofry.widgets.gui.ow_optical_element_1d import OWWOOpticalElement1D


class OWWOIdealLens1D(OWWOOpticalElement1D):

    name = "Ideal Lens 1D"
    description = "Wofry: Ideal Lens 1D"
    icon = "icons/ideallens_1d.png"
    priority = 23

    focal_x = Setting(0.0)

    def __init__(self):
        super().__init__()

    def draw_specific_box(self):

        self.filter_box = oasysgui.widgetBox(self.tab_bas, "Ideal Lens Setting", addSpace=True, orientation="vertical")

        oasysgui.lineEdit(self.filter_box, self, "focal_x", "Horizontal Focal Length [m]", labelWidth=260, valueType=float, orientation="horizontal")


    def get_optical_element(self):
        return WOIdealLens(name=self.oe_name,
                           focal_x=self.focal_x,
                           focal_y=None)

    def get_optical_element_python_code(self):
        txt  = ""
        txt += "\nfrom wofry.beamline.optical_elements.ideal_elements.lens import WOIdealLens"
        txt += "\n"
        txt += "\noptical_element = WOIdealLens(name='%s',focal_x=%f,focal_y=None)"%(self.oe_name,self.focal_x)
        txt += "\n"
        return txt

    def check_data(self):
        super().check_data()

        congruence.checkStrictlyPositiveNumber(self.focal_x, "Horizontal Focal Length")


    def receive_specific_syned_data(self, optical_element):
        if not optical_element is None:
            if isinstance(optical_element, IdealLens):
                self.focal_x = optical_element._focal_x
            else:
                raise Exception("Syned Data not correct: Optical Element is not a Slit")
        else:
            raise Exception("Syned Data not correct: Empty Optical Element")

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    a = QApplication(sys.argv)
    ow = OWWOIdealLens1D()

    ow.show()
    a.exec_()
    ow.saveSettings()
