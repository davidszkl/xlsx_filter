#!/usr/bin/env python3
import pandas as pd
import os
from typing import List

from models.xlxs_doc import XLSXdoc

UNFILTERED_DIR = "unfiltered"
FILTERED_DIR = "filtered"


def create_docs():
    cwd = os.getcwd()
    src_dir = os.sep.join([cwd, UNFILTERED_DIR])
    dest_dir = os.sep.join([cwd, FILTERED_DIR])
    xlsx_files = filter(lambda f: f.split('.')[-1] == 'xlsx', os.listdir(src_dir))
    xlsx_docs = []
    for f in xlsx_files:
        xlsx_docs.append(
            XLSXdoc(
                df=None,
                src_path=os.sep.join([src_dir, f]),
                dst_path=os.sep.join([dest_dir, "-".join(f.split('-')[:-1])]) + ".xlsx"
            )
        )
    return xlsx_docs

def init_setup():
    os.makedirs(os.sep.join([os.getcwd(), FILTERED_DIR]), exist_ok=True)
    os.makedirs(os.sep.join([os.getcwd(), UNFILTERED_DIR]), exist_ok=True)


if __name__ == "__main__":
    init_setup()
    docs: List[XLSXdoc] = create_docs()
    for doc in docs:
        doc.df = pd.read_excel(doc.src_path, sheet_name="All CCC", header=5)
        doc.prep_table()
        with pd.ExcelWriter(doc.dst_path, engine="openpyxl") as writer:
            doc.filter("1-yr < 7.500")
            doc.filter("Yield < 2.00")
            doc.filter("10-yr < 7.500")
            doc.filter("Equity > 1.00")
            doc.filter("ROE < 10.00")
            doc.filter("($Mil) < 1000.00")
            doc.filter("3-yr < 7.500")
            doc.filter("5-yr < 7.500")
            doc.conditional_filter("Payout.1 > 75.00",
                                   "Industry != 'Equity Real Estate Investment Trusts (REITs)'")
            doc.save_sheet(writer)
