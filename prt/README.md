# PRT

Create, read and write `.prt` files.

## Usage examples

** Build a stimulation protocol from scratch:** 
```python
from brainvoyagertools import prt

prt = prt.StimulationProtocol(experiment_name="MyExperiment")
prt.add_condition(prt.Condition("Rest", [[x+1,x+8] for x in range(1,80,16], colour=[255,0,0]))
prt.add_condition(prt.Condition("Task", [[x+1,x+8] for x in range(8,80,16], colour=[0,255,0]))
prt.save("MyExperiment.prt")
```

**Change time units to milliseconds and add condition to other protocol:**
```python
prt = prt.StimulationProtocol(load="MyExperiment.prt")
prt.convert_to_msec(tr=2000)
prt2 = prt.StimulationProtocol(experiment_name="MyExperiment2", time_units="msec")
prt2.add_condition(prt.conditions[-1])
prt2.save("MyExperiment2.prt")
```
