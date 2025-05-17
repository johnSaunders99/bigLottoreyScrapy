# -*- coding: utf-8 -*-
"""
@author:
@time:
"""
# Writing the analysis module to a .py file
import pandas as pd
from itertools import combinations

def count_number_frequency(df):
    """
    Count the frequency of each number across all draws.
    Expects df with columns ['红1','红2','红3','红4','红5','蓝1','蓝2'] as integers or strings.
    Returns a pandas Series indexed by number, sorted descending by count.
    """
    # Ensure numeric
    num_cols = ['红1','红2','红3','红4','红5','蓝1','蓝2']
    nums = df[num_cols].astype(int)
    all_nums = nums.values.flatten()
    freq = pd.Series(all_nums).value_counts().sort_values(ascending=False)
    return freq

def count_pair_frequency(df):
    """
    Count the frequency of every 2-number combination across all draws.
    Returns a pandas Series indexed by 'xx-yy', sorted descending by count.
    """
    num_cols = ['红1','红2','红3','红4','红5','蓝1','蓝2']
    nums = df[num_cols].astype(int)
    pair_counts = {}
    for row in nums.values:
        # generate all unique pairs
        for a, b in combinations(sorted(row), 2):
            pair_counts[(a, b)] = pair_counts.get((a, b), 0) + 1
    pair_series = pd.Series(pair_counts).sort_values(ascending=False)
    # format index
    pair_series.index = pair_series.index.map(lambda x: f"{x[0]:02d}-{x[1]:02d}")
    return pair_series

def export_to_excel(df, filename):
    """
    Export the raw data and analysis sheets to an Excel file.
    Sheets:
      - RawData: original df
      - NumberRanking: single-number frequency
      - PairRanking: two-number combination frequency
    """
    freq = count_number_frequency(df)
    pair_freq = count_pair_frequency(df)
    with pd.ExcelWriter(filename) as writer:
        df.to_excel(writer, sheet_name='RawData', index=False)
        freq.to_frame('出现次数').to_excel(writer, sheet_name='NumberRanking')
        pair_freq.to_frame('出现次数').to_excel(writer, sheet_name='PairRanking')
if __name__ == "__main__":
    # 抓取示例（前2页）
    data = pd.read_csv(filepath_or_buffer='dlt_with_prizes.csv')
    export_to_excel(data, 'analysis.xlsx')
    print(data.head())