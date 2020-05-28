# -*- coding: utf-8 -*-

# 0.25x0.25 horizontal resolution on the specified geographical domain
# and for the specified meteorological parameters only (slice, i.e.
# sub-area of global data)

# Attention: trailing spaces are mandatory in structured "if" or "for"


import sys
# for file-directory functions
import os
# for sleep command
import time
# for archiving (tar) of created files
import os.path
import requests
import datetime
import socket
from optparse import OptionParser


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

    # logging.info('Start download of {:%Y-%m-%d %H:%M}'.format(date))
    with open(outfile, 'wb') as f:
        for block in response.iter_content(1024):
            f.write(block)

    # logging.info('Finished: {:%Y-%m-%d %H:%M}'.format(date))
    return 0


def download(inidate, output_dir):
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

    # Domain (limited area) definition (geographical coordinates)
    LON_W = "-96"
    LON_E = "-15"
    LAT_N = "-10"
    LAT_S = "-75"

    # Data grid resolution (in degree)
    ADGRID = "0.25"  # can be:0.25, 0.5, 1.0, 2.5

    # Defines connection timeoutcd
    socket.setdefaulttimeout(30)

    # Total forecast length (in hours) for which data are requested:
    NHOUR = int(os.environ['RUN_HOURS'])

    # Interval in hours between two forecast times:
    DHOUR = 3

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

    # Definition of requested levels and parameters
    LEV_LIST = ["all"]
    # PAR_LIST=["TMAX"]
    PAR_LIST = ["HGT", "LAND", "PRES", "PRMSL", "RH", "SOILW", "SPFH", "TMP",
                "UGRD", "VGRD", "WEASD", "TSOIL"]

    COUNTMAX = 50
    ICOUNTMAX = 100
    S_SLEEP1 = 600
    S_SLEEP2 = 60

    # N_LEV_TYPE = 1
    NINSTANT = NHOUR/DHOUR+1
    NFILE_REQUESTED = [NINSTANT, 1]

    FILE_NAME_DOMAIN = ("&subregion=&leftlon=" + LON_W + "&rightlon=" + LON_E
                        + "&bottomlat=" + LAT_S + "&toplat=" + LAT_N)
    if ADGRID == "0.25":
        FILE_NAME_INI = "filter_gfs_0p25.pl"
        DIR_NAME = "&dir=%2Fgfs." + day + "%2F" + fciA

    if ADGRID == "0.5":
        FILE_NAME_INI = "filter_gfs_hd.pl"
        DIR_NAME = "&dir=%2Fgfs." + day + fciA + "%2Fmaster"

    if ADGRID == "1.0":
        FILE_NAME_INI = "filter_gfs.pl"
        DIR_NAME = "&dir=%2Fgfs." + day + fciA

    if ADGRID == "2.5":
        FILE_NAME_INI = "filter_gfs_2p5.pl"
        DIR_NAME = "&dir=%2Fgfs." + day + fciA

    # Full list of requested files

    LIST_FILE_REMOTE = []
    # LIST_FILE_LOCAL = []
    LIST_FLAG = []
    LIST_FILE_LOCAL_FIN = []
    NINST = NFILE_REQUESTED[0]
    for INST in range(0, int(NINST)):
        if INST+1 > NFILE_REQUESTED[0]:
            continue
        NLEV = len(LEV_LIST)
        NPAR = len(PAR_LIST)
        PARAMETERS = ""
        for IPAR in range(0, NPAR):
            PARAMETERS = PARAMETERS + "&var_" + PAR_LIST[IPAR] + "=on"
            LEVELS = ""

        if LEV_LIST[0] == "all":
            LEVELS = LEVELS + "&all_lev=on"
        else:
            for ILEV in range(0, NLEV):
                LEVELS = LEVELS + "&lev_" + LEV_LIST[ILEV] + "=on"
            HF = INST*DHOUR
            HFA = "%2.2i" % HF
            HFA2 = "%3.3i" % HF

            if ADGRID == "0.25":
                FILE_NAME_BASE = f"?file=gfs.t{fciA}z.pgrb2.0p25.f{HFA2}"
            if ADGRID == "0.5":
                FILE_NAME_BASE = f"?file=gfs.t{fciA}z.mastergrb2f{HFA}"
            if ADGRID == "1.0":
                FILE_NAME_BASE = f"?file=gfs.t{fciA}z.pgrbf{HFA}.grib2"
            if ADGRID == "2.5":
                FILE_NAME_BASE = f"?file=gfs.t{fciA}z.pgrbf{HFA}.2p5deg.grib2"

            FILE_REMOTE = (FILE_NAME_INI + FILE_NAME_BASE + LEVELS
                           + PARAMETERS + FILE_NAME_DOMAIN + DIR_NAME)
            # FILE_LOCAL="GFS_"+LEV_TYPE[ILEVTYPE]+"_"+day+fciA+"+"+HFA2+".grib2"
            FILE_LOCAL_FIN = "GFS_" + day+fciA + "+" + HFA2 + ".grib2"
            FLAG = 0
            LIST_FILE_REMOTE.append(FILE_REMOTE)
            # LIST_FILE_LOCAL.append(FILE_LOCAL)
            # if ILEVTYPE==0: LIST_FILE_LOCAL_FIN.append(FILE_LOCAL_FIN)
            LIST_FILE_LOCAL_FIN.append(FILE_LOCAL_FIN)
            LIST_FLAG.append(FLAG)

            print("********************************")
            print(FILE_REMOTE)
            print("********************************")
            print(FILE_LOCAL_FIN)
            print("********************************")

    NFILE = len(LIST_FLAG)

    # sys.exit(0)

    # Dowloading of requested files

    WORK = True
    while WORK:
        NOMADS_ADDR = "https://nomads.ncep.noaa.gov/cgi-bin/"
        print('Request in server: ', NOMADS_ADDR)

        count = 1
        while count <= COUNTMAX:
            print('Attempt number: ', count)
            count_req_files = 0
            NFLAG = 0
            for IFILE in range(0, NFILE):
                    if LIST_FLAG[IFILE] == 0:
                        NFLAG = NFLAG + 1
                        FILE_REMOTE = NOMADS_ADDR+LIST_FILE_REMOTE[IFILE]
                        FILE_LOCAL = (f"{output_dir}/"
                                      f"{LIST_FILE_LOCAL_FIN[IFILE]}")

                        ##############################
                        print("FILE_LOCAL" + FILE_LOCAL)
                        print("FILE_REMOTE" + FILE_REMOTE)
                        # sys.exit(0)

                        ############################

                        ierr = 100
                        icount = 0
                        while ierr != 0 and icount <= ICOUNTMAX:
                            icount = icount + 1
                            # The following prints on the sceen the entire
                            # text of the request
                            print("Request remote file: ", FILE_REMOTE)
                            if ((not (os.path.exists(FILE_LOCAL))) or
                               ((os.path.getsize(FILE_LOCAL)) <= 20000000)):
                                ierr = download_grb_file(FILE_REMOTE,
                                                         FILE_LOCAL)
                                print('dowloading error= ', ierr)
                                if ierr == 0:  # successeful downloading
                                    LIST_FLAG[IFILE] = 1
                                    count_req_files = count_req_files+1
                                    print(f"Requested remote file downloaded "
                                          f"in local file{FILE_LOCAL}")
                                else:  # unsuccesseful downloading
                                    print(f'Data file {FILE_REMOTE} not '
                                          f'downloaded! sleep {S_SLEEP2}s')
                                    time.sleep(S_SLEEP2)

                            else:
                                print('Archivo ya descargado')
                                ierr = 0
                                count_req_files = count_req_files + 1
                                # print count_req_files

                        if NFLAG == count_req_files:
                            WORK = False
                        if WORK:
                            print(f"Not all requested files downloaded, "
                                  f"sleeping {S_SLEEP1} s before next trial")
                            time.sleep(S_SLEEP1)
                        else:
                            print('***************************************'
                                  '****************')
                            print(f" All requested grib2 files downloaded !"
                                  f" {day}, {fci}, UTC")
                            print('***************************************'
                                  '****************')
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

    usage = """descarga_GFS025.py --ini=inidate --output=output"""
    parser = OptionParser(usage)

    # define options
    parser.add_option("--ini", dest="inidate", help="init date")
    parser.add_option("--output", dest="output", help="directories where \
                      downloaded files are stored and (optionally) archived")

    (opts, args) = parser.parse_args()

    if len(sys.argv) == 1:
        print(usage)
    elif not opts.inidate or not opts.output:
        print("The parameter is required.  Nothing to do!")
        print(usage)
    else:
        download(opts.inidate, opts.output)


if __name__ == "__main__":
    main()
