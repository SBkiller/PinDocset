#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Author: TheCjw<thecjw@qq.com>
# Created on 下午12:55 15/1/31
import tarfile

__author__ = "TheCjw"

import os
import sqlite3


def parse_search_data(path):
    sub_dir = os.path.split(path)[1]
    search_dir = os.path.join(path, "search")
    js_files = [os.path.join(search_dir, file_name) for file_name in os.listdir(search_dir)
                if file_name.endswith(".js") and file_name != "search.js" and file_name.startswith("all_") == False]

    keywords = []
    # http://kapeli.com/docsets#supportedentrytypes
    entry_type = {
        "files": "File",
        "functions": "Function",
        "variables": "Variable",
        "enumvalues": "Enum",
        "classes": "Class",
        "typedefs": "Type",
        "groups": "Entry",
        "enums": "Enum",
        "pages": "Guide"
    }

    for file_name in js_files:
        lines = open(file_name).readlines()

        type = file_name.split("/")[-1].split("_")[0]
        current_type = entry_type.get(type)

        for line in lines:
            line = line.strip()
            if line.find("]]]") == -1:
                continue
            if line[-1:] == ",":
                line = line[:len(line) - 1]

            result = eval(line)

            name = result[1][0]
            doc_path = result[1][1][0].replace("../", "./{0}/".format(sub_dir))
            keywords.append([name, current_type, doc_path])

    return keywords


def adjust_archive_name(file_path):
    path, file_name = os.path.split(file_path)
    if path[-6:] == "search":
        file_name = os.path.join("search", file_name)
    return file_name


def main():
    docset_dir = os.path.join(os.path.dirname(__file__), "Pin.docset")

    pin_doc = os.path.join(docset_dir, "Contents", "Resources", "Documents", "pin")
    xed32_doc = os.path.join(docset_dir, "Contents", "Resources", "Documents", "xed32")
    xed64_doc = os.path.join(docset_dir, "Contents", "Resources", "Documents", "xed64")

    archive_path = os.path.join(os.path.dirname(__file__), "pin-2.14-67254-clang.5.1-mac.tar.gz")
    tar = tarfile.open(archive_path)
    pin_doc_files = []
    xed32_doc_files = []
    xed64_doc_files = []
    for tarinfo in tar.getmembers():
        if tarinfo.name.find("/doc/html/") != -1:
            tarinfo.name = adjust_archive_name(tarinfo.name)
            pin_doc_files.append(tarinfo)

        elif tarinfo.name.find("extras/xed2-ia32/doc/ref-manual/html/") != -1:
            tarinfo.name = adjust_archive_name(tarinfo.name)
            xed32_doc_files.append(tarinfo)

        elif tarinfo.name.find("extras/xed2-intel64/doc/ref-manual/html/") != -1:
            tarinfo.name = adjust_archive_name(tarinfo.name)
            xed64_doc_files.append(tarinfo)

    tar.extractall(path=pin_doc, members=pin_doc_files)
    tar.extractall(path=xed32_doc, members=xed32_doc_files)
    tar.extractall(path=xed64_doc, members=xed64_doc_files)
    tar.close()

    pin_keywords = parse_search_data(pin_doc)
    xed32_keywords = parse_search_data(xed32_doc)
    xed64_keywords = parse_search_data(xed64_doc)

    print "Pin Index: {0}".format(len(pin_keywords))
    print "Xed32 Index: {0}".format(len(xed32_keywords))
    print "Xed64 Index: {0}".format(len(xed64_keywords))

    dsidx_path = os.path.join(docset_dir, "Contents", "Resources", "docSet.dsidx")

    try:

        db = sqlite3.connect(dsidx_path)
        cur = db.cursor()
        cur.execute("DROP TABLE IF EXISTS searchIndex")
        cur.execute("CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);")

        for key in pin_keywords:
            cur.execute("INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)",
                        (key[0], key[1], key[2]))

        for key in xed32_keywords:
            cur.execute("INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)",
                        (key[0], key[1], key[2]))

        for key in xed64_keywords:
            cur.execute("INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)",
                        (key[0], key[1], key[2]))

        db.commit()
        db.close()

    except Exception as e:
        print e.message
        raise

    os.system("tar --exclude='.DS_Store' -cvzf Pin_Docset.tgz Pin.docset")


if __name__ == "__main__":
    main()
