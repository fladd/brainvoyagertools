# SDM

Create, read and write `.sdm` files.

## Usage examples

**Build a design matrix from scratch:**
```
from brainvoyagertools import sdm

design = sdm.DesignMatrix()
design.add_predictor(sdm.Predictor("FirstHalf", 100*[1] + 100*[0], [255,0,0]))
design.add_predictor(sdm.Predictor("SecondHalf", 100*[0] + 100*[1], [0,255,0]))
for p in design.predictors:
    p.convolve_with_hrf(tr=2.0)
design.save("design.sdm")
```

**Add z-transformed motion regressors and their first and second derivatives:**
```
from brainvoyagertools import sdm

design = sdm.DesignMatrix("design.sdm")
motion = sdm.DesignMatrix("3DMC.sdm")
for p in motion.predictors:
    p.ztransform()
    design.add_confound_predictor(p)
    design.add_confound_predictor(p.get_derivative(1))
    design.add_confound_predictor(p.get_derivative(2))
design.add_constant()
design.save("design_and_motion.sdm")
```

