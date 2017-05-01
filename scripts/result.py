import argparse
import os
import sys
from dependency.data_directory import DataDirectory
from strongsup.results.tracker import TopLevelTracker
from strongsup.results.table_drawer import TableDrawer


class ResultRunner(object):
    def __init__(self):
        parser = argparse.ArgumentParser(usage=("results <command> [<args>]\n\n"
            "Supported commands:\n"
            " \ttable\t Draw table of Tracker\n"
            " \trefresh\t Force load a result\n"
            " \tmerge\t Merge two Trackers\n"
            " \tadd\t Add a result\n"
            " \tlist\t List all Trackers\n"
            " \tdelete\t Delete a Tracker\n"))
        parser.add_argument("command", help="subcommand to run")
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            print "Unrecognized command"
            parser.print_help()
            exit(1)

        getattr(self, args.command)()

    # TODO: Don't create a new one if one doesn't exist
    def table(self):
        parser = argparse.ArgumentParser(
                description="Display table of a Tracker")
        parser.add_argument("tracker", help="name of tracker")
        parser.add_argument("--avg", help="average over all seeds",
                action="store_true")
        parser.add_argument("--stddev", help="stddev",
                action="store_true")
        parser.add_argument("--final", help="prints final results",
                action="store_true")
        parser.add_argument("--datasets", nargs="+")
        parser.add_argument("-e", "--experiment_types", nargs="+",
                help="experiment types to filter on (substrings are okay)")
        args = parser.parse_args(sys.argv[2:])
        with TopLevelTracker(args.tracker) as tracker:
            if args.datasets is None:
                for dataset in tracker.datasets:
                    drawer = TableDrawer(tracker.entries(
                        dataset_filters=[dataset],
                        experiment_type_filters=args.experiment_types),
                        dataset)
                    assert not (args.avg and args.stddev)
                    if args.avg:
                        print drawer.avg_table(args.final)
                    elif args.stddev:
                        print drawer.stddev_table(args.final)
                    else:
                        print drawer.all_table(args.final)
            else:
                # TODO: Fix this. Add dataset to entry?
                drawer = TableDrawer(tracker.entries(
                    dataset_filters=args.datasets,
                    experiment_type_filters=args.experiment_types),
                    "All")

                if args.avg:
                    print drawer.avg_table(args.final)
                else:
                    print drawer.all_table(args.final)

    def merge(self):
        parser = argparse.ArgumentParser(
                description="Merge second tracker into first tracker")
        parser.add_argument("tracker", help="tracker to be merged into")
        parser.add_argument("to_merge", help="tracker to merge")
        args = parser.parse_args(sys.argv[2:])
        with TopLevelTracker(args.tracker) as tracker:
            with TopLevelTracker(args.to_merge) as other:
                tracker.merge(other)

    def list(self):
        files = os.listdir(DataDirectory.results)
        for f in files:
            if os.path.splitext(f)[-1] == ".trk":
                print os.path.splitext(os.path.basename(f))[0]

    def delete(self):
        parser = argparse.ArgumentParser(
                description="Delete trackers")
        parser.add_argument("trackers", help="name of trackers to delete",
                            nargs="+")
        args = parser.parse_args(sys.argv[2:])
        for tracker in args.trackers:
            os.remove(TopLevelTracker(tracker).filename)

    def add(self):
        raise NotImplementedError("Not yet implemented")

    def refresh(self):
        raise NotImplementedError("Not yet implemented")


if __name__ == "__main__":
    ResultRunner()
