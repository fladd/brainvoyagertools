"""Create, read and write .mdm files.

"""

__author__ = "Florian Krause <siebenhundertzehn@gmail.com>"


import os
import random
from collections import OrderedDict

import numpy as np
import scipy.stats as stats


class Study:
    """A class representing a Study object."""

    def __init__(self, data_files, sdm_file):
        """Create a Study object.

        Parameters
        ----------
        data_files : str or list
            full path of .vtc file or full paths of .ssm and .mtc files
        sdm_file : str
            fullpath of .sdm file

        """

        if not isinstance(data_files, list):
            data_files = [data_files]
        self.data_files = data_files
        self.sdm_file = sdm_file

    def __str__(self):
        return "{0}\n{1}".format(self.data_files, repr(self.sdm_file))


class DesignMatrix:
    """A class representing a multi-subject design matrix."""

    def __init__(self, load=None):
        """Create a design matrix object.

        Parameters
        ----------
        load : str, optional
            the name of a .mdm file to load

        """

        self.clear()
        if load is not None:
            self.load(load)

    def __str__(self):
        return "{0}\n{1}".format(self._format_header(),
                                 self._format_studies())

    @property
    def header(self):
        return self._header

    @property
    def studies(self):
        return self._studies

    @property
    def rfx_glm(self):
        return bool(self._header["RFX-GLM"])

    @rfx_glm.setter
    def rfx_glm(self, value):
        self._header["RFX-GLM"] = int(value)

    @property
    def transformation(self):
        if self._header["PSCTransformation"] == 1:
            return "psc"
        elif self._header["zTransformation"] == 1:
            return "z"

    @transformation.setter
    def transformation(self, value):
        if value.lower() == "psc":
            self._header["PSCTransformation"] = 1
            self._header["zTransformation"] = 0
        elif value.lower() == "z":
            self._header["zTransformation"] = 1
            self._header["PSCTransformation"] = 0
        else:
            raise ValueError("'rfx_glm' can only be 'psc' or 'z'!")

    @property
    def separate_predictors(self):
        return bool(self._header["SeparatePredictors"])

    @separate_predictors.setter
    def separate_predictors(self, value):
        self._header["SeparatePredictors"] = int(value)

    def _format_header(self):
        rtn = ""
        for c,x in enumerate(self.header):
            rtn += "{0}:".format(x).ljust(22) + "{0}".format(self.header[x])
            if c < len(self.header) - 1:
                rtn += "\n"
            if c in [1,2,5]:
                rtn += "\n"
        return rtn

    def _format_studies(self):
        rtn = ""
        for c,x in enumerate(self.studies):
            rtn += '"' + '" "'.join(x.data_files) + '" "' +  x.sdm_file + '"'
            if c < len(self.header) - 1:
                rtn += "\n"
        return rtn

    def add_study(self, study):
        """Add a study to the design matrix.

        Parameters
        ----------
        study : Study object
            the study to add to the design matrix

        """

        if len(study.data_files) > 1:
            if self._header["NrOfStudies"] > 0 and \
               self._header["TypeOfFunctionalData"] == "VTC":
                raise ValueError(
                    "Data is MTC, but design matrix contains VTC data!")
            else:
                self._header["TypeOfFunctionalData"] = "MTC"
        else:
            if self._header["NrOfStudies"] > 0 and \
               self._header["TypeOfFunctionalData"] == "MTC":
                raise ValueError(
                    "Data is VTC, but design matrix contains MTC data!")

        self._header["NrOfStudies"] += 1
        self._studies.append(study)

    def clear(self):
        """Clear design matrix."""

        self._header = OrderedDict([("FileVersion", 3),
                                   ("TypeOfFunctionalData", "VTC"),
                                   ("RFX-GLM", 0),
                                   ("PSCTransformation", 1),
                                   ("zTransformation", 0),
                                   ("SeparatePredictors", 0),
                                   ("NrOfStudies", 0)])
        self._studies = []

    def load(self, filename):
        """Load design matrix from a .mdm file.

        This will overwrite current header and studies!

        Parameters
        ----------
        filename : str
            the name of the .mdm file

        """

        self.clear()
        with open(filename) as f:
            lines = f.readlines()
        for counter, line in enumerate(lines):
            if line.startswith('"'):
                break
        for line in lines[:counter-1]:
            if line.strip():
                try:
                    self._header[line[:22].strip(": ")] = int(line[22:].strip())
                except ValueError:
                    self._header[line[:22].strip(": ")] = line[22:].strip()
        for line in lines[counter:]:
            tmp = [x for x in line.split('"') if x.strip()!= ""]
            if len(tmp) > 2:
                data_files = tmp[:2]
                sdm_file = tmp[2]
            else:
                data_files = [tmp[0]]
                sdm_file = tmp[1]
            self._studies.append(Study(data_files, sdm_file))

    def save(self, filename):
        """Save design matrix to a .mdm file.

        Parameters
        ----------
        filename : str
            the name of the .mdm file

        """

        if not os.path.splitext(filename)[-1].lower() == ".mdm":
            filename += ".mdm"

        with open(filename, 'w') as f:
            f.write("\n")
            f.write(self._format_header() + "\n")
            f.write(self._format_studies())
