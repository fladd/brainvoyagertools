# PRT

Create, read and write `.prt` files.

## Usage examples

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
