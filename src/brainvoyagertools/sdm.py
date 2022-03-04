"""Create, read and write .sdm files.

"""

__author__ = "Florian Krause <me@floriankrause.org>"


import os
import random
from collections import OrderedDict

import numpy as np
import scipy.stats as stats


class Predictor:
    """A class representing a predictor."""

    def __init__(self, name, data, colour=None):
        """Create a Predictor object.

        Parameters
        ----------
        name : str
            the name of the predictor
        data : list
            the data of the predictor
        colour : [int, int, int], optional
            the colour of the regressor;
            a random colour will be generated if argument not given (default)

        """

        self.name = name
        self.data = np.array(data)
        if colour is not None:
            if isinstance(colour, str):
                self.colour = [int(x) for x in colour.split(" ") if x != '']
            else:
                self.colour = list(colour[:3])
        else:
            self.colour = [random.randint(0, 255),
                           random.randint(0, 255),
                           random.randint(0, 255)]

    def __str__(self):
        return "{0}\n{1}\n{2}\n{3}".format(self.colour, repr(self.name),
                                           repr(self.data), len(self.data))

    def _hrf(self, tr, p=[6,16,1,1,6,0,32]):
        """Create an HRF from two gamma functions.

        Paramters
        ---------
        tr : float
            repetition time (in seconds) at which to sample the HRF
        p : list, optional
            parameters of the two gamma functions:
                                                                defaults
                                                                (seconds)
            p[0] - delay of response (relative to onset)         6
            p[1] - delay of undershoot (relative to onset)      16
            p[2] - dispersion of response                        1
            p[3] - dispersion of undershoot                      1
            p[4] - ratio of response to undershoot               6
            p[5] - onset (seconds)                               0
            p[6] - length of kernel (seconds)                   32

        """

        p = [float(x) for x in p]
        tr=float(tr)
        fMRI_T = 16.0

        # HRF in seconds
        dt = tr/fMRI_T
        u = np.arange(p[6] / dt + 1) - p[5] / dt
        g1 = stats.gamma.pdf(u, p[0] / p[2], scale=1.0 / (dt / p[2]))
        g2 = stats.gamma.pdf(u, p[1] / p[3], scale=1.0 / (dt / p[3])) / p[4]
        hrf = g1 - g2

        # Sample in volumes
        good_pts = np.array(range(np.int((p[6] + tr) / tr))) * fMRI_T
        hrf = hrf[[int(x) for x in list(good_pts)]]
        hrf = hrf / np.sum(hrf);

        return hrf

    def convolve_with_hrf(self, tr):  # TODO: Needs testing!
        """Convolve with the haemodynamic response function.

        Parameters
        ----------
        tr : int
            the repetition time in milliseconds

        """

        tr = float(tr) / 1000
        hrf_ = self._hrf(tr)
        self.data = np.convolve(self.data, self._hrf(tr))[0:len(self.data)]

    def ztransform(self):
        """z-transform the predictor data."""

        self.data = stats.mstats.zscore(self.data, axis=0)

    def get_derivative(self, n=1):  # TODO: Needs testing!
        """Get derivative of predictor.

        Parameters
        ----------
        n : int
            the order of the derivative

        Returns
        -------
        predictor : Predictor
            the derivative predictor

        """

        name = self.name + "_D{0}".format(n)
        data = self.data
        for x in range(n):
            data = np.ediff1d(data, to_begin=0)

        return Predictor(name, data, self.colour)


