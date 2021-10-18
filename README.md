# spagl
State arrays for resolving fast mixtures of Brownian motions in short single particle trajectories

**Note: spagl is an early prototype for the state array algorithm. We highly recommend you use the production version, see https://github.com/alecheckert/saspt.**

## What does it do?

`spagl` represents single particle tracking (SPT) data as
an "aggregate likelihood" function, which is the sum of a
likelihood function for all trajectories in a dataset. This
is useful to get a rough idea of things like the trajectory
diffusion coefficient, localization error, and cell-to-cell
variability in a dataset.

`spagl` includes tools to plot the likelihood function as a 
function of cell, space, or time - see examples below.

## What doesn't it do?

`spagl` does not do localization and tracking. It assumes that 
you have already produced a high-quality set of trajectories
from your raw data. 

`spagl` does not check the quality of your data. It will analyze
all data you give it.

`spagl` expects the user to understand the parameters for their own
experiment, including the frame interval, microscope focal depth, 
and pixel size. Some likelihood functions (for instance, `gamma` or
`fbme`) assume that you have measured the approximate localization error
of the microscope in advance.

## Likelihood functions supported

Four likelihood functions are currently supported:

 - `gamma`: the gamma approximation to the likelihood function for 
    regular Brownian motion with localization error. This is obtained by
    taking the RBME likelihood function and neglecting the off-diagonal
    covariance terms that result from localization error. It's the
    simplest model and the fastest to compute, but also the least accurate.
 - `rbme`: bivariate likelihood function for diffusion coefficient
    and localization error.
 - `rbme_marginal`: regular Brownian motion with localization error,
    marginalized on the localization error part. The result is a univariate
    likelihood function dependent on the diffusion coefficient. Similar
    to `gamma`, but far more stable in situations where the localization
    error is unknown or cannot be assumed to be constant between cells
    or molecular subpopulations.
 - `fbme`: fractional Brownian motion with localization error. The free
    parameters are diffusion coefficient and Hurst parameter, and the 
    localization error is assumed to be constant.

See below for usage.

## Dependencies

`numpy`, `scipy`, `pandas`, `matplotlib`, `seaborn`, `matplotlib_scalebar`, and `tqdm`. 

## Install

Clone the repository, then run
```
    python setup.py develop
```

The `develop` option will allow you to pull new versions of the repository as they 
become available.

## Expected input

All of the `spagl` functions operate on `pandas.DataFrame` or CSVs with trajectories.
Each row of the CSV is expected to correspond to a single detection, and the CSVs
are expected to contain the following columns at minimum:

 - `trajectory`: the index of the trajectory to which this detection belongs
 - `frame`: the frame index
 - `y`: the y-coordinate, **in pixels**
 - `x`: the x-coordinate, **in pixels**

See the docstring for each function for more detail.

## Examples

A few different use cases of `spagl` are included in the `samples` folder of this
repository. These include:

 - plot the aggregate likelihood for a collection of files
    (`sample_script_by_file.py`)
 - plot the aggregate likelihood as a function of the spatial trajectory position
    (`sample_script_spatial.py`)
 - plot the aggregate likelihood as a function of time (`sample_script_temporal.py`)
 - show the aggregate likelihood function for both diffusion coefficient and 
    localization error (`sample_script_rbme.py`)
 - estimate the underlying state occupations from the aggregate likelihood function
    using a fixed state sampler (`sample_script_fss.py`)

All of the required sample data is included in `samples/sample_track_csvs`. The
samples are intended to be easily modified to target user data. 

