from subprocess import run
from time import strftime

FORMAT = ("jobid,jobname,account,user,partition,nodelist,reqgres,allocgres,"
          "state,exitcode,elapsed,submit,start,end")
DELIMITER = ","


def export(year, month):
    date_format = "%Y-%m-%d"
    start = strftime(date_format, (year, month, 1, 0, 0, 0, 0, 1, -1))
    if month != 12:
        end = strftime(date_format, (year, month+1, 1, 0, 0, 0, 0, 1, -1))
    else:
        end = strftime(date_format, (year+1, 1, 1, 0, 0, 0, 0, 1, -1))

    filename = "{}_usage.csv".format(start)
    with open(filename, 'w') as outfile:
        run([
            "sacct",
            "--allusers",
            "--parsable2",
            "--delimiter={}".format(DELIMITER),
            "--starttime={}".format(start),
            "--endtime={}".format(end),
            "--format={}".format(FORMAT)
            ], stdout=outfile)
