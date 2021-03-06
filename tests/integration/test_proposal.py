# -*- coding: utf-8 -*-

from __future__ import division, print_function

import numpy as np
from scipy import stats

import emcee

__all__ = ["_test_normal", "_test_uniform"]


def normal_log_prob(params):
    return -0.5 * np.sum(params**2)


def uniform_log_prob(params):
    if np.any(params > 1) or np.any(params < 0):
        return -np.inf
    return 0.0


def _test_normal(proposal, ndim=1, nwalkers=32, nsteps=2000, seed=1234,
                 check_acceptance=True):
    # Set up the random number generator.
    np.random.seed(seed)

    # Initialize the ensemble and proposal.
    coords = np.random.randn(nwalkers, ndim)

    sampler = emcee.EnsembleSampler(nwalkers, ndim, normal_log_prob,
                                    moves=proposal)
    sampler.run_mcmc(coords, nsteps)

    # Check the acceptance fraction.
    if check_acceptance:
        acc = sampler.acceptance_fraction
        assert np.all((acc < 0.9) * (acc > 0.1)), \
            "Invalid acceptance fraction\n{0}".format(acc)

    # Check the resulting chain using a K-S test and compare to the mean and
    # standard deviation.
    samps = sampler.get_chain(flat=True)
    mu, sig = np.mean(samps, axis=0), np.std(samps, axis=0)
    assert np.all(np.abs(mu) < 0.08), "Incorrect mean"
    assert np.all(np.abs(sig - 1) < 0.05), "Incorrect standard deviation"

    if ndim == 1:
        ks, _ = stats.kstest(samps[:, 0], "norm")
        assert ks < 0.05, "The K-S test failed"


def _test_uniform(proposal, nwalkers=32, nsteps=2000, seed=1234):
    # Set up the random number generator.
    np.random.seed(seed)

    # Initialize the ensemble and proposal.
    coords = np.random.rand(nwalkers, 1)

    sampler = emcee.EnsembleSampler(nwalkers, 1, normal_log_prob,
                                    moves=proposal)
    sampler.run_mcmc(coords, nsteps)

    # Check the acceptance fraction.
    acc = sampler.acceptance_fraction
    assert np.all((acc < 0.9) * (acc > 0.1)), \
        "Invalid acceptance fraction\n{0}".format(acc)

    # Check that the resulting chain "fails" the K-S test.
    samps = sampler.get_chain(flat=True)
    np.random.shuffle(samps)
    ks, _ = stats.kstest(samps[::100], "uniform")
    assert ks > 0.1, "The K-S test failed"
