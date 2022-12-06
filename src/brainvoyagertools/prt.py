"""Create, read and write .prt files.

"""

__author__ = "Florian Krause <me@floriankrause.org>"


import os
import random
from collections import OrderedDict
from itertools import groupby

import numpy as np


class Condition:
    """A class implementing a condition."""

    def __init__(self, name, data, colour=None):
        """Create a condition.

        Parameters
        ----------
        name : str
            the name of the condition
        data : list
            the data of the condition
        colour : [int, int, int], optional
            the colour of the condition;
            a random colour will be generated if argument not given (default)

        """

        self.name = name
        self.data = np.array(data, dtype=object)
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
        return "{0}\n{1}\n{2}\n{3}".format(self.name,
                                           len(self.data),
                                           self._format_data(),
                                           self._format_colour())

    def __add__(self, other):
        name = self.name + "+" + other.name
        data = np.sort(np.concatenate((self.data, other.data)), axis=0)
        colour = [min(self.colour[0] + other.colour[0], 255),
                 min(self.colour[1] + other.colour[1], 255),
                 min(self.colour[2] + other.colour[2], 255)]

        return Condition(name, data, colour)
    
    def _format_data(self):
        rtn = ""
        max = 0
        for intervall in self.data:
            if len(str(intervall[1])) > max:
                max = len(str(intervall[1]))
        for c, intervall in enumerate(self.data):
            rtn += " {0}".format(
                "  ".join([str(x).rjust(max) for x in intervall]))
            if c < len(self.data) - 1:
                rtn += "\n"
        return rtn

    def _format_colour(self):
        return "Color: " + " ".join([str(x) for x in self.colour])


