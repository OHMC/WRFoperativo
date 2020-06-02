# -*- coding: utf-8 -*-

# 0.25x0.25 horizontal resolution on the specified geographical domain
# and for the specified meteorological parameters only (slice, i.e.
# sub-area of global data)

# Attention: trailing spaces are mandatory in structured "if" or "for"

# for file-directory functions
import os
# for sleep command
import time
# for archiving (tar) of created files
import os.path
import requests
import datetime
import socket
import argparse

# CONFIGURATION OF GRIB FILTER AND DATE RANGE
# Domain (limited area) definition (geographical coordinates)
LON_W = "-96"
LON_E = "-15"
LAT_N = "-10"
LAT_S = "-75"

# Data grid resolution (in degree)
ADGRID = "0.25"  # can be:0.25, 0.5, 1.0, 2.5

# Total forecast length (in hours) for which data are requested:
NHOUR = int(os.environ['RUN_HOURS'])
# Interval in hours between two forecast times:
DHOUR = 3

# Count files to request
CANT_FILES_REQUESTED = NHOUR/DHOUR+1

COUNTMAX = 50
ICOUNTMAX = 100
S_SLEEP1 = 600
S_SLEEP2 = 60

# Definition of requested levels and parameters
# PAR_LIST=["TMAX"]
PAR_LIST = ["HGT", "LAND", "PRES", "PRMSL", "RH", "SOILW", "SPFH", "TMP",
            "UGRD", "VGRD", "WEASD", "TSOIL"]

# ADDR
BASE_ADDR = "https://nomads.ncep.noaa.gov/cgi-bin/"

PERL_FILTER = "filter_gfs_0p25.pl"

DOMAIN_PARAMETERS = (f"&subregion=&leftlon={LON_W}&rightlon={LON_E}"
                     f"&bottomlat={LAT_S}&toplat={LAT_N}")
LEVELS = "&all_lev=on"


def download_grb_file(url, outfile):
    """ Download grib files
    This function download an url of a Grib file and
    saves the file in outfile location and name

    Attributes:
        url (str): url of the grib gfile
        oufile (str): fullpath and name of the file

    Todo: chek if its an GRIB file
          activate logging

    """
    # cur_url = url.format(date=date)
    response = requests.get(url, stream=True)

    if not response.ok:
        print('Failed to download gfs data for date')
        return -1

    # logging.info('Start download DOMAIN_PARAMETERScontent(1024):
    with open(outfile, 'wb') as f:
        for block in response.iter_content(1024):
            f.write(block)

    # logging.info('Finished: {:%Y-%m-%d %H:%M}'.format(date))
    return 0


def get_list_gfs(inidate):
    inidate = int(inidate)      # CAST INIT date
    # inidate=int(os.environ['inidate'])

    # Date of forecast start (analysis)
    date = inidate//100
    # Instant (hour, UTC) of forecast start (analysis)

    # fci=int(sys.argv[1]) # reads input on the calling line
    # (example: "python get_GFS_grib2_slice.py 00")
    # fci=input('Type UTC time of analysis (00, 06, 12, 18) ')
    # # for request of manual input after launch
    fci = inidate-date*100

    # Defines connection timeoutcd
    socket.setdefaulttimeout(30)

    # Definiton of date (in required format)
    day = datetime.datetime.today()
    # tomorrow=day+datetime.timedelta(days=1)
    # yesterday=day+datetime.timedelta(days=-1)

    # If the download is made early in the morning,
    # the date is that of yesterday

    # if day.hour < 6 :
    #   day=yesterday

    # day="%4.4i%2.2i%2.2i" % (day.year,day.month,day.day)
    # # structure definition
    day = "%8.8i" % (date)
    fciA = "%2.2i" % fci

    print("Date and hour of GFS forecast initial time: ", day, fci)

    dir_gfs_name = f"&dir=%2Fgfs.{day}%2F{fciA}"

    # Full list of requested files
    list_remote_files = []
    list_files_local = []

    for iter_num_file in range(0, int(CANT_FILES_REQUESTED)):

        npar = len(PAR_LIST)
        parameters = ""
        for iparam in range(0, npar):
            parameters = parameters + f"&var_{PAR_LIST[iparam]}=on"

        hf = iter_num_file*DHOUR
        hfA2 = "%3.3i" % hf

        file_name_base = f"?file=gfs.t{fciA}z.pgrb2.0p25.f{hfA2}"

        remote_file = (f"{PERL_FILTER}{file_name_base}{LEVELS}"
                       f"{parameters}{DOMAIN_PARAMETERS}{dir_gfs_name}")
        local_file = f"GFS_{day}{fciA}+{hfA2}.grib2"

        list_remote_files.append(remote_file)
        list_files_local.append(local_file)

        print("********************************")
        print(remote_file)
        print("********************************")
        print(local_file)
        print("********************************")

    return list_remote_files, list_files_local


