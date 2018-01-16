from PyQt5.QtWidgets import QMessageBox

from orangewidget import gui,widget
from orangewidget.settings import Setting
from oasys.widgets import gui as oasysgui, congruence
from oasys.widgets import widget as oasyswidget


from wofry.propagator.wavefront2D.generic_wavefront import GenericWavefront2D
from wofry.propagator.wavefront1D.generic_wavefront import GenericWavefront1D

# from syned.storage_ring.light_source import LightSource
# from syned.beamline.beamline import Beamline
# from syned.util.json_tools import load_from_json_file, load_from_json_url

class OWWavefrontFileReader(oasyswidget.OWWidget):
    name = "Generic Wavefront File Reader"
    description = "Utility: Wofry Wavefront File Reader"
    icon = "icons/file_reader.png"
    maintainer = "Manuel Sanchez del Rio"
    maintainer_email = "srio(@at@)esrf.eu"
    priority = 5
    category = "Utility"
    keywords = ["data", "file", "load", "read"]

    want_main_area = 0

    file_name = Setting("")

    outputs = [{"name":"GenericWavefront2D",
                "type":GenericWavefront2D,
                "doc":"GenericWavefront2D",
                "id":"data"}]


    def __init__(self):
        super().__init__()

        self.runaction = widget.OWAction("Read Wavefront hdf5 File", self)
        self.runaction.triggered.connect(self.read_file)
        self.addAction(self.runaction)

        self.setFixedWidth(590)
        self.setFixedHeight(150)

        left_box_1 = oasysgui.widgetBox(self.controlArea, "HDF5 Local File Selection", addSpace=True,
                                        orientation="vertical",width=570, height=60)

        figure_box = oasysgui.widgetBox(left_box_1, "", addSpace=True, orientation="horizontal", width=550, height=50)

        self.le_file_name = oasysgui.lineEdit(figure_box, self, "file_name", "HDF5 File Name",
                                                    labelWidth=190, valueType=str, orientation="horizontal")
        self.le_file_name.setFixedWidth(260)

        gui.button(figure_box, self, "...", callback=self.selectFile)

        gui.separator(left_box_1, height=20)

        button = gui.button(self.controlArea, self, "Read File", callback=self.read_file)
        button.setFixedHeight(45)

        gui.rubber(self.controlArea)

    def selectFile(self):
        self.le_file_name.setText(oasysgui.selectFileFromDialog(self, self.file_name, "Open File"))

    def read_file(self):
        self.setStatusMessage("")

        try:
            congruence.checkEmptyString(self.file_name, "File Name")
            congruence.checkFile(self.file_name)

            wfr = GenericWavefront2D.load_h5_file(self.file_name,prefix="")

            print(">>>>>> sending Wavefront")
            self.send("GenericWavefront2D", wfr)


        except Exception as e:
            QMessageBox.critical(self, "Error", str(e.args[0]), QMessageBox.Ok)

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys

    a = QApplication(sys.argv)
    ow = OWWavefrontFileReader()
    ow.file_name = "/users/srio/Working/paper-hierarchical/CODE-SRW/tmp.h5"
    ow.show()
    a.exec_()

