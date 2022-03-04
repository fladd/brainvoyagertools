# BrainVoyager Tools
An object-oriented approach to create, read and write common plain-text BrainVoyager input formats with Python.

Currently supported:
* .ctr
* .mdm
* .prt
* .sdm
* .voi


## Installation
BrainVoyager Tools can be easily installed with pip:
```
pip install brainvoyagertools
```

## Usage
### ctr
**Build a contrast definition from scratch:**
```python
from brainvoyagertools import ctr

contrasts = ctr.ContrastsDefinition()
contrasts.add_contrast(ctr.Contrast("All vs. Baseline", [1, 1, 0]))
contrasts.add_contrast(ctr.Contrast("House vs. Faces", [1, -1, 0]))
contrasts.save("contrasts.ctr")
```

**Add contrasts to contrast definition file:**
```python
from brainvoyagertools import ctr

contrasts = ctr.ContrastsDefinition(load="contrasts.ctr")
contrasts.add_contrast(ctr.Contrast("Faces vs. Houses", [-1, 1, 0]))
contrasts.save("contrasts2.ctr")
```

### mdm
**Build a design matrix from scratch:**
```python
from brainvoyagertools import mdm

design = mdm.DesignMatrix()
design.add_study(mdm.Study("path/to/MyStudy1.vtc", "path/to/MyStudy1.sdm")
design.add_study(mdm.Study("path/to/MyStudy2.vtc", "path/to/MyStudy2.sdm")
design.add_study(mdm.Study("path/to/MyStudy3.vtc", "path/to/MyStudy3.sdm")
design.add_study(mdm.Study("path/to/MyStudy4.vtc", "path/to/MyStudy4.sdm")
design.add_study(mdm.Study("path/to/MyStudy5.vtc", "path/to/MyStudy5.sdm")
design.add_study(mdm.Study("path/to/MyStudy6.vtc", "path/to/MyStudy6.sdm")
design.add_study(mdm.Study("path/to/MyStudy7.vtc", "path/to/MyStudy7.sdm")
design.add_study(mdm.Study("path/to/MyStudy8.vtc", "path/to/MyStudy8.sdm")
design.add_study(mdm.Study("path/to/MyStudy9.vtc", "path/to/MyStudy9.sdm")
design.add_study(mdm.Study("path/to/MyStudy10.vtc", "path/to/MyStudy10.sdm")
design.rfx_glm = True
design.transformation = 'z'
design.separate_predictors = True
design.save("design.mdm")
```

**Also works for MTC data:**
```python
from brainvoyagertools import mdm

design = mdm.DesignMatrix()
design.add_study(mdm.Study(["path/to/MyStudy1.ssm", "path/to/MyStudy1.mtc"], "path/to/MyStudy1.sdm")
design.add_study(mdm.Study(["path/to/MyStudy2.ssm", "path/to/MyStudy2.mtc"], "path/to/MyStudy2.sdm")
design.add_study(mdm.Study(["path/to/MyStudy3.ssm", "path/to/MyStudy3.mtc"], "path/to/MyStudy3.sdm")
design.save("design2.mdm")
```

### prt
**Build a stimulation protocol from scratch:** 
```python
from brainvoyagertools import prt

protocol = prt.StimulationProtocol(experiment_name="MyExperiment")
protocol.add_condition(prt.Condition("Rest", [[x+1,x+8] for x in range(1,80,16], colour=[255,0,0]))
protocol.add_condition(prt.Condition("Task", [[x+1,x+8] for x in range(8,80,16], colour=[0,255,0]))
protocol.save("MyExperiment.prt")
```

**Change time units to milliseconds and add condition to other protocol:**
```python
from brainvoyagertools import prt

protocol = prt.StimulationProtocol(load="MyExperiment.prt")
protocol.convert_to_msec(tr=2000)
protocol2 = prt.StimulationProtocol(experiment_name="MyExperiment2", time_units="msec")
protocol2.add_condition(prt.conditions[-1])
protocol2.save("MyExperiment2.prt")
```

**Add combination of conditions into new protocol:**
```python
from brainvoyagertools import prt

protocol = prt.StimulationProtocol(load="MyExperiment.prt")
protocol2 = prt.StimulationProtocol(experiment_name="MyExperiment3"
protocol2.add_condition(protocol.condition[0] + protocol.conditions[1])
protocol2.save("MyExperiment3.prt")
```

### sdm
**Build a design matrix from scratch:**
```python
from brainvoyagertools import sdm

design = sdm.DesignMatrix()
design.add_predictor(sdm.Predictor("FirstHalf", 100*[1] + 100*[0], colour=[255,0,0]))
design.add_predictor(sdm.Predictor("SecondHalf", 100*[0] + 100*[1], colour=[0,255,0]))
for p in design.predictors:
    p.convolve_with_hrf(tr=2000)
design.save("design.sdm")
```

**Add z-transformed motion regressors, their first and second derivatives, and a constant:**
```python
from brainvoyagertools import sdm

design = sdm.DesignMatrix(load="design.sdm")
motion = sdm.DesignMatrix(load="3DMC.sdm")
for p in motion.predictors:
    p.ztransform()
    design.add_confound_predictor(p)
    design.add_confound_predictor(p.get_derivative(1))
    design.add_confound_predictor(p.get_derivative(2))
design.add_constant()
design.save("design_and_motion.sdm")
```

**Define predictors from a prt file:**
```python
from brainvoyagertools import prt, sdm

protocol = prt.StimulationProtocol(load="protocol.prt")
design = sdm.DesignMatrix()
design.define_predictors(protocol, data_points=400, tr=2000)
design.add_constant()
design.save("design.sdm")
```

### voi
**Save a single a VOI with three coordinates :**
```python
from brainvoyagertools import voi

vois = voi.VOIsDefinition(reference_space="MNI")
vois.add_voi(voi.VOI("VOI_1", [[15, 30, 40], [16, 30, 40]]
vois.save("my_voi.voi")
```
