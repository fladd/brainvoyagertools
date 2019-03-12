"""Create, read and write .voi files.

"""

__author__ = "Florian Krause <siebenhundertzehn@gmail.com>"


import os
import random
from collections import OrderedDict
from itertools import groupby

import numpy as np
import scipy.stats as stats


class VOI:
    """A class representing a VOI."""

    def __init__(self, name, data, colour=None):
        """Create a VOI object.

        Parameters
        ----------
        name : str
            the name of the VOI
        data : list
            the data of the VOI
        colour : [int, int, int], optional
            the colour of the VOI;
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

    def _format_colour(self):
        return "ColorOfVOI: " + " ".join([str(x) for x in self.colour])
    
    def _format_data(self):
        rtn = ""
        for c, coordinate in enumerate(self.data):
            rtn += " ".join([str(int(x)) for x in coordinate])
            if c < len(self.data) - 1:
                rtn += "\n"
        return rtn

    def __str__(self):
        return "NameOfVOI:  {0}\n{1}\n\nNrOfVoxels: {2}\n{3}".format(
                self.name,
                self._format_colour(),
                len(self.data),
                self._format_data())

class VOIsDefinition:
    """A class representing a VOIs definition."""

    def __init__(self, reference_space="BV", resolution=[1,1,1],
            offset=[0,0,0], framing_cube=256, left_right=1,
            subject_voi_naming="<VOI>_<SUBJ>", load=None):
        """Create a VOIs definition object.

        Parameters
        ---------- 
        reference_space : str, optional
            the reference space ("BV", "TAL", "MNI"; default="BV")
        resolution : [int, int, int], optional
            the resolution of the original VMR (default=[1,1,1])
        offset : [int, int, int], optional
            the offset of the original VMR (default=[0,0,0])
        framing_cube : int, optional
            the dimension of the original VMR framing cube (default=256)
        left_right : int, optional
            the image orientation (radiological=1, neurological=2; default=1)
        subject_voi_naming : str, optional
            the subject and VOI naming convention (default="<VOI>_<SUBJ>")
        load : str, optional
            the name of a .voi file to load

        """

        self.clear()
        self.header["OriginalVMRResolutionX"] = resolution[0]
        self.header["OriginalVMRResolutionY"] = resolution[1]
        self.header["OriginalVMRResolutionZ"] = resolution[2]
        self.header["OriginalVMROffsetX"] = offset[0]
        self.header["OriginalVMROffsetY"] = offset[1]
        self.header["OriginalVMROffsetZ"] = offset[2]
        self.header["ReferenceSpace"] = reference_space
        self.header["OriginalVMRFramingCubeDim"] = framing_cube
        self.header["LeftRightConvention"] = left_right
        self.header["SubjectVOINamingConvention"] = subject_voi_naming
        if load is not None:
            try:
                self.load(load)
            except:
                raise IOError("Could not read {0}!".format(load))

    def __str__(self):
        return "{0}\n\n{1}\n\n{2}".format(self._format_header(),
                                          self._format_vois(),
                                          self._format_vtcs())

    @property
    def header(self):
        return self._header

    @property
    def vois(self):
        return self._vois

    @property
    def vtcs(self):
        return self._vtcs

    @property
    def names(self):
        return [x.name for x in self.vois]

    @property
    def colours(self):
        return [x.colour for x in self.vois]

    def _format_header(self):
        rtn = ""
        for c,x in enumerate(self.header):
            if x in ("FileVersion", "OriginalVMRResolutionX",
                    "LeftRightConvention", "SubjectVOINamingConvention"):
                rtn += "\n"
            if x ==  "NrOfVOIs":
                rtn += "\n\n"
            rtn += "{0}:".format(x).ljust(29) + "{0}".format(self.header[x])
            if c < len(self.header) - 1:
                rtn += "\n"
            if c == 0:
                rtn += "\n"
        return rtn

    def _format_vois(self):
        rtn = "NrOfVOIs".ljust(29) + "{0}\n\n".format(len(self.vois))
        for c, voi in enumerate(self.vois):
            rtn += str(voi)
            if c < len(self.vois) - 1:
                rtn += "\n\n"
        return rtn

    def _format_vtcs(self):
        rtn = "NrOfVOIVTCs: {0}".format(len(self.vtcs))
        for c, vtc in enumerate(self.vtcs):
            rtn += vtc
            if c < len(self.vtcs) - 1:
                rtn += "\n"
        return rtn

    def add_voi(self, voi):
        """Add a VOI to the VOIs definition.

        Parameters
        ----------
        voi : VOI object
            the VOI to add to the VOIs definition

        """

        self._vois.append(voi)

    def add_vtc(self, vtc):
        """Add a VOI VTC to the VOIs definition.

        Parameters
        ----------
        vtc : str
            the full path of the VOI VTC to add to the VOIs definition

        """

        self._vtcs.append(vtc)

    def clear(self):
        """Clear VOIs definition."""

        self._header = OrderedDict([("FileVersion", 4),
                                    ("ReferenceSpace", "BV"),
                                    ("OriginalVMRResolutionX", 1),
                                    ("OriginalVMRResolutionY", 1),
                                    ("OriginalVMRResolutionZ", 1),
                                    ("OriginalVMROffsetX", 0),
                                    ("OriginalVMROffsetY", 0),
                                    ("OriginalVMROffsetZ", 0),
                                    ("OriginalVMRFramingCubeDim", 256),
                                    ("LeftRightConvention", 1),
                                    ("SubjectVOINamingConvention", "<VOI>_<SUBJ>")])
        self._vois = []
        self._vtcs = []

    def load(self, filename):
        """Load VOIs definition from a .voi file.

        This will overwrite current header and VOIs!

        Parameters
        ----------
        filename : str
            the name of the .voi file

        """

        self.clear()
        with open(filename) as f:
            lines = f.readlines()
        lines = [x[0] for x in groupby(lines)]
        for counter, line in enumerate(lines):
            if line.startswith('NrOfVOIs'):
                break
        for line in lines[:counter-1]:
            if line.strip() != "":
                value = line[27:].strip().split(" ")
                try:
                    value = int(value[0])
                except:
                    value = value[0]
                self._header[line[:27].strip(": ")] = value

        idx = counter
        for line in lines[counter+1:]: 
            idx += 1
            if line.startswith("NrOfVOIVTCs"):
                break
            if line.startswith("NameOfVOI"):
                try:
                    name = line.split(":")[1].strip()
                    colour = [int(x) for x in lines[idx+1].split(":")[1].strip().split(" ")]
                    nvoxels =  int(lines[idx+3].split(":")[1].strip())
                    start = idx + 4
                    end = start + nvoxels
                    data = []
                    for x in range(start, end):
                        data.append([int(i) for i in lines[x].split(" ") if i])
                    self.add_voi(VOI(name, data, colour))
                except IndexError:
                    pass

        for line in lines[idx+1:]:
            try:
                self.add_vtc(line.strip())
            except IndexError:
                pass

    def save(self, filename):
        """Save VOIs definition to a .voi file.

        Parameters
        ----------
        filename : str
            the name of the .voi file

        """

        if not os.path.splitext(filename)[-1].lower() == ".voi":
            filename += ".voi"

        with open(filename, 'w') as f:
            f.write(self._format_header() + "\n")
            f.write("\n\n")
            f.write(self._format_vois() + "\n")
            f.write("\n\n")
            f.write(self._format_vtcs())
