#!/usr/bin/env python3

# avoid using Xwindow
import matplotlib
matplotlib.use("agg")

from tf_pwa.config_loader import ConfigLoader, MultiConfig
from pprint import pprint
from tf_pwa.utils import error_print
import tensorflow as tf
import json

# for my_cut
from tf_pwa.config_loader.data import register_data_mode, MultiData
from tf_pwa.data import data_mask

# for single plot chi2/ndf calculation
import os.path
import sys
import numpy as np
from tf_pwa.adaptive_bins import AdaptiveBound, cal_chi2
from tf_pwa.data import data_index


def cal_chi2_single_plot(
    res = "BD", config_file = "config.yml", init_params = "final_params.json", nbins = 400
):
    config = ConfigLoader(config_file)
    data = my_cut(config.get_data("data")[0], res)
    phsp = my_cut(config.get_data("phsp")[0], res)
    bg = my_cut(config.get_data("bg")[0], res)
    config.set_params(init_params)
    
    fig_idx = config.get_data_index(
        "mass", "R_" + res
    )
    data_idx = [fig_idx]
    data_cut = np.array([data_index(data, idx) for idx in data_idx])
    amp_weight = config.get_amplitude()(phsp).numpy()
    phsp_cut = np.array([data_index(phsp, idx) for idx in data_idx])
    phsp_slice = np.concatenate(
        [np.array(phsp_cut), [amp_weight]], axis = 0
    )
    adapter = AdaptiveBound(data_cut, [[nbins]])
    phsps = adapter.split_data(phsp_slice)
    datas = adapter.split_data(data_cut)
    bound = adapter.get_bounds()
    if bg is not None:
        bg_weight = config._get_bg_weight(display=False)[0][0]
        if isinstance(bg_weight, float): 
            bg_cut = np.array([data_index(bg, idx) for idx in data_idx])
            int_norm = (
                data_cut.shape[-1] - bg_cut.shape[-1] * bg_weight
            ) / np.sum(amp_weight)
        elif isinstance(bg_weight, np.ndarray):
            int_norm = (
                data_cut.shape[-1] + np.sum(bg_weight)
            ) / np.sum(amp_weight)
        else:
            print('not supported type of bg_weight, please check!')
            exit()
    else:
        int_norm = data_cut.shape[-1] / np.sum(amp_weight)
    print("int norm:", int_norm)
    if bg is not None and isinstance(bg_weight, np.ndarray):
        bg_cut = np.array([data_index(bg, idx) for idx in data_idx])
        tag = set(bg_weight)
        start = 0
        stop = 0
        bg_cut_tag = []
        for t in tag:
            seg = len(bg_weight[bg_weight == t])
            stop += seg
            bg_cut_tag.append(np.array([bg_cut[0][start:stop]]))
            start += seg
        bgs_tag = []
        for t, bg_tag in zip(tag, bg_cut_tag):
            bgs_tag.append([t, adapter.split_data(bg_tag)])
    numbers = []
    for i, bnd in enumerate(bound):
        ndata = datas[i].shape[-1]
        nmc = np.sum(phsps[i][1]) * int_norm
        if bg is not None:
            if isinstance(bg_weight, int): 
                bgs = adapter.split_data(bg_cut)
                nmc += bgs[i].shape[-1] * bg_weight
            elif isinstance(bg_weight, np.ndarray):
                    for l in bgs_tag:
                        t, bgs = l
                        nmc -= bgs[i].shape[-1] * t
            else:
                print('not supported type of bg_weight, please check!')
        numbers.append((ndata, nmc))
    return cal_chi2(numbers, config.get_ndf())


def my_cut(data, res):
    if res == "BD": mass = data.get_mass("(B, D)")
    elif res == "CD": mass = data.get_mass("(C, D)")
    cut = mass > 2.35
    return data_mask(data, cut)


@register_data_mode("my_cut")
class MyCut(MultiData):
    def get_data(self, *arg, **kwarg):
        data = super(MyCut, self).get_data(*arg, **kwarg)
        if data is None: return None
        else: return [my_cut(i) for i in data]


# examples of custom particle model
from tf_pwa.amp import Particle, register_particle


@register_particle("New")
class NewParticle(Particle):
    """example Particle model define, can be used in config.yml as `model: New`"""
    def init_params(self):
        # self.a = self.add_var("a")
        pass
    def get_amp(self, data, data_extra, **kwargs):
        # m = data["m"]
        # q = data_extra[self.outs[0]]["|q|"]
        # a = self.a()
        return 1.0


def json_print(dic):
    """print parameters as json"""
    s = json.dumps(dic, indent=2)
    print(s, flush=True)


