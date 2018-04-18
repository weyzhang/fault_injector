from csv import DictWriter, DictReader
import argparse

metricWhitelist = ['#Time', 'Active', 'cpu_freq.0']
timeLabel = '#Time'


def mergeAndFilter(inpaths, out, times=None):
    infiles = {}
    readers = {}
    for p in inpaths:
        infile = open(p, 'r')
        infiles[p] = infile
        readers[p] = DictReader(infile)

    entries = {}
    for reader in readers.values():
        try:
            entry = next(reader)
        except (StopIteration, IOError):
            continue

        while entry is not None:
            time = int(entry[timeLabel].split('.')[0])
            if times is None or (times[0] <= time <= times[1]):
                for k, v in entry.items():
                    if not metricWhitelist or k in metricWhitelist:
                        if time not in entries:
                            entries[time] = {}
                        entries[time][k] = v
            try:
                entry = next(reader)
            except (StopIteration, IOError):
                break
    for f in infiles.values():
        f.close()

    outfile = open(out, 'w')
    writer = DictWriter(outfile, fieldnames=metricWhitelist)
    fieldict = {k: k for k in writer.fieldnames}
    writer.writerow(fieldict)
    for t in sorted(entries.keys()):
        writer.writerow(entries[t])
    outfile.close()


# This script takes as input a list of CSV performance metric files, and merges/filters them according to a specific
# timestamp window and a whitelist of allowed metrics
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Fin-J CSV Filter and Merge Tool")
    parser.add_argument("-f", action="store", dest="sources", type=str, default=None,
                        help="Path to the CSV files to be analyzed, separated by comma.")
    parser.add_argument("-t", action="store", dest="times", type=str, default=None,
                        help="Starting and end times for filtering, separated by comma.")
    parser.add_argument("-o", action="store", dest="out", type=str, default="out.csv",
                        help="Path to the output file.")
    args = parser.parse_args()
    times = [int(t) for t in args.times.split(',')]if args.times is not None else None
    sources = args.sources.split(',') if args.sources is not None else None
    if times is not None and len(times) != 2:
        print("Starting and end times must be supplied together and separated by comma!")
        exit(-1)
    if sources is None:
        print("You must supply at least one path to a CSV file that must be analyzed!")
        exit(-1)
    mergeAndFilter(sources, args.out, times)
    exit(0)
