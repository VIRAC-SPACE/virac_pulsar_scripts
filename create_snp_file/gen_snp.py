import argparse
import os
import sys
import time

import vex


def format_coords(ra, dec):
    out_ra = ra.replace("h", "").replace("m", "").replace("s", "").rstrip("0")
    out_dec = dec.replace("d", "").replace("\'", "").replace("\"", "").rstrip("0")
    return out_ra, out_dec


def main(vex_file):
    os.environ['TZ'] = 'UTC'
    time.tzset()

    with open(vex_file, "r") as vex_data:
        v = vex.parse(vex_data.read())
        scans = v["SCHED"]
        nr_scans = len(scans)
        sources = v["SOURCE"]

        snp_file = vex_file.split(".")[0] + "ir.snp"
        obs_name = vex_file.split(".")[0]
        year = 2024
        with open(snp_file, "w") as snp:
            snp.write("\" " + obs_name + "      " + str(year) + " IRBENE   I Ir\n")
            snp.write("\" I IRBENE   AZEL  .0000 120.0    3 -330.0   30.0 120.0    3    5.0   85.0   .0 Ir\n")
            snp.write("\" Ir IRBENE    3183649.31400  1276902.98900  5359264.71000\n")
            snp.write("\"      IRBENE      0     8820\n")
            snp.write("\" drudg version 2019Sep23 compiled under FS  9.13.02\n")
            snp.write("\" Rack=DBBC_DDC  Recorder 1=FlexBuff  Recorder 2=none\n")

            new_source = True
            source_index = 0
            for scan in range(1, nr_scans + 1):
                if scan < 10:
                    tmp = "000"
                elif scan >= 10:
                    tmp = "00"
                else:
                    tmp = "0"

                scan_ = scans["No" + tmp + str(scan)]
                scan_duration = scan_["station"][2].split(" ")[0]
                source = scan_["source"]
                coords = format_coords(sources[source]["ra"], sources[source]["dec"])
                snp.write("scan_name=no" + tmp + str(scan) + "," + obs_name + ",ir,"
                          + str(scan_duration) + "," + str(scan_duration) + "\n")
                snp.write("source=" + source.lower() + "," + str(coords[0]) + "," +
                          str(coords[1]) + ",2000.0," + scan_["station"][4] + "\n")
                snp.write("ready_disk\n")
                snp.write("checkmk5\n")
                snp.write("setup01\n")
                snp.write("preob\n")

                if new_source:
                    snp.write("disk_record=on\n")
                    new_source = False

                snp.write("disk_record\n")

                source_index += 1

                if source_index == 4:
                    new_source = True
                    source_index = 0
                    snp.write("disk_record=off\n")

                snp.write("midob\n")
                snp.write("data_valid=off\n")
                snp.write("postob\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate snp file')
    parser.add_argument('vex_file', type=str, help='vex file name')
    args = parser.parse_args()
    main(args.vex_file)
    sys.exit(0)
