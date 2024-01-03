import sys
import os

import baseband
from baseband import vdif
import numpy as np
from tqdm import tqdm


# [-1, 1]

def main():
    orginal_vdif =  "pul1_ir_no0002.m5a"
    out = "pul1_ir_no0001_spw4.vdif"
        
    i = 1
    with vdif.open(orginal_vdif, 'rs',  subset=(slice(1,2)) )as fr, vdif.open(orginal_vdif, 'rs',  subset=(slice(5,6)) )as fr2:
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
                    
                    
if __name__ == "__main__":
    main()
    sys.exit()


