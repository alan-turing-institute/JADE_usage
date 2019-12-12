from subprocess import run
from time import strftime

FORMAT = ("jobid,jobname,account,user,partition,nodelist,reqgres,allocgres,"
          "state,exitcode,elapsed,submit,start,end")
DELIMITER = ","
JADE_ADDRESS = "jade.hartree.stfc.ac.uk"


def fetch(user, year, month):
    date_format = "%Y-%m-%d"
    start = strftime(date_format, (year, month, 1, 0, 0, 0, 0, 1, -1))
    if month != 12:
        end = strftime(date_format, (year, month+1, 1, 0, 0, 0, 0, 1, -1))
    else:
        end = strftime(date_format, (year+1, 1, 1, 0, 0, 0, 0, 1, -1))

    result = run(["ssh",
                  "{user}@{jade}".format(user=user, jade=JADE_ADDRESS),
                  "sacct",
                  "--allusers",
                  "--parsable2",
                  "--delimiter={}".format(DELIMITER),
                  "--starttime={}".format(start),
                  "--endtime={}".format(end),
                  "--format={}".format(FORMAT)
                  ], capture_output=True, text=True)

    if result.returncode != 0:
        raise FetchError(result)

    return result.stdout


def export(user, year, month):
    date_format_short = "%Y-%m"
    file_date = strftime(date_format_short,
                         (year, month, 1, 0, 0, 0, 0, 1, -1))
    filename = "{}_usage.csv".format(file_date)

    with open(filename, "w") as outfile:
        outfile.write(fetch(user, year, month))


class FetchError(Exception):
    def __init__(self, result):
        message = (
            "Non zero return code when attempting to execute sacct over ssh\n"
            "command: {}\n".format(" ".join(result.args))
            + "return code: {}\n".format(result.returncode)
            + "stderr: {}\n".format(result.stderr)
        )
        super().__init__(message)
