import argparse
import sys
import os
import subprocess

from astropy.io import ascii
from matplotlib import pyplot as plt
import numpy as np
from lmfit import Model, report_fit


def get_freq(psredit_result):
    return float(str(psredit_result).split(" ")[1].split("=")[1].replace("\\n", "").replace("'", ""))


def profile_function(x, A, alpha, thata_min):
    return A * (x ** (-alpha)) + thata_min
    

def gauss(x, mu, sigma, amplitude):
    return amplitude * (
        (np.exp((-1 / 2) * ((x - mu) ** 2 / sigma ** 2))))


def gauss2(x, mu1, sigma1, amplitude1, mu2, sigma2, amplitude2):
    return gauss(x, mu1, sigma1, amplitude1) + \
        gauss(x, mu2, sigma2, amplitude2)


def gauss3(x, mu1, sigma1, amplitude1, mu2, sigma2, amplitude2, mu3, sigma3, amplitude3):
    return gauss(x, mu1, sigma1, amplitude1) + \
        gauss(x, mu2, sigma2, amplitude2) + \
        gauss(x, mu3, sigma3, amplitude3)


def gauss4(x, mu1, sigma1, amplitude1, mu2, sigma2, amplitude2, mu3, sigma3, amplitude3, mu4, sigma4, amplitude4):
    return gauss(x, mu1, sigma1, amplitude1) + \
        gauss(x, mu2, sigma2, amplitude2) + \
        gauss(x, mu3, sigma3, amplitude3) + \
        gauss(x, mu4, sigma4, amplitude4)


def gauss5(x, mu1, sigma1, amplitude1, mu2, sigma2, amplitude2, mu3, sigma3, amplitude3, mu4, sigma4,
           amplitude4, mu5, sigma5, amplitude5):
    return gauss(x, mu1, sigma1, amplitude1) + \
        gauss(x, mu2, sigma2, amplitude2) + \
        gauss(x, mu3, sigma3, amplitude3) + \
        gauss(x, mu4, sigma4, amplitude4) + \
        gauss(x, mu5, sigma5, amplitude5)
        
        
def gauss6(x, mu1, sigma1, amplitude1, mu2, sigma2, amplitude2, mu3, sigma3, amplitude3, mu4, sigma4,
           amplitude4, mu5, sigma5, amplitude5, mu6, sigma6, amplitude6):
    return gauss(x, mu1, sigma1, amplitude1) + \
        gauss(x, mu2, sigma2, amplitude2) + \
        gauss(x, mu3, sigma3, amplitude3) + \
        gauss(x, mu4, sigma4, amplitude4) + \
        gauss(x, mu5, sigma5, amplitude5) + \
        gauss(x, mu6, sigma6, amplitude6)


def get_error(results, variable):
    try:
        error = np.float128(str(results.params[variable]).split(",")[1].split("+/-")[1])
    except:
        error = 0
    return error


