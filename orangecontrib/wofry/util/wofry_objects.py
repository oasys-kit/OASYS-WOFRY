from syned.beamline.beamline import Beamline
from wofry.propagator.wavefront import Wavefront

class WofryData(object):
    def __init__(self, beamline=Beamline(), wavefront=Wavefront()):
        super().__init__()

        self.__beamline = beamline
        self.__wavefront = wavefront

    def get_beamline(self):
        return self.__beamline

    def get_wavefront(self):
        return self.__wavefront