class DesignMatrix:
    """A class representing a single-subject design matrix."""

    def __init__(self, load=None):
        """Create a design matrix object.

        Parameters
        ----------
        load : str, optional
            the name of a .sdm file to load

        """

        self.clear()
        if load is not None:
            try:
                self.load(load, col_length=11)
            except:
                try:
                    self.load(load, col_length=12)
                except:
                    raise IOError("Could not read {0}!".format(load))

    def __str__(self):
        return "{0}\n\n{1}\n{2}\n{3}".format(self._format_header(),
                                             self._format_colours(),
                                             self._format_names(),
                                             self.data)

    @property
    def header(self):
        return self._header

    @property
    def predictors(self):
        return self._predictors

    @property
    def names(self):
        return [x.name for x in self.predictors]

    @property
    def colours(self):
        return [x.colour for x in self.predictors]

    @property
    def data(self):
        for c,x in enumerate(self.predictors):
            if c == 0:
                rtn = np.array([x.data]).T
            else:
                rtn = np.append(rtn, np.array([x.data]).T, axis=1)
        return rtn

    def _format_header(self):
        rtn = ""
        for c,x in enumerate(self.header):
            rtn += "{0}:".format(x).ljust(24) + "{0}".format(self.header[x])
            if c < len(self.header) - 1:
                rtn += "\n"
            if c == 0:
                rtn += "\n"
        return rtn

    def _format_colours(self):
        colours = ["{0} {1} {2}".format(x[0],x[1],x[2]) for x in self.colours]
        return "   ".join(colours)

    def _format_names(self):
        return '"' + '" "'.join(self.names) + '"'

    def _format_data(self):
        rtn = ""
        for c,x in enumerate(self.data):
            rtn += "".join(["{0:f}".format(y).rjust(12) for y in x])
            if c < np.shape(self.data)[0] - 1:
                rtn += "\n"
        return rtn

    def add_predictor(self, predictor, is_confound=False):
        """Add a predictor to the design matrix.

        Parameters
        ----------
        predictor : Predictor object
            the predictor to add to the design matrix
        is_confound : bool, optional
            whether the predictor is a confound predictor (default=False)

        """

        if self._header["NrOfPredictors"] > 0:
            if len(predictor.data) != self._header["NrOfDataPoints"]:
                e = "Predictor has {0} data points, but design matrix has {1}!"
                raise ValueError(e.format(len(predictor.data),
                                          self._header["NrOfDataPoints"]))

        if is_confound:
            position = self._header["NrOfPredictors"] - \
                        self._header["IncludesConstant"]
        else:
            position = self._header["FirstConfoundPredictor"] - 1
        self._predictors.insert(position, predictor)

        if self._header["NrOfPredictors"] == 0:
            self._header["NrOfDataPoints"] = len(predictor.data)
        self._header["NrOfPredictors"] += 1

        if not is_confound:
            self._header["FirstConfoundPredictor"] += 1

    def add_confound_predictor(self, predictor):
        """Add a confound predictor to the design matrix.

        Parameters
        ----------
        predictor : Predictor object
            the predictor to add to the design matrix

        """

        self.add_predictor(predictor, is_confound=True)

    def add_constant(self):
        """Add constant."""

        self.add_predictor(Predictor("Constant", len(self.data) * [1], [255,255,255]), True)
        self._header["IncludesConstant"] = 1

    def define_predictors(self, protocol, data_points, tr):
        """Define predictors from stimulation protocol.

        Note: This does (for now) only create demeaned parametric predictors!

        Parameters
        ----------
        protocol : brainvoyagertools.prt.StimulationProtocol
            the protocol do define predictors from
        data_points : int
            the number of data points per predictor
        tr : int or None
            the TR for convolving with HRF; no convolution if None

        """

        if protocol.time_units != "Volumes":
            raise NotImplementedError(
                "Currently only protocols with time unit 'Volumes' supported!")

        for condition in protocol.conditions:
            # main effect
            mod = False
            parameters = []
            data = data_points * [0]
            for event in condition.data:
                if protocol.header["ParametricWeights"] == 1:
                    parameters.append(event[2])
                    if event[2] != 1:
                        mod = True
                for x in range(event[0]-1, event[1]):
                    data[x] = 1
            if mod:
                predictor = Predictor(condition.name + " [Main]", data,
                                      condition.colour)
            else:
                predictor = Predictor(condition.name, data, condition.colour)
            if tr is not None:
                predictor.convolve_with_hrf(tr)
            self.add_predictor(predictor)

            # parametric effect
            if mod:
                mean = np.mean(list(set(parameters)))
                mod_data = data_points * [0]
                for event in condition.data:
                    for x in range(event[0]-1, event[1]):
                        mod_data[x] = event[2] - mean
                predictor = Predictor(condition.name + " [Parametric]", mod_data,
                                      condition.colour)
                if tr is not None:
                    predictor.convolve_with_hrf(tr)
                self.add_predictor(predictor)

    def clear(self):
        """Clear design matrix."""

        self._header = OrderedDict([("FileVersion", 1),
                                   ("NrOfPredictors", 0),
                                   ("NrOfDataPoints", 0),
                                   ("IncludesConstant", 0),
                                   ("FirstConfoundPredictor", 1)])
        self._predictors = []

    def load(self, filename, col_length=11):
        """Load design matrix from a .sdm file.

        This will overwrite current header and predictors!

        Parameters
        ----------
        filename : str
            the name of the .sdm file
        col_length : int, optional
            the length of the columns in characters
                design files -- 11 (default)
                motion files -- 12

        """

        self.clear()
        with open(filename) as f:
            lines = f.readlines()
        for counter, line in enumerate(lines):
            if line.startswith('"'):
                break
        names = line.strip().strip('"').split('" "')
        colours = lines[counter-1].strip().split('   ')
        for line in lines[:counter-1]:
            if line.strip():
                self._header[line[:24].strip(": ")] = int(line[24:].strip())
        data = np.array([[float(line[i:i+col_length]) for i in range(0, len(line), col_length) if line[i].strip("\r\n")!=""]
                                       for line in lines[counter + 1:]])
        for x in range(len(names)):
            self._predictors.append(Predictor(names[x], data[:,x], colours[x]))

    def save(self, filename):
        """Save design matrix to a .sdm file.

        Parameters
        ----------
        filename : str
            the name of the .sdm file

        """

        if not os.path.splitext(filename)[-1].lower() == ".sdm":
            filename += ".sdm"

        with open(filename, 'w') as f:
            f.write(self._format_header() + "\n")
            f.write("\n")
            f.write(self._format_colours() + "\n")
            f.write(self._format_names() + "\n")
            f.write(self._format_data())