def fit(config_file="config.yml", init_params="init_params.json", method="BFGS", res = "BD", nbins = 50):
    """
    simple fit script 
    """
    # load config.yml
    config = ConfigLoader(config_file)
    
    # set initial parameters if have
    try:
        config.set_params(init_params)
        print("using {}".format(init_params))
    except Exception as e:
        if str(e) != "[Errno 2] No such file or directory: 'init_params.json'":
            print(e)
        print("\nusing RANDOM parameters", flush=True)
    
    # print("\n########### initial parameters")
    # json_print(config.get_params())

    # fit
    data, phsp, bg, inmc = config.get_all_data()
    fit_result = config.fit(batch=65000, method=method)
    json_print(fit_result.params)
    fit_result.save_as("final_params.json")

    # calculate parameters error
    fit_error = config.get_params_error(fit_result, batch=13000)
    fit_result.set_error(fit_error)
    fit_result.save_as("final_params.json")
    pprint(fit_error)

    chi2_ndf = cal_chi2_single_plot(res, config_file, "final_params.json", nbins)
    fit_result.chi2_ndf = chi2_ndf[-2]/chi2_ndf[-1]
    fit_result.save_as("final_params.json")

    print("\n########## fit results:")
    for k, v in config.get_params().items():
        print(k, error_print(v, fit_error.get(k, None)))

    # plot partial wave distribution
    config.plot_partial_wave(fit_result, plot_pull=True)

    # calculate fit fractions
    phsp_noeff = config.get_phsp_noeff()
    fit_frac, err_frac = config.cal_fitfractions({}, phsp_noeff)

    print("########## fit fractions")
    fit_frac_string = ""
    for i in fit_frac:
        if isinstance(i, tuple):
            name = "{}x{}".format(*i)
        else:
            name = i
        fit_frac_string += "{} {}\n".format(name, error_print(fit_frac[i], err_frac.get(i, None)))
    print(fit_frac_string)
    #from tf_pwa.utils import frac_table
    #frac_table(fit_frac_string)


def fit_combine(config_file=["config.yml"], init_params="init_params.json", method="BFGS", total_same=False):
    """fit with multiply config.yml"""
    config = MultiConfig(config_file, total_same=total_same)
    try:
        config.set_params(init_params)
        print("using {}".format(init_params))
    except Exception as e:
        if str(e) != "[Errno 2] No such file or directory: 'init_params.json'":
            print(e)
        print("\nusing RANDOM parameters")
    
    # print("\n########### initial parameters")
    # pprint = lambda dic: print(json.dumps(dic, indent=2))
    # pprint(config.get_params())
    
    fit_result = config.fit(method=method, batch=65000)
    pprint(fit_result.params)

    fit_error = config.get_params_error(fit_result, batch=13000)
    fit_result.set_error(fit_error)
    fit_result.save_as("final_params.json")
    pprint(fit_error)
    
    print("\n########## fit results:")
    from tf_pwa.applications import fit_fractions
    for k, v in fit_result.params.items():
        print(k, error_print(v, fit_error.get(k, None)))

    for i, c in enumerate(config.configs):
        c.plot_partial_wave(fit_result, prefix="figure/s{}_".format(i))

    print("########## fit fractions:")
    mcdata = config.configs[0].get_phsp_noeff()
    fit_frac, err_frac = fit_fractions(config.configs[0].get_amplitude(), mcdata, config.inv_he, fit_result.params)
    fit_frac_string = ""
    for i in fit_frac:
        if isinstance(i, tuple):
            name = "{}x{}".format(*i) # interference term
        else:
            name = i # fit fraction
        fit_frac_string += "{} {}\n".format(name, error_print(fit_frac[i], err_frac.get(i, None)))
    print(fit_frac_string)
    #from frac_table import frac_table
    #frac_table(fit_frac_string)

def main():
    """entry point of fit. add some arguments in commond line"""
    import argparse
    parser = argparse.ArgumentParser(description="simple fit scripts")
    parser.add_argument("--no-GPU", action="store_false", default=True, dest="has_gpu")
    parser.add_argument("-c", "--config", default="config.yml", dest="config")
    parser.add_argument("-i", "--init_params", default="init_params.json", dest="init")
    parser.add_argument("-m", "--method", default="BFGS", dest="method")
    parser.add_argument("-l", "--loop", type=int, default=1, dest="loop")
    parser.add_argument("-r", "--res", default = "BD", dest = "res")
    parser.add_argument("-b", "--bins", default = 200, dest = "nbins")
    parser.add_argument("--total-same", action="store_true", default=False, dest="total_same")
    results = parser.parse_args()
    config = results.config.split(",")
    res = results.res
    nbins = int(results.nbins)
    if results.has_gpu:
        devices = "/device:GPU:0"
    else:
        devices = "/device:CPU:0"
    with tf.device(devices):
        for i in range(results.loop):
            if len(config) > 1:
                fit_combine(config, results.init, results.method, results.total_same)
            else:
                fit(results.config, results.init, results.method, res, nbins)
            print("", flush=True)


if __name__ == "__main__":
    main()
