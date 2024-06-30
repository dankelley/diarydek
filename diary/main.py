#!/usr/bin/python3

from .diaryclass import Diary
import argparse
import sys
from csv import reader
import textwrap
import datetime

indent = "  "
showRandomHint = False
defaultDatabase = "~/Dropbox/diary.db"


def diary():
    # print("len(sys.argv) = %d" % len(sys.argv))
    # print("sys.argv = %s" % sys.argv)
    parser = argparse.ArgumentParser(
        prog="diary",
        description="Diary: a diary tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("FIXME: explain more here"),
    )
    parser.add_argument(
        "-d", "--debug", action="store_true", help="Turn on tracer information."
    )
    parser.add_argument(
        "--version", action="store_true", help="Show application version number."
    )
    parser.add_argument(
        "--tags", action="store_true", help="Show tags in database, with counts."
    )
    parser.add_argument(
        "--database",
        type=str,
        default=None,
        help="database location (defaults to %s)" % defaultDatabase,
        metavar="filename",
    )
    parser.add_argument("--list", action="store_true", help="Print entries")
    parser.add_argument(
        "--writeCSV",
        action="store_true",
        help="Write entries to a CSV format that can be read with --readCSV.",
    )
    parser.add_argument(
        "--readCSV",
        type=str,
        default=None,
        help="Read CSV information into database, reversing --writeCSV action.",
        metavar="file.csv",
    )
    parser.add_argument(
        "words", type=str, nargs="*", help="Entry, optionally with tags following ':'"
    )
    args = parser.parse_args()
    if args.words:
        if ":" in args.words:
            start = args.words.index(":") + 1
            tags = args.words[start : len(args.words)]
            entry = " ".join(map(str, args.words[0 : start - 1]))
        else:
            entry = " ".join(map(str, args.words))
            tags = []
    else:
        entry = []
        tags = []
    if args.debug:
        print("  entry: %s" % entry)
        print("  tags:  %s" % tags)
    if not args.database:
        args.database = defaultDatabase
    diary = Diary(debug=args.debug, db=args.database)
    if args.debug:
        print("  database: '%s'" % args.database)

    if args.version:
        (major, minor, subminor) = diary.appversion
        print("diary version %d.%d.%d" % (major, minor, subminor))
        sys.exit(0)

    if args.tags:
        print("Tags in database, with counts:")
        for row in diary.get_tags_with_counts():
            print(" %10s: %d" % (row[0], row[1]))
        sys.exit(0)  # handle --tags

    if args.readCSV:
        with open(args.readCSV) as csv:
            rows = reader(csv)
            for row in rows:
                (time, entry, tagsWithCommas) = row
                # print("<%s> <%s> <%s>" % (time, entry, tagsWithCommas))
                tags = tagsWithCommas.split(",")
                # print(tags)
                diary.add_entry(time, entry, tags)
        sys.exit(0)  # handle --readCSV

    # Write whole database to CSV
    if args.writeCSV:
        tags = diary.get_table("tags")
        entries = diary.get_table("entries")
        entry_tags = diary.get_table("entry_tags")
        if args.debug:
            print("tags: ", end="")
            print(tags)
            print("entries: ", end="")
            print(entries)
            print("entry_tags: ", end="")
            print(entry_tags)
        # put tags in a dictionary, for easier lookup
        taglist = {}
        for tag in tags:
            taglist[tag[0]] = tag[1]
        for entry in entries:
            entryId = entry[0]
            tags = []
            for entry_tag in entry_tags:
                if entry_tag[1] == entryId:
                    tags.append(taglist[entry_tag[2]])
            print('"%s","%s"' % (entry[1], entry[2]), end="")
            if tags:
                print(',"', end="")
                print(",".join(tags), end="")
                print('"', end="")
            else:
                print(',""', end="")
            print("")
        sys.exit(0)  # handle --writeCSV

    if args.list:
        if args.debug:
            print("handling --list")
        tagSearch = []
        entrySearch = ""
        if args.words:
            # print("FIXME: --list needs to handle words and tags.  FYI, words are:")
            if ":" in args.words:
                start = args.words.index(":") + 1
                tagSearch = args.words[start : len(args.words)]
                entrySearch = " ".join(map(str, args.words[0 : start - 1]))
            else:
                entrySearch = " ".join(map(str, args.words))
            if args.debug:
                print("  args.words:  %s" % args.words)
                print("  entrySearch: '%s'" % entrySearch)
                print("  tagSearch:   %s" % tagSearch)
            if tagSearch and len(tagSearch) > 1:
                diary.error(
                    "cannot have more than 1 tag to search, but got: %s" % tagSearch
                )
            # un-tuple it
            if len(tagSearch) == 1:
                tagSearch = tagSearch[0]
        tags = diary.get_table("tags")
        entries = diary.get_table("entries")
        entry_tags = diary.get_table("entry_tags")
        if args.debug:
            print("tags: ", end="")
            print(tags)
            print("entries: ", end="")
            print(entries)
            print("entry_tags: ", end="")
            print(entry_tags)
        # put tags in a dictionary, for easier lookup
        taglist = {}
        for tag in tags:
            taglist[tag[0]] = tag[1]
        if args.debug:
            print("len(entrySearch): %s" % len(entrySearch))
            print("len(tagSearch): %s" % len(tagSearch))
            print("entrySearch: %s" % entrySearch)
            print("tagSearch: %s" % tagSearch)
        for entry in entries:
            entryId = entry[0]
            tags = []
            for entry_tag in entry_tags:
                if entry_tag[1] == entryId:
                    tags.append(taglist[entry_tag[2]])
            showAll = 0 == len(entrySearch) and 0 == len(tagSearch)
            showBasedOnEntry = 0 < len(entrySearch) and entrySearch in entry[2]
            showBasedOnTag = 0 < len(tagSearch) and tagSearch in tags
            show = showAll or showBasedOnEntry or showBasedOnTag
            if args.debug:
                print("  entrySearch:", entrySearch)
                print("  entry: ", entry[2])
                print("  tagSearch:", tagSearch)
                print("  tags: ", tags)
                print("  showAll: %d" % showAll)
                print("  showBasedOnEntry: %d" % showBasedOnEntry)
                print("  showBasedOnTag: %d" % showBasedOnTag)
                print("  show: %d" % show)
            if show:
                print("%s %s" % (entry[1], entry[2]), end="")
                if tags:
                    print(" : ", end="")
                    for tag in tags:
                        print(tag, end=" ")
                print()
        sys.exit(0)  # handle --list

    # Database insertion
    elif args.words:
        time = datetime.datetime.now()
        diary.add_entry(time, entry, tags)
    else:
        print("Try -h to learn how to use this")
