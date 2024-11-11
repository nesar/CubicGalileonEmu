# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/04_mcmc.ipynb.

# %% auto 0
__all__ = ['ln_prior', 'ln_like', 'ln_prob', 'chain_init', 'define_sampler', 'do_mcmc', 'mcmc_results']

# %% ../nbs/04_mcmc.ipynb 3
import numpy as np
import emcee 
import time
from .emu import emu_redshift

# %% ../nbs/04_mcmc.ipynb 4
def ln_prior(theta, params_list):
    pdf_sum = 0
    for p, param in zip(theta, params_list):
        if not (param[2] < p < param[3]):
            return -np.inf
        p_mu = 0.5 * (param[3] - param[2]) + param[2]
        p_sigma = 1 * (param[3] - p_mu)
        pdf_sum += np.log(1.0 / (np.sqrt(2 * np.pi) * p_sigma)) - 0.5 * (p - p_mu) ** 2 / p_sigma ** 2
    return pdf_sum

# %% ../nbs/04_mcmc.ipynb 5
def ln_like(theta, 
            redshift,
            x_grid, 
            sepia_model_list, 
            sepia_data_list,
            z_all, 
            x, 
            y, 
            yerr
            ):
      
#     p1, p2, p3, p4, p5 = theta
#     new_params = np.array([p1, p2, p3, p4, p5, redshift])[np.newaxis, :]

#     new_params = np.array(theta + [redshift])[np.newaxis, :]
    new_params = np.append( np.array(theta), [redshift] )[np.newaxis, :]

#     print('Theta', len(theta))
#     print('New params', new_params.shape)
        
    model_grid, model_err_grid = emu_redshift(new_params, sepia_model_list, sepia_data_list, z_all)
        
    model = np.interp(x, x_grid, model_grid[:, 0])
    # model_err = np.interp(x, x_grid, model_err_grid[:, 0, 0])
    
    # model_err = np.interp(x, x_grid, model_err_grid[:, 0])
  
    # sigma2 = yerr**2  + model_err
    sigma2 = yerr**2 # + model_var

    ll = -0.5 * np.sum((y - model)** 2 / sigma2 )
    
    return ll


# %% ../nbs/04_mcmc.ipynb 6
def ln_prob(theta, 
            redshift,
            params_list, 
            x_grid, 
            sepia_model_list, 
            sepia_data_list,
            z_all, 
            x, 
            y, 
            yerr
            ):
    
    lp = ln_prior(theta, params_list)
    if not np.isfinite(lp):
        return -np.inf
    return lp + ln_like(theta, redshift, x_grid, sepia_model_list, sepia_data_list, z_all, x, y, yerr)

# %% ../nbs/04_mcmc.ipynb 7
def chain_init(params_list, ndim, nwalkers):
    pos0 = [[param[1] * 1.0 for param in params_list] + 1e-3 * np.random.randn(ndim) for _ in range(nwalkers)]
    return pos0

# %% ../nbs/04_mcmc.ipynb 8
def define_sampler(redshift, 
                   ndim, 
                   nwalkers, 
                   params_list, 
                   x_grid, 
                   sepia_model_list, 
                   sepia_data_list,
                   z_all, 
                   x, 
                   y, 
                   yerr
                   ):
    
    sampler = emcee.EnsembleSampler(nwalkers, ndim, ln_prob, args=(redshift, params_list, x_grid, sepia_model_list, sepia_data_list, z_all, x, y, yerr))
    return sampler

# %% ../nbs/04_mcmc.ipynb 9
def do_mcmc(sampler, 
            pos, 
            nrun, 
            ndim,
            if_burn=False
            ):
    
    print('Burn-in phase') if if_burn else print('Sampling phase')

    time0 = time.time()
    pos, prob, state = sampler.run_mcmc(pos, nrun)

    time1 = time.time()
    print('time (minutes):', (time1 - time0)/60. )

    samples = sampler.chain[:, :, :].reshape((-1, ndim))

    if if_burn: 
        sampler.reset()


    if True:

        # We'll track how the average autocorrelation time estimate changes
        index = 0
        autocorr = np.empty(nrun)

        # This will be useful to testing convergence
        old_tau = np.inf

        # Now we'll sample for up to max_n steps
        for sample in sampler.sample(pos, iterations=nrun, progress=True):
            # Only check convergence every 10 steps
            if sampler.iteration % 100:
                continue

            # Compute the autocorrelation time so far
            # Using tol=0 means that we'll always get an estimate even
            # if it isn't trustworthy
            tau = sampler.get_autocorr_time(tol=0)
            autocorr[index] = np.mean(tau)
            index += 1

            # Check convergence
            converged = np.all(tau * 100 < sampler.iteration)
            converged &= np.all(np.abs(old_tau - tau) / tau < 0.01)
            if converged:
                break
            old_tau = tau
            # print(index)

    return pos, prob, state, samples, sampler, autocorr, index

# %% ../nbs/04_mcmc.ipynb 10
def mcmc_results(samples):
    results = list(map(lambda v: (v[1], v[2] - v[1], v[1] - v[0]), zip(*np.percentile(samples, [16, 50, 84], axis=0))))
    print('mcmc results:', ' '.join(str(result[0]) for result in results))
    return tuple(result[0] for result in results)