def main(pulsar, componet_count):
    plt.style.use("plot.style")
    path = "/mnt/LOFAR0/pulsars/LuMP_LV614/pulsar_data_processed/" + pulsar + "/"
    
    paas_m_files = sorted([file for file in os.listdir(path) if file.endswith(".paas.m")])
    paas_txt_files = sorted([file for file in os.listdir(path) if file.endswith(".paas.txt")])
    fscrs_files = sorted([file for file in os.listdir(path) if file.endswith(".fscr")])
    
    print(paas_m_files)
    print("\n\n")
    print(paas_txt_files)
    print("\n\n")
    print(fscrs_files)
    print("\n\n")
    
    print(len(paas_m_files), len(paas_txt_files), len(fscrs_files))
    
    colors = []
    symbols = []
    
    telescopes = []
    for tmp in paas_txt_files:
        if "combine_lanes" in tmp:
            colors.append("r")
            symbols.append("s")
            telescopes.append("LV614")
        elif "nuppi" in tmp:
            colors.append("b")
            symbols.append("o")
            telescopes.append("NRT")
        else:
            colors.append("g")
            symbols.append("D")
            telescopes.append("Nenufar")

    phase_diff = []
    phase_diff_errors = []
    
    
    frequency = np.array([get_freq(subprocess.check_output(["psredit", "-c", "freq", path + fscrs_file])) for fscrs_file in fscrs_files])
    for sb in range(0, len(paas_m_files)):
        #if sb == 6:
            #continue
            
        print(sb)
        fig1, ax1 = plt.subplots(nrows=1, ncols=2, figsize=(8, 8), dpi=90)

        ax1[0].set_title("SB " + str(sb) + " paas fit")
        ax1[1].set_title("SB " + str(sb) + " init gauss")

        paas_txt_file = paas_txt_files[sb]
        paas_m_file = paas_m_files[sb]

        phase_bin, model_data, gaussian_sum = np.loadtxt(path + paas_txt_file, usecols=(0, 1, 2), unpack=True)
        phase = np.linspace(0, 1, int(phase_bin[-1]) + 1)

        ax1[0].plot(phase, model_data, label="model data " + str(sb))
        ax1[0].plot(phase, gaussian_sum, label="gaussian sum " + str(sb))

        phase_init, sigma_init, intensity_init = np.loadtxt(path + paas_m_file, usecols=(0, 1, 2), unpack=True)

        if len(phase_init) == 2:
            g = gauss2(phase,
                       phase_init[0], sigma_init[0], intensity_init[0],
                       phase_init[1], sigma_init[1], intensity_init[1])

            model_gauss2 = Model(gauss2)
            parameters_gauss2 = model_gauss2.make_params(mu1=phase_init[0], sigma1=sigma_init[0],
                                                         amplitude1=intensity_init[0],
                                                         mu2=phase_init[1], sigma2=sigma_init[1],
                                                         amplitude2=intensity_init[1])

            result_gauss2 = model_gauss2.fit(data=model_data, x=phase, params=parameters_gauss2, method='leastsq',
                                             nan_policy='omit')
            #report_fit(result_gauss2)
            print("\n\n")
            
            amplitude_fits = [result_gauss2.params["amplitude1"].value, result_gauss2.params["amplitude2"].value]
            
            phase_fits = [result_gauss2.params["mu1"].value, result_gauss2.params["mu2"].value]
            phase_fits_errors = [get_error(result_gauss2, "mu1"), get_error(result_gauss2, "mu2")]

        elif len(phase_init) == 3:
            g = gauss3(phase,
                       phase_init[0], sigma_init[0], intensity_init[0],
                       phase_init[1], sigma_init[1], intensity_init[1],
                       phase_init[2], sigma_init[2], intensity_init[2])

            model_gauss3 = Model(gauss3)
            parameters_gauss3 = model_gauss3.make_params(mu1=phase_init[0], sigma1=sigma_init[0],
                                                         amplitude1=intensity_init[0],
                                                         mu2=phase_init[1], sigma2=sigma_init[1],
                                                         amplitude2=intensity_init[1],
                                                         mu3=phase_init[2], sigma3=sigma_init[2],
                                                         amplitude3=intensity_init[2])

            result_gauss3 = model_gauss3.fit(data=model_data, x=phase, params=parameters_gauss3, method='leastsq',
                                             nan_policy='omit')
            #report_fit(result_gauss3)
            print("\n\n")
            
            amplitude_fits = [result_gauss3.params["amplitude1"].value, result_gauss3.params["amplitude2"].value,
                          result_gauss3.params["amplitude3"].value]
            
            phase_fits = [result_gauss3.params["mu1"].value, result_gauss3.params["mu2"].value,
                          result_gauss3.params["mu3"].value]
            phase_fits_errors = [get_error(result_gauss3, "mu1"), get_error(result_gauss3, "mu2"),
                                 get_error(result_gauss3, "mu3")]

        elif len(phase_init) == 4:
            g = gauss4(phase,
                       phase_init[0], sigma_init[0], intensity_init[0],
                       phase_init[1], sigma_init[1], intensity_init[1],
                       phase_init[2], sigma_init[2], intensity_init[2],
                       phase_init[3], sigma_init[3], intensity_init[3])

            model_gauss4 = Model(gauss4)
            parameters_gauss4 = model_gauss4.make_params(mu1=phase_init[0], sigma1=sigma_init[0], amplitude1=intensity_init[0],
                                                         mu2=phase_init[1], sigma2=sigma_init[1], amplitude2=intensity_init[1],
                                                         mu3=phase_init[2], sigma3=sigma_init[2], amplitude3=intensity_init[2],
                                                         mu4=phase_init[3], sigma4=sigma_init[3], amplitude4=intensity_init[3])
            result_gauss4 = model_gauss4.fit(data=model_data, x=phase, params=parameters_gauss4, method='leastsq',
                                             nan_policy='omit')
            #report_fit(result_gauss4)
            print("\n\n")
            
            amplitude_fits = [result_gauss4.params["amplitude1"].value, result_gauss4.params["amplitude2"].value,
                          result_gauss4.params["amplitude3"].value, result_gauss4.params["amplitude4"].value]
            
            phase_fits = [result_gauss4.params["mu1"].value, result_gauss4.params["mu2"].value,
                          result_gauss4.params["mu3"].value, result_gauss4.params["mu4"].value]
            phase_fits_errors = [get_error(result_gauss4, "mu1"), get_error(result_gauss4, "mu2"),
                                 get_error(result_gauss4, "mu3"), get_error(result_gauss4, "mu4")]

        elif len(phase_init) == 5:
            g = gauss5(phase,
                       phase_init[0], sigma_init[0], intensity_init[0],
                       phase_init[1], sigma_init[1], intensity_init[1],
                       phase_init[2], sigma_init[2], intensity_init[2],
                       phase_init[3], sigma_init[3], intensity_init[3],
                       phase_init[4], sigma_init[4], intensity_init[4])

            model_gauss5 = Model(gauss5)
            parameters_gauss5 = model_gauss5.make_params(mu1=phase_init[0], sigma1=sigma_init[0], amplitude1=intensity_init[0],
                                                         mu2=phase_init[1], sigma2=sigma_init[1], amplitude2=intensity_init[1],
                                                         mu3=phase_init[2], sigma3=sigma_init[2], amplitude3=intensity_init[2],
                                                         mu4=phase_init[3], sigma4=sigma_init[3], amplitude4=intensity_init[3],
                                                         mu5=phase_init[4], sigma5=sigma_init[4], amplitude5=intensity_init[4])

            result_gauss5 = model_gauss5.fit(data=model_data, x=phase, params=parameters_gauss5, method='leastsq',
                                             nan_policy='omit')
            #report_fit(result_gauss5)
            print("\n\n")
            
            amplitude_fits = [result_gauss5.params["amplitude1"].value, result_gauss5.params["amplitude2"].value,
                          result_gauss5.params["amplitude3"].value, result_gauss5.params["amplitude4"].value,
                          result_gauss5.params["amplitude5"].value]
            
            phase_fits = [result_gauss5.params["mu1"].value, result_gauss5.params["mu2"].value,
                          result_gauss5.params["mu3"].value, result_gauss5.params["mu4"].value,
                          result_gauss5.params["mu5"].value]

            phase_fits_errors = [get_error(result_gauss5, "mu1"), get_error(result_gauss5, "mu2"),
                                 get_error(result_gauss5, "mu3"), get_error(result_gauss5, "mu4"),
                                 get_error(result_gauss5, "mu5")]
                                 
        elif len(phase_init) == 6:
             g = gauss6(phase,
                       phase_init[0], sigma_init[0], intensity_init[0],
                       phase_init[1], sigma_init[1], intensity_init[1],
                       phase_init[2], sigma_init[2], intensity_init[2],
                       phase_init[3], sigma_init[3], intensity_init[3],
                       phase_init[4], sigma_init[4], intensity_init[4],
                       phase_init[5], sigma_init[5], intensity_init[5])
                       
             model_gauss6 = Model(gauss6)
             parameters_gauss6 = model_gauss6.make_params(mu1=phase_init[0], sigma1=sigma_init[0], amplitude1=intensity_init[0],
                                                         mu2=phase_init[1], sigma2=sigma_init[1], amplitude2=intensity_init[1],
                                                         mu3=phase_init[2], sigma3=sigma_init[2], amplitude3=intensity_init[2],
                                                         mu4=phase_init[3], sigma4=sigma_init[3], amplitude4=intensity_init[3],
                                                         mu5=phase_init[4], sigma5=sigma_init[4], amplitude5=intensity_init[4],
                                                         mu6=phase_init[5], sigma6=sigma_init[5], amplitude6=intensity_init[5])

             result_gauss6 = model_gauss6.fit(data=model_data, x=phase, params=parameters_gauss6, method='leastsq',
                                             nan_policy='omit')
             #report_fit(result_gauss5)
             print("\n\n")
             
             amplitude_fits = [result_gauss6.params["amplitude1"].value, result_gauss6.params["amplitude2"].value,
                          result_gauss6.params["amplitude3"].value, result_gauss6.params["amplitude4"].value,
                          result_gauss6.params["amplitude5"].value, result_gauss6.params["amplitude6"].value]
            
             phase_fits = [result_gauss6.params["mu1"].value, result_gauss6.params["mu2"].value,
                          result_gauss6.params["mu3"].value, result_gauss6.params["mu4"].value,
                          result_gauss6.params["mu5"].value, result_gauss6.params["mu6"].value]

             phase_fits_errors = [get_error(result_gauss6, "mu1"), get_error(result_gauss6, "mu2"),
                                 get_error(result_gauss6, "mu3"), get_error(result_gauss6, "mu4"),
                                 get_error(result_gauss6, "mu5"), get_error(result_gauss6, "mu6")]
                
        remove = False
        bad_index = []
        phase_fits_copy = phase_fits.copy()
        for pf in phase_fits:
            if pf > 1:
                bad_index.append(phase_fits_copy.index(pf))
                phase_fits.remove(pf)
                remove = True
                
        if remove:
            bad_amplitude_fits = []
            bad_phase_fits_errors = []
            for bi in bad_index:
                bad_amplitude_fits.append(amplitude_fits[bi])
                bad_phase_fits_errors.append(phase_fits_errors[bi])
            for i in range(0, len(bad_index)):
                amplitude_fits.remove(bad_amplitude_fits[i])
                phase_fits_errors.remove(bad_phase_fits_errors[i])
                    
        amplitude_fits_sorted = sorted(amplitude_fits, reverse=True)
        if componet_count == 2:
            index_a = amplitude_fits.index(amplitude_fits_sorted[0])
            index_b = amplitude_fits.index(amplitude_fits_sorted[1])
        elif componet_count == 3:
            index_a = phase_fits.index(np.max(phase_fits))
            index_b = phase_fits.index(np.min(phase_fits))
                           
        phase_diff.append(np.abs(phase_fits[index_b] - phase_fits[index_a]))
        phase_diff_errors.append(np.sqrt(
        phase_fits_errors[index_a] ** 2 + phase_fits_errors[index_b] ** 2))
        
        ax1[1].plot(phase, g, label="init gauss")
        ax1[1].plot(phase, model_data, label="data")
        fig1.suptitle("Frequency:" + str(frequency[sb]) + " telscope: " + telescopes[sb])
       
        ax1[0].legend()
        ax1[1].legend()
        ax1[0].set_xlim(0, 1)
        ax1[1].set_xlim(0, 1)
        ax1[0].set_xlabel("Pulse phase")
        ax1[1].set_xlabel("Pulse phase")
        ax1[0].set_ylabel("Intensity")
        ax1[0].set_ylabel("Intensity")
        fig1.tight_layout()
    
    phase_diff = np.array(phase_diff) * 360
    print("\n\n")

    frequency = np.array([get_freq(subprocess.check_output(["psredit", "-c", "freq", path + fscrs_file])) for fscrs_file in fscrs_files])

    thorset_frequency = np.linspace(30, 10000, 1000)
    thorset_fit_values = {"B0301+19": [86, 0.34, 0.9], 
                          "B0329+54": [1059, 0.96, 19.8], 
                          "B0525+21": [90, 0.47, 9.5], 
                          "B1133+16": [53, 0.50, 4.4], 
                          "B1237+25": [79, 0.52, 7.9], 
                          "B2020+28": [1103, 1.08, 9.1],
                          "B2045-16": [45, 0.36, 7.9]}

    model = Model(profile_function)
    A_t = thorset_fit_values[pulsar][0]
    alpha_t = thorset_fit_values[pulsar][1]
    thata_min_t = thorset_fit_values[pulsar][2]

    parameters = model.make_params(A=A_t, alpha=alpha_t, thata_min=thata_min_t)
    
    #print(frequency)
    #frequency = np.array([40.13625, 77.63625, 2429, 2685, 1374, 1630])
        
    result = model.fit(data=phase_diff, x=frequency, params=parameters, method='leastsq', nan_policy='omit')
    
    a = result.params["A"].value
    alpha = result.params["alpha"].value
    thata_min = result.params["thata_min"].value
    report_fit(result)
    
    pulsar_fit_values_file = "pulsar_fit_values.csv"
    
    alpha_error = get_error(result, "alpha")
    thata_min_error = get_error(result, "thata_min")

    with open(pulsar_fit_values_file, "a") as fit_out:
        fit_out.write(pulsar + "," + "%.3f" % a + "," + "%.3f" % alpha + "," + "%.3f" % thata_min + "," + "%.3f" % alpha_error + "," + "%.3f" % + thata_min_error + "\n")

    fig2, ax2 = plt.subplots(nrows=1, ncols=1, figsize=(16, 16), dpi=150)
    
    #print("frequency", frequency)
    #print("phase_diff", phase_diff)
    #symbols.remove(symbols[6])
    #colors.remove(colors[6])
    
    for i in range(0, len(frequency)):
        ax2.scatter(frequency[i], phase_diff[i], c=colors[i], alpha=0.4, marker=symbols[i])
        ax2.errorbar(frequency[i], phase_diff[i], yerr=np.abs(phase_diff_errors[i]) * 100, fmt=symbols[i], c=colors[i], xerr=10,  alpha=0)
    
    x = np.linspace(min(frequency), max(frequency), 1000)
    ax2.plot(x, profile_function(x, a, alpha, thata_min), label="New data", c="black", linewidth=2)
    ax2.plot(thorset_frequency, profile_function(thorset_frequency, A_t, alpha_t, thata_min_t), c="gray", linestyle='dashed', label="Thorset", linewidth=2)
    ax2.set_xlabel("Frequency [MHz]")
    ax2.set_ylabel(r'$ \Delta \theta [deg]$')
    ax2.set_xscale("log")
    ax2.legend()
    fig2.tight_layout()

    fig2.savefig(pulsar + "_profile.png")
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create pulsar profile')
    parser.add_argument('pulsar_name', type=str, help='pulsar name')
    parser.add_argument('componet_count', type=float, help='pulsar componet count')
    args = parser.parse_args()
    main(args.pulsar_name, args.componet_count)
    sys.exit(0)
