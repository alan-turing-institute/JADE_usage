from subprocess import run

FORMAT = ("jobid,jobname,account,user,partition,nodelist,reqgres,allocgres,"
          "state,exitcode,elapsed,submit,start,end")
DELIMITER = ","
JADE_ADDRESS = "jade.hartree.stfc.ac.uk"


def fetch(user, start_date, end_date):
    result = run(["ssh",
                  "{user}@{jade}".format(user=user, jade=JADE_ADDRESS),
                  "sacct",
                  "--allusers",
                  "--parsable2",
                  "--delimiter={}".format(DELIMITER),
                  "--starttime={}".format(start_date),
                  "--endtime={}".format(end_date),
                  "--format={}".format(FORMAT)
                  ], capture_output=True, text=True)

    if result.returncode != 0:
        raise FetchError(result)

    return result.stdout


def export(user, start_date, end_date):
    filename = "{}-{}_usage.csv".format(start_date, end_date)

    with open(filename, "w") as outfile:
        outfile.write(fetch(user, start_date, end_date))


class FetchError(Exception):
    def __init__(self, result):
        message = (
            "Non zero return code when attempting to execute sacct over ssh\n"
            "command: {}\n".format(" ".join(result.args))
            + "return code: {}\n".format(result.returncode)
            + "stderr: {}\n".format(result.stderr)
        )
        super().__init__(message)
