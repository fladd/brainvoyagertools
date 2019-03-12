# VOI

Create, read and write `.voi` files.

## Usage examples

**Save a single a VOI with three coordinates :**
```python
from brainvoyagertools import voi

vois = voi.VOIsDefinition(reference_space="MNI")
vois.add_voi(voi.VOI("VOI_1", [[15, 30, 40], [16, 30, 40]]
vois.save("my_voi.voi")
```
