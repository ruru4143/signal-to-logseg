#!/bin/python3
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
import os

with open("config.json", "r") as f:
    config = json.load(f)

logseq_root = Path(config["logseq_root"])
XDG_DATA_HOME = os.environ["XDG_DATA_HOME"] if "XDG_DATA_HOME" in os.environ.keys() else config['xdg_data_home']
page_filename_template = config["page_template"]
tag_template = config["tag_template"]

assert XDG_DATA_HOME != ""

logseq_pages = logseq_root.joinpath("pages")
logseq_assets = logseq_root.joinpath("assets")

attachment_source = Path(XDG_DATA_HOME).joinpath("signal-cli/attachments")

assert logseq_pages.exists()
assert attachment_source.exists()



def save_to_logseg(msg):
    handle_attachments(msg)
    block = get_content(msg)
    print(f"Saving msg...")

    filename = logseq_pages.joinpath(format_timestamp(msg, page_filename_template))

    if filename.exists():
        with open(filename, "a") as page:
            page.write(block + "\n")
    else:
        with open(filename, "w") as page:
            page.write(block + "\n")

def format_timestamp(msg, template):
    return datetime.fromtimestamp(msg["timestamp"] / 1000).strftime(template)

def get_content(msg):
    block = format_timestamp(msg, tag_template) + " "

    if msg["message"]:
        block += msg["message"]

    if msg["attachments"] and len(msg["attachments"]) > 0:
        for attachment in msg["attachments"]:
            filename = attachment["filename"]
            link = f"![{filename}](../assets/{filename})"
            block += " " + link

    return "- " + block + "\n"


def handle_attachments(msg):
    if msg["attachments"] and len(msg["attachments"]) > 0:
        for attachment in msg["attachments"]:
            filename = attachment["filename"]
            filepath = attachment["filepath"]
            
            # Filename formatting
            if filename is None:
                filename = format_timestamp(msg, "%Y-%m-%d-") + attachment["id"]

            filename = "signal-" + filename
            attachment["filename"] = filename

            if filepath.exists():
                filepath = filepath.rename(filename)
                filepath = filepath.rename(logseq_assets.joinpath(filename))
                attachment["filepath"] = filepath

                print(filepath)
            else:
                print(f"File {filepath} not found.")
            



def add_missing_fileinformation(msg):
    """ This only works because dicts and lists are passed by reference in python.
    """
    attachment_list = msg["attachments"]
    if attachment_list and len(attachment_list) > 0:
        for idx, attachment in enumerate(attachment_list):
            attachment["filepath"] = attachment_source.joinpath(attachment["id"])

def get_data():
    parser = argparse.ArgumentParser()

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("FILE", nargs="?")
    group.add_argument("--read-from-stdin", action="store_true", default=False)


    args = parser.parse_args()
    args.FILE

    if args.read_from_stdin:
        data = sys.stdin.readlines()
        return json.loads("".join(data))
    else:
        with open(args.FILE, "r") as f:
            return json.load(f)


if __name__ == "__main__":
    data = get_data()

    for msg in data:
        add_missing_fileinformation(msg)
        save_to_logseg(msg)
