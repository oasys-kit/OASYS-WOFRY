#TODO: this widget is valid for 1D and 2D wavefronts. Is there a better way to discriminate without duplicating widgets?

import os
import h5py
from PyQt5.QtWidgets import QMessageBox

try:
    from silx.gui.dialog.DataFileDialog import DataFileDialog
except:
    print("Fail to import silx.gui.dialog.DataFileDialog: need silx >= 0.7")

from orangewidget import gui,widget
from orangewidget.settings import Setting
from oasys.widgets import gui as oasysgui, congruence
from oasys.widgets import widget as oasyswidget

from wofry.propagator.wavefront2D.generic_wavefront import GenericWavefront2D
from wofry.propagator.wavefront1D.generic_wavefront import GenericWavefront1D

from orangecontrib.wofry.util.wofry_objects import WofryData

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
    data_path = Setting("")

    outputs = [{"name":"WofryData2D",
                "type":WofryData,
                "doc":"WofryData2D",
                "id":"WofryData2D"},
               {"name": "WofryData1D",
                "type": WofryData,
                "doc": "WofryData1D",
                "id": "WofryData1D"},
               ]

    def __init__(self):
        super().__init__()

        self.runaction = widget.OWAction("Read Wavefront hdf5 File", self)
        self.runaction.triggered.connect(self.read_file)
        self.addAction(self.runaction)

        self.setFixedWidth(590)
        self.setFixedHeight(250)

        left_box_1 = oasysgui.widgetBox(self.controlArea, "HDF5 Local File Selection", addSpace=True,
                                        orientation="vertical",width=570, height=100)

        figure_box = oasysgui.widgetBox(left_box_1, "", addSpace=True, orientation="vertical", width=550, height=50)

        self.le_file_name = oasysgui.lineEdit(figure_box, self, "file_name", "File Name",
                                                    labelWidth=190, valueType=str, orientation="horizontal")
        self.le_file_name.setFixedWidth(360)

        self.le_data_path = oasysgui.lineEdit(figure_box, self, "data_path", "Group (wavefront name)",
                                                    labelWidth=190, valueType=str, orientation="horizontal")
        self.le_data_path.setFixedWidth(360)

        gui.separator(left_box_1, height=20)

        button = gui.button(self.controlArea, self, "Browse File and Send Data", callback=self.read_file)
        button.setFixedHeight(45)
        gui.separator(self.controlArea, height=20)
        button = gui.button(self.controlArea, self, "Send Data", callback=self.send_data)
        button.setFixedHeight(45)

        gui.rubber(self.controlArea)


    def read_file(self):

        dialog = DataFileDialog(self)
        dialog.setFilterMode(DataFileDialog.FilterMode.ExistingGroup)

        path, filename = os.path.split(self.file_name)
        print("Setting path: ",path)
        dialog.setDirectory(path)

        # Execute the dialog as modal
        result = dialog.exec_()
        if result:
            print("Selection:")
            print(dialog.selectedFile())
            print(dialog.selectedUrl())
            print(dialog.selectedDataUrl().data_path())
            self.file_name = dialog.selectedFile()
            self.data_path = dialog.selectedDataUrl().data_path()
            self.send_data()

    def send_data(self):
        try:
            congruence.checkEmptyString(self.file_name, "File Name")
            congruence.checkFile(self.file_name)

            # get wavefront dimension
            f = h5py.File(self.file_name, 'r')
            dimension = f[self.data_path+"/wfr_dimension"].value
            f.close()
            if dimension == 1:
                wfr = GenericWavefront1D.load_h5_file(self.file_name,self.data_path)
                print(">>> sending 1D wavefront")
                self.send("WofryData1D", WofryData(wavefront=wfr))
            elif dimension == 2:
                wfr = GenericWavefront2D.load_h5_file(self.file_name,self.data_path)
                print(">>> sending 2D wavefront")
                self.send("WofryData2D", WofryData(wavefront=wfr))
            else:
                raise Exception("Invalid wavefront dimension")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e.args[0]), QMessageBox.Ok)

            if self.IS_DEVELOP:raise e

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys

    a = QApplication(sys.argv)
    ow = OWWavefrontFileReader()
    # ow.file_name = "/Users/srio/OASYS_DMG/srw-scripts/hdf5/tmp_wofry.h5"
    # ow.data_path = "/wfr2"
    ow.file_name = "/Users/srio/OASYS_DMG/srw-scripts/hdf5/tmp.h5"
    ow.data_path = "/wfr1"
    ow.show()
    a.exec_()

