#!/usr/bin/env python
"""
eval_lik.py -- evaluate a likelihood function on a set of 
trajectories

"""
import numpy as np 
import pandas as pd 

# Calculate jumps for a set of trajectories
from .utils import tracks_to_jumps 

# Split a set of trajectories into smaller trajectories
from .utils import split_jumps

# Raw likelihood functions
from .lik import (
    gamma_likelihood,
    rbme_likelihood,
    fbme_likelihood
)

# Available raw likelihood functions
LIKELIHOODS = {
    "gamma": gamma_likelihood,
    "rbme": rbme_likelihood,
    "fbme": fbme_likelihood
}

# Convert trajectories into a jump-based ndarray format
from .utils import tracks_to_jumps

# Correct for defocalization
from .defoc import defoc_corr

def eval_likelihood(tracks, likelihood="gamma", splitsize=None, n_gaps=0,
    max_jumps_per_track=None, start_frame=None, pixel_size_um=0.16,
    frame_interval=0.00748, scale_by_jumps=True, dz=None, pos_cols=["y", "x"],
    **kwargs):
    """
    Evaluate a likelihood function on some trajectories, returning
    the results in a matrix indexed to each trajectory and each 
    likelihood parameter.

    note on splitsize's effect on track indices
    -------------------------------------------

        Each trajectory has a unique index in the original *tracks*
        dataframe. If *splitsize* is set, then these trajectories 
        are broken apart into smaller trajectories, which are all
        assigned new indices.

        As a result, the number of trajectories in the output does 
        not necessarily equal the number of unique trajectories in
        the input dataframe.

        The map between old and new trajectory indices is recorded
        in the *orig_track_indices* output of this function. If 
        *i* is the index of one of the split trajectories, then 
        orig_track_indices[i] is the index of the source trajectory
        in the origin *tracks* dataframe.

    args
    ----
        tracks              :   pandas.DataFrame

        likelihood          :   str, "gamma", "rbme", or "fbm"

        splitsize           :   int, the length of the subsampled
                                trajectories in number of jumps

        n_gaps              :   int, the number of gaps tolerated 
                                during tracking. Note that only "gamma"
                                likelihoods support gaps. 

        max_jumps_per_track :   int, do not consider more than this
                                many jumps per trajectory

        frame_interval      :   float, frame interval in seconds

        scale_by_jumps      :   bool, scale the likelihoods for 
                                each trajectory by the number of 
                                jumps in that trajectory

        dz                  :   focal depth in microns

        pos_cols            :   list of str, the columns in *tracks*
                                with spatial coordinates in pixels

        kwargs              :   to the likelihood function

    returns
    -------
        (
            ndarray, the likelihood function. This always has the 
                shape (n_tracks, ...), with the second axes onward
                corresponding to different likelihood parameters;

            1D ndarray of shape (n_tracks,), the number of jumps in
                each trajectory;

            1D ndarray of shape (n_tracks,), the indices of each
                new trajectory in the origin dataframe;

            tuple of 1D ndarray, the parameters corresponding to 
                axes 1 onward for the likelihood

        )

    """
    # Cannot use gaps if using RBME or FBME likelihood
    if (n_gaps > 0) and (likelihood in ["rbme", "fbme"]):
        raise RuntimeError("Cannot currently use gapped tracking with " \
            "rbme or fbme likelihoods")

    # Calculate all the vector jumps in this set of trajectories
    jumps = tracks_to_jumps(tracks, start_frame=start_frame, pos_cols=pos_cols,
        pixel_size_um=pixel_size_um, n_gaps=n_gaps)

    # If desired, split the trajectories into smaller trajectories
    orig_track_indices = jumps[:,1].astype(np.int64)
    if (not splitsize is None) and (not splitsize is np.inf):
        jumps[:,1] = split_jumps(jumps, splitsize=splitsize)

    # Calculate likelihoods for each trajectory
    L, n_jumps, track_indices, support = LIKELIHOODS[likelihood](jumps,
        frame_interval=frame_interval, max_jumps_per_track=max_jumps_per_track,
        **kwargs)

    # Account for defocalization
    if (not dz is None) and (not dz is np.inf):
        L = defoc_corr(L, support, likelihood=likelihood, 
            frame_interval=frame_interval, dz=dz)

    # Scale by the number of jumps in each trajectory, if desired
    if scale_by_jumps:
        L = (L.T * n_jumps).T 

    return L, n_jumps, orig_track_indices, support
