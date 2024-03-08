import sys
import subprocess
from multiprocessing import Pool

from baseband import vdif
import numpy as np
from tqdm import tqdm


def split_data(params):
    orginal_vdif = params[0]
    channs = params[1]
    spw = params[2]
    
    input_file = orginal_vdif.replace(".m5a", "")
    out = input_file.split("_")[0] + "_" + input_file.split("_")[1] + "_" +  input_file.split("_")[2] + "_spw" + str(spw) + ".vdif"
    
    with vdif.open(orginal_vdif, 'rs',  subset=(slice(channs[0], channs[0]+1)))as fr, vdif.open(orginal_vdif, 'rs',  subset=(slice(channs[1], channs[1]+1)))as fr2:
        new_header = fr.header0.copy()
        new_header.nchan = 2
        info = str(fr.info).split("\n")
        number_of_frames = 0
        samples_per_frame = 0
        
        for it in info:
            if it.startswith("number_of_frames = "):
                number_of_frames = int(it.split("=")[1])
            elif  it.startswith("samples_per_frame = "):
                samples_per_frame = int(it.split("=")[1])
                
        samples = samples_per_frame * number_of_frames
        with vdif.open(out, 'ws', sample_rate=fr.sample_rate, header0=new_header, nthread=1) as fw:
            for i in tqdm(range(0, number_of_frames)):
                try:
                    data = np.zeros((samples_per_frame, 2), dtype=np.float32)
                        
                    data[:, 0] = fr.read(samples_per_frame).reshape(samples_per_frame,)
                    data[:, 1] = fr2.read(samples_per_frame).reshape(samples_per_frame,)
                            
                    fw.write(data)
                                                       
                except EOFError:
                    print(EOFError)
                    break


def main(vex_file, input_file):
    channels = subprocess.check_output(["python2", "/home/pulsars/virac_pulsar_scripts/split_vdif_data/get_channels_mapping.py", vex_file]).decode("utf8").replace("[", "").replace("]", "").replace("(", "").replace(")", "").replace(",", "").replace("'", "").split()
    
    channels = [int(ch) for ch in channels]
    channels_mapping = []
    
    a = 0
    b = 1
    while b< len(channels) + 1:
        channels_mapping.append((channels[a], channels[b]))
        a += 2
        b += 2
            
    split_data_inputs = []
    orginal_vdif = input_file
    for channs in channels_mapping:
        spw = channels_mapping.index(channs) + 1        
        split_data_inputs.append((orginal_vdif, channs, spw))

    p = Pool(16)
    p.map(split_data, split_data_inputs)
    
                         
if __name__ == "__main__":
    vex_file = sys.argv[1]
    input_file = sys.argv[2]
    main(vex_file, input_file)
    sys.exit()
