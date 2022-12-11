import pandas as pd
from utils import parse_domain

COLUMNS_TO_DELETE = [
    "Seq", "DR", "SP", "Sch", "A/D*", "DEG", "Payout", "Factor", "Rule", "Graham",
    "Annualized", "Price", "Month", "Own.", "$", "%", "Notes",
]

class XLSXdoc():

    def __init__(self, df=None, *args, **kwargs):
        self.title = "filtered.xlsx"
        self.src_path = ""
        self.dst_path = ""
        self.cols = []
        self.df: pd.DataFrame = None
        self.final_df: pd.DataFrame = None
        self.dropped_rows = {}
        if kwargs:
            self.init_from_kwargs(**kwargs)

    def init_from_kwargs(self, **kwargs):
        for k, v in kwargs.items():
            if k in self.__dict__ or f"_{k}" in self.__dict__:
                self.__setattr__(k, v)

    # pre / post actions
    def prep_table(self, to_delete=COLUMNS_TO_DELETE):
        self.final_df = self.df.copy()
        for col in to_delete:
            if col in self.final_df.columns:
                self.final_df.drop(col, inplace=True, axis=1)

    def save_sheet(self, writer: pd.ExcelWriter):
        self.final_df.sort_values(by="Yield", ascending=False, inplace=True)
        self.final_df.reset_index(drop=True, inplace=True)
        self.final_df.to_excel(writer, sheet_name="All CCC")

    # document actions
    def filter(self, domain):
        col, op, val = parse_domain(domain)
        to_drop = []
        for index, row in self.final_df.iterrows():
            if op(row[col], val):
                to_drop.append(index)
        print("filtering on '{:8}': deleting {} rows".format(col, len((to_drop))))
        self.dropped_rows.update({domain: to_drop})
        self.final_df.drop(to_drop, inplace=True)
        return to_drop

    def conditional_filter(self, domain, condition):
        col, op, val = parse_domain(domain)
        cond_col, cond_op, cond_val = parse_domain(condition)
        to_drop = []
        for index, row in self.final_df.iterrows():
            if op(row[col], val) and cond_op(row[cond_col], cond_val):
                to_drop.append(index)
        print("filtering on '{:8}': deleting {} rows".format(col, len(to_drop)))
        self.dropped_rows.update({domain: to_drop})
        self.final_df.drop(to_drop, inplace=True)
        return to_drop
