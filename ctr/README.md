# CTR

Create, read and write `.ctr` files.

## Usage examples

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

