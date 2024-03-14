import argparse
import os
import sys
import time

import vex


def gen_hdr_file_names(obs_name, nr_vdif_files,  spw_nr):
    hdr_files_name = []
    
    vdif_file_index = 1
    for i in range(1, nr_vdif_files + 1):
        
        if i == 1:
            vdif_file_index = 1
        else:
            vdif_file_index += 4

        if vdif_file_index < 10:
            tmp = "000"
        elif vdif_file_index >= 10:
            tmp = "00"
        else:
            tmp = "0"

        for j in range(0, spw_nr):
            hdr_file_name = obs_name + "_no" + tmp + str(vdif_file_index) + "_spw" + str(j + 1) + ".hdr"
            hdr_files_name.append(hdr_file_name)
            
    return hdr_files_name


def get_source(hdr_file_name, sources, vdif_files_name_index):
    index = vdif_files_name_index.index(int(hdr_file_name.split("_")[1].replace("no", "").replace("0", "")))
    return sources[index]


def get_freq(hdr_file_name, freqs):
    spw = int(hdr_file_name.split("_")[2].split(".")[0].replace("spw", ""))
    return freqs[spw -1]


def gen_hdr_files(hdr_files_name, sources, vdif_files_name_index, freqs, bw):
    for hdr_file_name in hdr_files_name:
        source = get_source(hdr_file_name, sources, vdif_files_name_index)
        freq = get_freq(hdr_file_name, freqs)
        
        with open(hdr_file_name, "w") as hdr:
            data_file = hdr_file_name.split("_")
            data_file = data_file[0] + "_" + "ir" + "_" + data_file[1] + "_" + data_file[2].replace("hdr", "vdif")
            hdr.write("INSTRUMENT VDIF\n")
            hdr.write("FORMAT VDIF_8000-512-2-2\n")
            hdr.write("NCHAN 2\n")
            hdr.write("NPOL 2\n")
            hdr.write("TELESCOPE Irbene\n")
            hdr.write("SOURCE " + source + "\n")
            hdr.write("FREQ " + str(freq) + "\n")
            hdr.write("BW " + str(bw) + "\n")
            hdr.write("DATAFILE " + data_file  + "\n")
            hdr.write("HDR_VERSION 1\n")
            hdr.write("MODE Pulsar\n")


def gen_freq(vex_freqs):
    freqs = []
    for f in vex_freqs:
        bw = int(f[3].replace(" MHz", "").replace("0", "").replace(".", ""))
        if f[2] == 'L':
            freqs.append(float(f[1].replace(" MHz", "")) - int(bw/2))
        elif f[2] == 'U':
            freqs.append(float(f[1].replace(" MHz", "")) + int(bw/2)) 
        
    return sorted(list(set(freqs)))


def main(vex_file):
    os.environ['TZ'] = 'UTC'
    time.tzset()
    
    obs_name = vex_file.split(".")[0]

    with open(vex_file, "r") as vex_data:
        v = vex.parse(vex_data.read())
        scans = v["SCHED"]
        nr_scans = len(scans)
        sources = [src[0] for src in v["SOURCE"].items()]
        freq_block_name = v.getall("FREQ")[0].items()[0][0]
        spw_nr = (len(v["FREQ"][freq_block_name]) -1)/2
        
        nr_scans = len(scans)
        nr_vdif_files = nr_scans /4
        hdr_files = gen_hdr_file_names(obs_name, nr_vdif_files,  spw_nr)
        vdif_files_name_index = sorted(list(set([int(file.split("_")[1].replace("no", "").replace("0", "")) for file in hdr_files])))
        
        freqs = v["FREQ"][freq_block_name].getall('chan_def')
        f = freqs[0]
        bw = int(f[3].replace(" MHz", "").replace("0", "").replace(".", ""))
        freqs = gen_freq(freqs)
        gen_hdr_files(hdr_files, sources, vdif_files_name_index, freqs, bw)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate snp file')
    parser.add_argument('vex_file', type=str, help='vex file name')
    args = parser.parse_args()
    main(args.vex_file)
    sys.exit(0)
