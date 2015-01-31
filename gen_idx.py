#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Author: TheCjw<thecjw@qq.com>
# Created on 下午12:55 15/1/31

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


def main():
    docset_dir = os.path.join(os.getcwd(), "Pin.docset")
    doc_file_dir = os.path.join(docset_dir, "Contents", "Resources", "Documents", "html")
    keywords = parse_search_data(doc_file_dir)

    dsidx_path = os.path.join(docset_dir, "Contents", "Resources", "docSet.dsidx")

    try:
        db = sqlite3.connect(dsidx_path)
        cur = db.cursor()
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
    main()
