#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Author: TheCjw<thecjw@qq.com>
# Created on 下午12:55 15/1/31
import tarfile

__author__ = "TheCjw"

import os
import sqlite3


def parse_search_data(path):
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
            doc_path = result[1][1][0].replace("../", "./html/")
            keywords.append([name, current_type, doc_path])

    return keywords


def init_pin_doc():
    archive_path = os.path.join(os.path.dirname(__file__), "pin-2.14-67254-clang.5.1-mac.tar.gz")
    tar = tarfile.open(archive_path)
    pin_doc_files = []
    xed32_doc_files = []
    xed64_doc_files = []
    for tarinfo in tar.getmembers():
        if tarinfo.name.find("/doc/html") != -1:
            tarinfo.name = os.path.basename(tarinfo.name)
            pin_doc_files.append(tarinfo)
        elif tarinfo.name.find("extras/xed2-ia32/doc/ref-manual/html") != -1:
            tarinfo.name = os.path.basename(tarinfo.name)
            xed32_doc_files.append(tarinfo)
        elif tarinfo.name.find("extras/xed2-intel64/doc/ref-manual/html") != -1:
            tarinfo.name = os.path.basename(tarinfo.name)
            xed64_doc_files.append(tarinfo)

    output_path = os.path.join(os.path.dirname(__file__), "test", "pin")
    tar.extractall(path=output_path, members=pin_doc_files)
    output_path = os.path.join(os.path.dirname(__file__), "test", "xed32")
    tar.extractall(path=output_path, members=xed32_doc_files)
    output_path = os.path.join(os.path.dirname(__file__), "test", "xed64")
    tar.extractall(path=output_path, members=xed64_doc_files)

    tar.close()


def main():
    docset_dir = os.path.join(os.path.dirname(__file__), "Pin.docset")
    doc_file_dir = os.path.join(docset_dir, "Contents", "Resources", "Documents", "html")
    keywords = parse_search_data(doc_file_dir)

    dsidx_path = os.path.join(docset_dir, "Contents", "Resources", "docSet.dsidx")

    try:
        db = sqlite3.connect(dsidx_path)
        cur = db.cursor()
        cur.execute("DROP TABLE IF EXISTS searchIndex")
        cur.execute("CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);")

        for key in keywords:
            cur.execute("INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)",
                        (key[0], key[1], key[2]))
        db.commit()
        db.close()
    except Exception as e:
        print e.message
        raise


if __name__ == "__main__":
    # main()
    init_pin_doc()
