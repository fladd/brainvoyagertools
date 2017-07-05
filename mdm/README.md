# MDM

Create, read and write `.mdm` files.

## Usage examples

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