class StimulationProtocol:
    """A class implementing a stimulation protocol."""

    def __init__(self, experiment_name="untitled", time_units="Volumes",
                 load=None):
        """Create a stimulation protocol.

        Parameters
        ----------
        experiment_name : str
            the name of the experiment (default="untitled")
        time_units : str
            "Volumes" or "msec" (default="Volumes")
        load : str, optional
            the name of a .prt file to load

        """

        self.clear()
        self._header["Experiment"] = experiment_name
        if time_units not in ["Volumes", "msec"]:
            raise ValueError("")
        self._header["ResolutionOfTime"] = time_units
        if load is not None:
            try:
                self.load(load)
            except:
                raise IOError("Could not read {0}!".format(load))

    def __str__(self):
        return "{0}\n\n{1}".format(self._format_header(),
                                   self._format_conditions())

    @property
    def header(self):
        return self._header

    @property
    def conditions(self):
        return self._conditions

    @property
    def time_units(self):
        return self._header["ResolutionOfTime"]

    @property
    def experiment_name(self):
        return self._header["Experiment"]

    @property
    def event_list(self):
        events = []
        for condition in self.conditions:
            for intervall in condition.data:
                event = [condition.name]
                event.extend(intervall)
                events.append(event)
        return sorted(events, key=lambda x: x[1])

    @property
    def event_names(self):
        return [x[0] for x in self.event_list]

    @property
    def event_onsets(self):
        return [x[1] for x in self.event_list]

    @property
    def event_durations(self):
        if self.time_units == "msec":
            return [x[2] - x[1] for x in self.event_list]
        else:
            return [x[2] - x[1] + 1 for x in self.event_list]

    @property
    def event_weights(self):
        try:
            return [x[3] for x in self.event_list]
        except IndexError:
            return [1 for x in self.event_list]

    @property
    def condition_names(self):
        return [c.name for c in self.conditions]

    @property
    def condition_onsets(self):
        return [c.data[:,0] for c in self.conditions]

    @property
    def condition_durations(self):
        if self.time_units == "msec":
            return [c.data[:,1] - c.data[:,0] for c in self.conditions]
        else:
            return [c.data[:,1] - c.data[:,0] + 1 for c in self.conditions]

    @property
    def condition_weights(self):
        try:
            return [c.data[:,2] for c in self.conditions]
        except IndexError:
            return [np.array([1] * len(c.data)) for c in self.conditions]

    def _format_header(self):
        rtn = ""
        for c,x in enumerate(self.header):
            if c != 9 or (c == 9 and self._header["FileVersion"] == 3):
                if isinstance(self.header[x], list):
                    r,g,b = self.header[x]
                    value = "{0} {1} {2}".format(r,g,b)
                else:
                    value = self.header[x]
                rtn += "{0}:".format(x).ljust(20) + \
                    "{0}".format(value)
                if c < len(self.header) - 1:
                    rtn += "\n"
                if c in [0, 1, 2, 8, 9]:
                    rtn += "\n"
        return rtn

    def _format_conditions(self):
        rtn = ""
        for c, condition in enumerate(self.conditions):
            rtn += str(condition)
            if c < len(self.conditions) - 1:
                rtn += "\n\n"
        return rtn

    def add_condition(self, condition):
        """Add a condition to the stimulation protocol.

        Parameters
        ----------
        condition : Condition object
            the condition to add to the stimulation protocol

        """

        if condition.data.shape[1] > 2:
            self._header["FileVersion"] = 3
            self._header["ParametricWeights"] = 1
            for condition_ in self.conditions:
                if condition_.data.shape[1] < 3:
                    condition_.data = np.append(
                        condition_.data,
                        np.array([(condition_.data.shape[0]) * [1]]).T,
                        axis=1)
        else:
            if self._header["FileVersion"] == 3 and \
               self._header["ParametricWeights"] == 1:
                condition.data = np.append(
                    condition.data,
                    np.array([(condition.data.shape[0]) * [1]]).T,
                    axis=1)

        self._conditions.append(condition)
        self._header["NrOfConditions"] += 1

    def clear(self):
        """Clear Protocol."""
        self._header = OrderedDict([("FileVersion", 2),
                                   ("ResolutionOfTime", "Volumes"),
                                   ("Experiment", "untitled"),
                                   ("BackgroundColor", [0, 0, 0]),
                                   ("TextColor", [255, 255, 255]),
                                   ("TimeCourseColor", [255, 255, 255]),
                                   ("TimeCourseThick", 3),
                                   ("ReferenceFuncColor", [0, 0, 80]),
                                   ("ReferenceFuncThick", 3),
                                   ("ParametricWeights", 0),
                                   ("NrOfConditions", 0)])

        self._conditions = []

    def convert_to_msec(self, tr):
        """Convert time units to milliseconds.

        Parameters
        ----------
        tr : int
            the repetition time in milliseconds

        """

        if self._header["ResolutionOfTime"] == "msec":
            pass
        else:
            for condition in self._conditions:
                for intervall in condition.data:
                    intervall[0] = int((intervall[0] - 1) * tr)
                    intervall[1] = int(intervall[1] * tr)
            self._header["ResolutionOfTime"] = "msec"

    def load(self, filename):
        """Load stimulation protocol from a .prt file.

        This will overwrite current header and conditions!

        Parameters
        ----------
        filename : str
            the name of the .prt file

        """

        
        with open(filename) as f:
            lines = f.readlines()
        lines = [x[0].replace("\t", "  ").strip() for x in groupby(lines)]
        lines = [line for line in lines if line.strip() != ""]
        for counter, line in enumerate(lines):
            if line.startswith('NrOfConditions'):
                break
        for line in lines[:counter]:
            value = line.split(":", 1)[1].strip().split(" ")
            if len(value) > 1:
                try:
                    value = [int(x) for x in value]
                except ValueError:
                    value = " ".join(value)
            else:
                try:
                    value = int(value[0])
                except ValueError:
                    value = value[0]
            self._header[line.split(":", 1)[0].strip()] = value

        def int_or_float(x):
            try:
                return int(x)
            except:
                return float(x)

        conds = conds = int(lines[counter].split(":", 1)[1].strip())
        counter = counter+1
        for i in range(conds):
            try:
                name = lines[counter].strip()
                start = counter + 2
                number_events = int(lines[counter+1])
                end = start + number_events
                data = []
                for x in range(start, end):
                    data.append([int_or_float(i) for i in lines[x].split(" ") if i])
                colour = [int(x) for x in lines[end][7:].split(" ")]
                self.add_condition(Condition(name, data, colour))
            except IndexError:
                pass
            counter = counter + number_events + 3

    def save(self, filename):
        """Save stimulation protocol to a .prt file.

        Parameters
        ----------
        filename : str
            the name of the .prt file

        """

        if not os.path.splitext(filename)[-1].lower() == ".prt":
            filename += ".prt"

        with open(filename, 'w') as f:
            f.write("\n")
            f.write(self._format_header() + "\n")
            f.write("\n")
            f.write(self._format_conditions())
