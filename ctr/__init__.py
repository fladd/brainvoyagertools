"""Create, read and write .ctr files.

"""

__author__ = "Florian Krause <siebenhundertzehn@gmail.com>"


import os
import random
from collections import OrderedDict

import numpy as np
import scipy.stats as stats


class Contrast:
    """A class representing a Contrast object."""

    def __init__(self, name, data):
        """Create a Contrast object.

        Parameters
        ----------
        name : str
            the name of the contrast
        data : list
            the data of the contrast

        """

        self.name = name
        self.data = np.array(data)

    def __str__(self):
        return "{0}\n{1}".format(repr(self.name),
                                 repr(self.data))


class ContrastsDefinition:
    """A class representing a contrasts definition."""

    def __init__(self, load=None):
        """Create a contrasts definition object.

        Parameters
        ----------
        load : str, optional
            the name of a .ctr file to load

        """

        self.clear()
        if load is not None:
            self.load(load)

    def __str__(self):
        return "{0}\n\n{1}\n{2}".format(self._format_header(),
                                 self._format_names(),
                                 self._format_data())

    @property
    def header(self):
        return self._header

    @property
    def contrasts(self):
        return self._contrasts

    @property
    def names(self):
        return [x.name for x in self.contrasts]

    @property
    def data(self):
        for c,x in enumerate(self.contrasts):
            if c == 0:
                rtn = np.array([x.data]).T
            else:
                rtn = np.append(rtn, np.array([x.data]).T, axis=1)
        return rtn

    def _format_header(self):
        rtn = ""
        for c,x in enumerate(self.header):
            rtn += "{0}:".format(x).ljust(22) + "{0}".format(self.header[x])
            if c < len(self.header) - 1:
                rtn += "\n"
        return rtn

    def _format_names(self):
        return '"' + '" "'.join(self.names) + '"'

    def _format_data(self):
        rtn = ""
        for c,x in enumerate(self.data):
            rtn += " ".join(["{0:d}".format(y).rjust(3) for y in x])
            if c < np.shape(self.data)[0] - 1:
                rtn += "\n"
        return rtn

    def add_contrast(self, contrast):
        """Add a contrast to the contrasts definition.

        Parameters
        ----------
        contrast : Contrast object
            the contrast to add to contrasts definition

        """

        if self._header["NrOfContrasts"] == 0:
            self._header["NrOfValues"] = len(contrast.data)
        else:
            if self._header["NrOfValues"] != len(contrast.data):
                e = "Contrast has {0} data points, but contrasts definition has {1}!"
                raise ValueError(e.format(len(contrast.data),
                                          self._header["NrOfValues"]))

        self._header["NrOfContrasts"] += 1

    def clear(self):
        """Clear contrasts definition."""

        self._header = OrderedDict([("FileVersion", 1),
                                   ("NrOfContrasts", 0),
                                   ("NrOfValues", 0)])
        self._contrasts = []

    def load(self, filename):
        """Load contrasts definition from a .ctr file.

        This will overwrite current header and contrasts!

        Parameters
        ----------
        filename : str
            the name of the .ctr file

        """

        self.clear()
        with open(filename) as f:
            lines = f.readlines()
        for counter, line in enumerate(lines):
            if line.startswith('"'):
                break
        names = line.strip().strip('"').split('" "')
        for line in lines[:counter-1]:
            if line.strip():
                self._header[line[:16].strip(": ")] = int(line[16:].strip())
        data = np.array([[int(line[i:i+4]) for i in range(0, len(line), 4) if line[i].strip("\r\n")!=""]
                                       for line in lines[counter + 1:]])
        for x in range(len(names)):
            self._contrasts.append(Contrast(names[x], data[:,x]))

    def save(self, filename):
        """Save contrast definition to a .ctr file.

        Parameters
        ----------
        filename : str
            the name of the .ctr file

        """

        if not os.path.splitext(filename)[-1].lower() == ".ctr":
            filename += ".ctr"

        with open(filename, 'w') as f:
            f.write("\n")
            f.write(self._format_header() + "\n")
            f.write("\n")
            f.write(self._format_names() + "\n")
            f.write(self._format_data())
