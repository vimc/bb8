from os import listdir, system

from os.path import join

log_dir = "/bb8/logs"


def get_all_log_files():
    return sorted(listdir(log_dir), reverse=True)


def list_logs(n):
    all_files = get_all_log_files()
    count = len(all_files)
    for f in all_files[:min(n, count)]:
        print(f)
    if count > n:
        print("Results truncated, use bb8 log --list --limit={} to view "
              "all".format(count))


def get_latest_version():
    all_files = get_all_log_files()
    if all_files:
        return all_files[0]
    else:
        return None


def view_logs(version):
    path = join(log_dir, version)
    system("cat {}".format(path))


def inspect_logs(args):
    if args["--list"]:
        n = int(args["--limit"])
        list_logs(n)
    else:
        version = args["--version"] or get_latest_version()
        if version:
            view_logs(version)
        else:
            print("No logs exist")
