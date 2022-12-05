#!/usr/bin/env python3
import pandas as pd
import operator
import os
from shlex import split as ssplit

UNFILTERED_DIR = "unfiltered"
FILTERED_DIR = "filtered"
OPERATORS = {
    '<': operator.lt,
    '<=': operator.le,
    '>': operator.gt,
    '>=': operator.ge,
    '==': operator.eq,
    '!=': operator.ne,
}
COLUMNS_TO_DELETE = [
    "Seq", "DR", "SP", "Sch", "A/D*", "DEG", "Payout", "Factor", "Rule", "Graham",
    "Annualized", "Price", "Month", "Own.", "$", "%",
]

def sheet_filter(df: pd.DataFrame, domain):
    col, op, val = parse_domain(domain)
    to_drop = []
    for index, row in df.iterrows():
        if op(row[col], val):
            to_drop.append(index)
    print("filtering on '{:8}': deleting {} rows".format(col, len((to_drop))))
    df.drop(to_drop, inplace=True)

def sheet_filter_condition(df: pd.DataFrame, domain, condition):
    col, op, val = parse_domain(domain)
    cond_col, cond_op, cond_val = parse_domain(condition)
    to_drop = []
    for index, row in df.iterrows():
        if op(row[col], val) and cond_op(row[cond_col], cond_val):
            to_drop.append(index)
    print("filtering on '{:8}': deleting {} rows".format(col, len(to_drop)))
    df.drop(to_drop, inplace=True)

def prep_table(df: pd.DataFrame):
    for col in COLUMNS_TO_DELETE:
        df.drop(col, inplace=True, axis=1)

def get_doc_pairs():
    cwd = os.getcwd()
    src_dir = os.sep.join([cwd, UNFILTERED_DIR])
    dest_dir = os.sep.join([cwd, FILTERED_DIR])
    xlsx_files = filter(lambda f: f.split('.')[-1] == 'xlsx', os.listdir(src_dir))
    src_docs = []
    dest_docs = []
    for f in xlsx_files:
        src_docs.append(os.sep.join([src_dir, f]))
        dest_docs.append(os.sep.join([dest_dir, "-".join(f.split('-')[:-1])]) + ".xlsx")
    return zip(src_docs, dest_docs)

def init_setup():
    os.makedirs(os.sep.join([os.getcwd(), FILTERED_DIR]), exist_ok=True)
    os.makedirs(os.sep.join([os.getcwd(), UNFILTERED_DIR]), exist_ok=True)

def parse_domain(domain: str):
    elements = ssplit(domain)
    if not len(elements) == 3:
        return None
    try:
        elements[2] = float(elements[2])
    except ValueError:
        elements[2] = str(elements[2].strip("'"))
    return (
        elements[0],
        OPERATORS[elements[1]],
        elements[2],
    )


if __name__ == "__main__":
    init_setup()
    docs = get_doc_pairs()
    for doc in docs:
        df = pd.read_excel(doc[0], sheet_name="All CCC", header=5)
        prep_table(df)
        with pd.ExcelWriter(doc[1], engine="openpyxl") as writer:
            sheet_filter(df, "1-yr < 7.500")
            sheet_filter(df, "Yield < 2.00")
            sheet_filter(df, "10-yr < 7.500")
            sheet_filter(df, "Equity > 1.00")
            sheet_filter(df, "ROE < 10.00")
            sheet_filter(df, "($Mil) < 1000.00")
            sheet_filter(df, "3-yr < 7.500")
            sheet_filter(df, "5-yr < 7.500")
            sheet_filter_condition(df, "Payout.1 > 75.00",
                                       "Industry != 'Equity Real Estate Investment Trusts (REITs)'")
            df.sort_values(by="Yield", ascending=False, inplace=True)
            df.reset_index(drop=True, inplace=True)
