import sys, numpy
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPalette, QColor, QFont

from orangewidget import widget, gui
from oasys.widgets import gui as oasysgui
from orangewidget.settings import Setting
from oasys.widgets.widget import OWWidget

from orangecontrib.wofry.util.wofry_objects import WofryData

class OWWOMerge(OWWidget):

    name = "Merge Wofry Data"
    description = "Display Data: Merge Wofry Data"
    icon = "icons/merge.png"
    maintainer = "M Sanchez del Rio"
    maintainer_email = "srio(@at@)esrf.eu"
    priority = 400
    category = "Wofry Tools"
    keywords = ["WodryData", "file"]

    inputs = [("Input WofryData # 1" , WofryData, "setBeam1" ),
              ("Input WofryData # 2" , WofryData, "setBeam2" ),
              ("Input WofryData # 3" , WofryData, "setBeam3" ),
              ("Input WofryData # 4" , WofryData, "setBeam4" ),
              ("Input WofryData # 5" , WofryData, "setBeam5" ),
              ("Input WofryData # 6" , WofryData, "setBeam6" ),
              ("Input WofryData # 7" , WofryData, "setBeam7" ),
              ("Input WofryData # 8" , WofryData, "setBeam8" ),
              ("Input WofryData # 9" , WofryData, "setBeam9" ),
              ("Input WofryData # 10", WofryData, "setBeam10"),]

    outputs = [{"name":"WofryData",
                "type":WofryData,
                "doc":"WofryData",
                "id":"WofryData"}]

    want_main_area=0
    want_control_area = 1

    input_beam1=None
    input_beam2=None
    input_beam3=None
    input_beam4=None
    input_beam5=None
    input_beam6=None
    input_beam7=None
    input_beam8=None
    input_beam9=None
    input_beam10=None

    use_weights = Setting(0)

    weight_input_beam1=Setting(1.0)
    weight_input_beam2=Setting(1.0)
    weight_input_beam3=Setting(1.0)
    weight_input_beam4=Setting(1.0)
    weight_input_beam5=Setting(1.0)
    weight_input_beam6=Setting(1.0)
    weight_input_beam7=Setting(1.0)
    weight_input_beam8=Setting(1.0)
    weight_input_beam9=Setting(1.0)
    weight_input_beam10=Setting(1.0)

    phase_input_beam1=Setting(0.0)
    phase_input_beam2=Setting(0.0)
    phase_input_beam3=Setting(0.0)
    phase_input_beam4=Setting(0.0)
    phase_input_beam5=Setting(0.0)
    phase_input_beam6=Setting(0.0)
    phase_input_beam7=Setting(0.0)
    phase_input_beam8=Setting(0.0)
    phase_input_beam9=Setting(0.0)
    phase_input_beam10=Setting(0.0)

    def __init__(self, show_automatic_box=True):
        super().__init__()

        self.runaction = widget.OWAction("Merge Beams", self)
        self.runaction.triggered.connect(self.merge_beams)
        self.addAction(self.runaction)

        self.setFixedWidth(470)
        self.setFixedHeight(470)

        gen_box = gui.widgetBox(self.controlArea, "Merge Shadow Beams", addSpace=True, orientation="vertical")

        button_box = oasysgui.widgetBox(gen_box, "", addSpace=False, orientation="horizontal")

        button = gui.button(button_box, self, "Merge Beams and Send", callback=self.merge_beams)
        font = QFont(button.font())
        font.setBold(True)
        button.setFont(font)
        palette = QPalette(button.palette()) # make a copy of the palette
        palette.setColor(QPalette.ButtonText, QColor('Dark Blue'))
        button.setPalette(palette) # assign new palette
        button.setFixedHeight(45)

        weight_box = oasysgui.widgetBox(gen_box, "Relative Weights and Phases", addSpace=False, orientation="vertical")

        gui.comboBox(weight_box, self, "use_weights", label="Use Relative Weights and Phases?", labelWidth=350,
                     items=["No", "Yes"],
                     callback=self.set_UseWeights, sendSelectedValue=False, orientation="horizontal")

        gui.separator(weight_box, height=10)

        self.le_weight_input_beam1 = oasysgui.lineEdit(weight_box, self, "weight_input_beam1", "Input Beam 1 weight",
                                                    labelWidth=300, valueType=float, orientation="horizontal")
        self.le_phase_input_beam1 = oasysgui.lineEdit(weight_box, self, "phase_input_beam1", "Input Beam 1 add phase [rad]",
                                                    labelWidth=300, valueType=float, orientation="horizontal")
        gui.separator(weight_box, height=10)

        self.le_weight_input_beam2 = oasysgui.lineEdit(weight_box, self, "weight_input_beam2", "Input Beam 2 weight",
                                                    labelWidth=300, valueType=float, orientation="horizontal")
        self.le_phase_input_beam2 = oasysgui.lineEdit(weight_box, self, "phase_input_beam2", "Input Beam 2 add phase [rad]",
                                                    labelWidth=300, valueType=float, orientation="horizontal")
        gui.separator(weight_box, height=10)

        self.le_weight_input_beam3 = oasysgui.lineEdit(weight_box, self, "weight_input_beam3", "Input Beam 3 weight",
                                                    labelWidth=300, valueType=float, orientation="horizontal")
        self.le_phase_input_beam3 = oasysgui.lineEdit(weight_box, self, "phase_input_beam3", "Input Beam 3 add phase [rad]",
                                                    labelWidth=300, valueType=float, orientation="horizontal")
        gui.separator(weight_box, height=10)

        self.le_weight_input_beam4 = oasysgui.lineEdit(weight_box, self, "weight_input_beam4", "Input Beam 4 weight",
                                                    labelWidth=300, valueType=float, orientation="horizontal")
        self.le_phase_input_beam4 = oasysgui.lineEdit(weight_box, self, "phase_input_beam4", "Input Beam 4 add phase [rad]",
                                                    labelWidth=300, valueType=float, orientation="horizontal")
        gui.separator(weight_box, height=10)

        self.le_weight_input_beam5 = oasysgui.lineEdit(weight_box, self, "weight_input_beam5", "Input Beam 5 weight",
                                                    labelWidth=300, valueType=float, orientation="horizontal")
        self.le_phase_input_beam5 = oasysgui.lineEdit(weight_box, self, "phase_input_beam5", "Input Beam 5 add phase [rad]",
                                                    labelWidth=300, valueType=float, orientation="horizontal")
        gui.separator(weight_box, height=10)

        self.le_weight_input_beam6 = oasysgui.lineEdit(weight_box, self, "weight_input_beam6", "Input Beam 6 weight",
                                                    labelWidth=300, valueType=float, orientation="horizontal")
        self.le_phase_input_beam6 = oasysgui.lineEdit(weight_box, self, "phase_input_beam6", "Input Beam 6 add phase [rad]",
                                                    labelWidth=300, valueType=float, orientation="horizontal")
        gui.separator(weight_box, height=10)

        self.le_weight_input_beam7 = oasysgui.lineEdit(weight_box, self, "weight_input_beam7", "Input Beam 7 weight",
                                                    labelWidth=300, valueType=float, orientation="horizontal")
        self.le_phase_input_beam7 = oasysgui.lineEdit(weight_box, self, "phase_input_beam7", "Input Beam 7 add phase [rad]",
                                                    labelWidth=300, valueType=float, orientation="horizontal")
        gui.separator(weight_box, height=10)

        self.le_weight_input_beam8 = oasysgui.lineEdit(weight_box, self, "weight_input_beam8", "Input Beam 8 weight",
                                                    labelWidth=300, valueType=float, orientation="horizontal")
        self.le_phase_input_beam8 = oasysgui.lineEdit(weight_box, self, "phase_input_beam8", "Input Beam 8 add phase [rad]",
                                                    labelWidth=300, valueType=float, orientation="horizontal")
        gui.separator(weight_box, height=10)

        self.le_weight_input_beam9 = oasysgui.lineEdit(weight_box, self, "weight_input_beam9", "Input Beam 9 weight",
                                                    labelWidth=300, valueType=float, orientation="horizontal")
        self.le_phase_input_beam9 = oasysgui.lineEdit(weight_box, self, "phase_input_beam9", "Input Beam 9 add phase [rad]",
                                                    labelWidth=300, valueType=float, orientation="horizontal")
        gui.separator(weight_box, height=10)

        self.le_weight_input_beam10 = oasysgui.lineEdit(weight_box, self, "weight_input_beam10", "Input Beam 10 weight",
                                                    labelWidth=300, valueType=float, orientation="horizontal")
        self.le_phase_input_beam10 = oasysgui.lineEdit(weight_box, self, "phase_input_beam10", "Input Beam 10 add phase [rad]",
                                                    labelWidth=300, valueType=float, orientation="horizontal")
        gui.separator(weight_box, height=10)

        self.le_weight_input_beam1.setEnabled(False)
        self.le_weight_input_beam2.setEnabled(False)
        self.le_weight_input_beam3.setEnabled(False)
        self.le_weight_input_beam4.setEnabled(False)
        self.le_weight_input_beam5.setEnabled(False)
        self.le_weight_input_beam6.setEnabled(False)
        self.le_weight_input_beam7.setEnabled(False)
        self.le_weight_input_beam8.setEnabled(False)
        self.le_weight_input_beam9.setEnabled(False)
        self.le_weight_input_beam10.setEnabled(False)

        self.le_phase_input_beam1.setEnabled(False)
        self.le_phase_input_beam2.setEnabled(False)
        self.le_phase_input_beam3.setEnabled(False)
        self.le_phase_input_beam4.setEnabled(False)
        self.le_phase_input_beam5.setEnabled(False)
        self.le_phase_input_beam6.setEnabled(False)
        self.le_phase_input_beam7.setEnabled(False)
        self.le_phase_input_beam8.setEnabled(False)
        self.le_phase_input_beam9.setEnabled(False)
        self.le_phase_input_beam10.setEnabled(False)


    def setBeam1(self, beam):
        self.le_weight_input_beam1.setEnabled(False)
        self.le_phase_input_beam1.setEnabled(False)
        self.input_beam1 = None

        try:
            shape = beam.get_wavefront().get_complex_amplitude().shape
        except:
            QtWidgets.QMessageBox.critical(self, "Error",
                                           "Data #1 not displayable",
                                           QtWidgets.QMessageBox.Ok)
            return

        self.input_beam1 = beam
        if self.use_weights:
            self.le_weight_input_beam1.setEnabled(True)
            self.le_phase_input_beam1.setEnabled(True)



    def setBeam2(self, beam):
        self.le_weight_input_beam2.setEnabled(False)
        self.le_phase_input_beam2.setEnabled(False)
        self.input_beam2 = None

        try:
            shape = beam.get_wavefront().get_complex_amplitude().shape
        except:
            QtWidgets.QMessageBox.critical(self, "Error",
                                           "Data #2 not displayable",
                                           QtWidgets.QMessageBox.Ok)
            return

        self.input_beam2 = beam
        if self.use_weights:
            self.le_weight_input_beam2.setEnabled(True)
            self.le_phase_input_beam2.setEnabled(True)

    def setBeam3(self, beam):
        self.le_weight_input_beam3.setEnabled(False)
        self.le_phase_input_beam3.setEnabled(False)
        self.input_beam3 = None

        try:
            shape = beam.get_wavefront().get_complex_amplitude().shape
        except:
            QtWidgets.QMessageBox.critical(self, "Error",
                                           "Data #3 not displayable",
                                           QtWidgets.QMessageBox.Ok)
            return

        self.input_beam3 = beam
        if self.use_weights:
            self.le_weight_input_beam3.setEnabled(True)
            self.le_phase_input_beam3.setEnabled(True)

    def setBeam4(self, beam):
        self.le_weight_input_beam4.setEnabled(False)
        self.le_phase_input_beam4.setEnabled(False)
        self.input_beam4 = None

        try:
            shape = beam.get_wavefront().get_complex_amplitude().shape
        except:
            QtWidgets.QMessageBox.critical(self, "Error",
                                           "Data #4 not displayable",
                                           QtWidgets.QMessageBox.Ok)
            return

        self.input_beam4 = beam
        if self.use_weights:
            self.le_weight_input_beam4.setEnabled(True)
            self.le_phase_input_beam4.setEnabled(True)

    def setBeam5(self, beam):
        self.le_weight_input_beam5.setEnabled(False)
        self.le_phase_input_beam5.setEnabled(False)
        self.input_beam5 = None

        try:
            shape = beam.get_wavefront().get_complex_amplitude().shape
        except:
            QtWidgets.QMessageBox.critical(self, "Error",
                                           "Data #5 not displayable",
                                           QtWidgets.QMessageBox.Ok)
            return

        self.input_beam5 = beam
        if self.use_weights:
            self.le_weight_input_beam5.setEnabled(True)
            self.le_phase_input_beam5.setEnabled(True)

    def setBeam6(self, beam):
        self.le_weight_input_beam6.setEnabled(False)
        self.le_phase_input_beam6.setEnabled(False)
        self.input_beam6 = None

        try:
            shape = beam.get_wavefront().get_complex_amplitude().shape
        except:
            QtWidgets.QMessageBox.critical(self, "Error",
                                           "Data #6 not displayable",
                                           QtWidgets.QMessageBox.Ok)
            return

        self.input_beam6 = beam
        if self.use_weights:
            self.le_weight_input_beam6.setEnabled(True)
            self.le_phase_input_beam6.setEnabled(True)

    def setBeam7(self, beam):
        self.le_weight_input_beam7.setEnabled(False)
        self.le_phase_input_beam7.setEnabled(False)
        self.input_beam7 = None

        try:
            shape = beam.get_wavefront().get_complex_amplitude().shape
        except:
            QtWidgets.QMessageBox.critical(self, "Error",
                                           "Data #7 not displayable",
                                           QtWidgets.QMessageBox.Ok)
            return

        self.input_beam7 = beam
        if self.use_weights:
            self.le_weight_input_beam7.setEnabled(True)
            self.le_phase_input_beam7.setEnabled(True)

    def setBeam8(self, beam):
        self.le_weight_input_beam8.setEnabled(False)
        self.le_phase_input_beam8.setEnabled(False)
        self.input_beam8 = None

        try:
            shape = beam.get_wavefront().get_complex_amplitude().shape
        except:
            QtWidgets.QMessageBox.critical(self, "Error",
                                           "Data #8 not displayable",
                                           QtWidgets.QMessageBox.Ok)
            return

        self.input_beam8 = beam
        if self.use_weights:
            self.le_weight_input_beam8.setEnabled(True)
            self.le_phase_input_beam8.setEnabled(True)

    def setBeam9(self, beam):
        self.le_weight_input_beam9.setEnabled(False)
        self.le_phase_input_beam9.setEnabled(False)
        self.input_beam9 = None

        try:
            shape = beam.get_wavefront().get_complex_amplitude().shape
        except:
            QtWidgets.QMessageBox.critical(self, "Error",
                                           "Data #9 not displayable",
                                           QtWidgets.QMessageBox.Ok)
            return

        self.input_beam9 = beam
        if self.use_weights:
            self.le_weight_input_beam9.setEnabled(True)
            self.le_phase_input_beam9.setEnabled(True)

    def setBeam10(self, beam):
        self.le_weight_input_beam10.setEnabled(False)
        self.le_phase_input_beam10.setEnabled(False)
        self.input_beam10 = None

        try:
            shape = beam.get_wavefront().get_complex_amplitude().shape
        except:
            QtWidgets.QMessageBox.critical(self, "Error",
                                           "Data #10 not displayable",
                                           QtWidgets.QMessageBox.Ok)
            return

        self.input_beam10 = beam
        if self.use_weights:
            self.le_weight_input_beam10.setEnabled(True)
            self.le_phase_input_beam10.setEnabled(True)

    def merge_beams(self):
        merged_beam = None

        if self.use_weights == 1:
            total_intensity = 1.0
            for index in range(1, 11):
                current_beam = getattr(self, "input_beam" + str(index))
                if not current_beam is None:
                    total_intensity += 0

        cumulated_complex_amplitude = None
        for index in range(1, 11):
            current_beam = getattr(self, "input_beam" + str(index))
            if not current_beam is None:
                current_beam = current_beam.duplicate()
                if self.use_weights == 1:
                    new_weight = getattr(self, "weight_input_beam" + str(index))
                    current_beam.get_wavefront().rescale_amplitude(new_weight)

                    new_phase = getattr(self, "phase_input_beam" + str(index))
                    current_beam.get_wavefront().add_phase_shift(new_phase)

                if cumulated_complex_amplitude is None:
                    merged_beam = current_beam.duplicate()
                    energy = merged_beam.get_wavefront().get_photon_energy()
                    cumulated_complex_amplitude = current_beam.get_wavefront().get_complex_amplitude().copy()
                    shape = cumulated_complex_amplitude.shape
                else:
                    ca = current_beam.get_wavefront().get_complex_amplitude().copy()
                    if current_beam.get_wavefront().get_photon_energy() != energy:
                        QtWidgets.QMessageBox.critical(self, "Error",
                                                       "Energies must match %f != %f" % (energy, current_beam.get_wavefront().get_photon_energy()),
                                                       QtWidgets.QMessageBox.Ok)
                        return
                    if ca.shape != shape:
                        QtWidgets.QMessageBox.critical(self, "Error",
                                                       "Wavefronts must have the same dimension and size",
                                                       QtWidgets.QMessageBox.Ok)
                        return
                    cumulated_complex_amplitude += ca

        wf = merged_beam.get_wavefront()
        wf.set_complex_amplitude(cumulated_complex_amplitude)

        self.send("WofryData", merged_beam)


    def set_UseWeights(self):
        self.le_weight_input_beam1.setEnabled(self.use_weights == 1 and not  self.input_beam1 is None)
        self.le_weight_input_beam2.setEnabled(self.use_weights == 1 and not  self.input_beam2 is None)
        self.le_weight_input_beam3.setEnabled(self.use_weights == 1 and not  self.input_beam3 is None)
        self.le_weight_input_beam4.setEnabled(self.use_weights == 1 and not  self.input_beam4 is None)
        self.le_weight_input_beam5.setEnabled(self.use_weights == 1 and not  self.input_beam5 is None)
        self.le_weight_input_beam6.setEnabled(self.use_weights == 1 and not  self.input_beam6 is None)
        self.le_weight_input_beam7.setEnabled(self.use_weights == 1 and not  self.input_beam7 is None)
        self.le_weight_input_beam8.setEnabled(self.use_weights == 1 and not  self.input_beam8 is None)
        self.le_weight_input_beam9.setEnabled(self.use_weights == 1 and not  self.input_beam9 is None)
        self.le_weight_input_beam10.setEnabled(self.use_weights == 1 and not  self.input_beam10 is None)

        self.le_phase_input_beam1.setEnabled(self.use_weights == 1 and not  self.input_beam1 is None)
        self.le_phase_input_beam2.setEnabled(self.use_weights == 1 and not  self.input_beam2 is None)
        self.le_phase_input_beam3.setEnabled(self.use_weights == 1 and not  self.input_beam3 is None)
        self.le_phase_input_beam4.setEnabled(self.use_weights == 1 and not  self.input_beam4 is None)
        self.le_phase_input_beam5.setEnabled(self.use_weights == 1 and not  self.input_beam5 is None)
        self.le_phase_input_beam6.setEnabled(self.use_weights == 1 and not  self.input_beam6 is None)
        self.le_phase_input_beam7.setEnabled(self.use_weights == 1 and not  self.input_beam7 is None)
        self.le_phase_input_beam8.setEnabled(self.use_weights == 1 and not  self.input_beam8 is None)
        self.le_phase_input_beam9.setEnabled(self.use_weights == 1 and not  self.input_beam9 is None)
        self.le_phase_input_beam10.setEnabled(self.use_weights == 1 and not  self.input_beam10 is None)


if __name__ == "__main__":
    a = QApplication(sys.argv)
    ow = OWWOMerge()
    ow.show()
    a.exec_()
    ow.saveSettings()