def download(output_dir, list_remote_files, list_files_local):
    """
    Se descargan los datos con los siguientes parámetros::

        LON_W="-96"  # límite de longitud oeste de la grilla
        LON_E="-15"  # límite de longitud este de la grilla
        LAT_N="-10"  # límite de latitud norte de la grilla
        LAT_S="-75"  # límite de latitud sur de la grilla
        ADGRID="0.25"  # resolución de la grilla
        NHOUR=39  # cantidad de horas que en que se descargan datos
        DHOUR=03 # intervalo en horas en que se vuelve a descargar
        LEV_LIST=["all"] # niveles solicitados
        PAR_LIST=["HGT","LAND","PRES","PRMSL","RH","SOILW","SPFH","TMP","UGRD",
        "VGRD","WEASD","TSOIL"]  # parámetros solicitados

    Parameters:
        inidate(str): date GFS files in the format YMDH with H 00, 06, 12 or 18
        output(str): path to the directory where GFS should be saved

    """

    # sys.exit(0)
    # Dowloading of requested files
    WORK = True

    count_files_to_download = len(list_remote_files)
    print(f"Request in server: {BASE_ADDR}")
    print(f"count of files to download: {count_files_to_download}")
    # extenar check, if this fail we go out
    count = 1

    while count <= COUNTMAX:
        print('Attempt number: ', count)
        count_req_files = 0
        # to check if all desired files were downloaded
        count_down_iter = 0

        for ifile in range(0, count_files_to_download):
            count_down_iter = count_down_iter + 1
            remote_file = f"{BASE_ADDR}{list_remote_files[ifile]}"
            local_file = (f"{output_dir}/{list_files_local[ifile]}")

            ##############################
            print(f"local_file {local_file}")
            print(f"remote_file {remote_file}")
            ############################

            ierr = 100
            icount = 0

            while ierr != 0 and icount <= ICOUNTMAX:
                icount = icount + 1
                # The following prints on the sceen the entire
                # text of the request
                print("Request remote file: ", remote_file)
                if ((not (os.path.exists(local_file))) or ((os.path.getsize(local_file)) <= 20000000)):
                    # Download de remopte file
                    ierr = download_grb_file(remote_file, local_file)
                    print('dowloading error= ', ierr)
                    if ierr == 0:  # successeful downloading
                        count_req_files = count_req_files+1
                        print(f"Requested file downloaded in {local_file}")
                    else:  # unsuccesseful downloading
                        print(f'File {remote_file} not downloaded! sleep')
                        time.sleep(S_SLEEP2)
                else:
                    print('Archivo ya descargado')
                    ierr = 0
                    count_req_files = count_req_files + 1

            if count_down_iter == count_req_files:
                # if we downloaded all files
                WORK = False
        if WORK:
            print(f"Not all requested files downloaded, "
                  f"sleeping {S_SLEEP1} s before next trial")
            time.sleep(S_SLEEP1)
        else:
            print('**************************************************')
            print(f" All requested grib2 files downloaded !")
            print('**************************************************')
            break

        count = count+1
        if WORK:
            print(f"All acceptable attempts have been done in this"
                  f" server, sleeping {S_SLEEP2}s befor request"
                  f" other server")
            time.sleep(S_SLEEP2)
        else:
            break

        if not WORK:
            break


def main():
    parser = argparse.ArgumentParser(
        description='descarga_GFS025.py --ini=inidate --output=output',
        epilog="script de descarga de GFS0925")

    parser.add_argument("--ini", type=int, dest="inidate", help="init date",
                        required=True)
    parser.add_argument("--output", dest="output", help="directories where \
                        downloaded files are stored and (optionally) archived",
                        required=True)
    args = parser.parse_args()

    # define options
    parser.print_help()

    if not args.inidate or not args.output:
        print("The parameter is required.  Nothing to do!")
    else:
        list_remote_files, list_files_local = get_list_gfs(args.inidate)
        download(args.output, list_remote_files, list_files_local)


if __name__ == "__main__":
    main()
