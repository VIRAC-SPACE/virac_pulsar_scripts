import sys
import os
import time

import vex

os.environ['TZ'] = 'UTC'
time.tzset()


def main(vex_file):
    channels_mapping = []
    vex_data = open(vex_file, "r")
    v = vex.parse(vex_data.read())
    threads = v["THREADS"]
    threads_name = threads.items()[0][0]
    channels = threads[threads_name].getall("channel")
    
    a = 0
    b = 1
    while b< len(channels) + 1:
        channels_mapping.append((channels[a][2], channels[b][2]))
        a += 2
        b += 2
        
    vex_data.close()
    
    print(channels_mapping)


if __name__ == "__main__":
    vex_file = sys.argv[1]
    main(vex_file)
    sys.exit()
