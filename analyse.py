# -*- coding: utf-8 -*-
"""
@author:
@time:
"""
# Writing the analysis module to a .py file
import pandas as pd
from itertools import combinations
def count_number_frequency(df: pd.DataFrame):
    """
    统计红区和蓝区号码的出现频次，返回两个 Series：red_counts, blue_counts
    """
    red_cols = ['红1', '红2', '红3', '红4', '红5']
    blue_cols = ['蓝1', '蓝2']
    # 展平红区和蓝区
    red_nums = df[red_cols].values.ravel()
    blue_nums = df[blue_cols].values.ravel()
    # 统计并按号码升序排列
    red_counts = pd.Series(red_nums).value_counts().sort_index()
    blue_counts = pd.Series(blue_nums).value_counts().sort_index()
    return red_counts, blue_counts

def count_pair_frequency(df: pd.DataFrame):
    """
    统计红区内部和蓝区内部的号码组合出现频次，返回两个 Series：red_pair_counts, blue_pair_counts
    """
    red_cols = ['红1', '红2', '红3', '红4', '红5']
    blue_cols = ['蓝1', '蓝2']
    red_pairs = []
    blue_pairs = []
    # 遍历每一行
    for _, row in df.iterrows():
        reds = sorted(row[red_cols].tolist())
        blues = sorted(row[blue_cols].tolist())
        # 红区两两组合
        for i in range(len(reds)):
            for j in range(i+1, len(reds)):
                red_pairs.append(f"{reds[i]}-{reds[j]}")
        # 蓝区两两组合
        for i in range(len(blues)):
            for j in range(i+1, len(blues)):
                blue_pairs.append(f"{blues[i]}-{blues[j]}")
    red_pair_counts = pd.Series(red_pairs).value_counts().sort_index()
    blue_pair_counts = pd.Series(blue_pairs).value_counts().sort_index()
    return red_pair_counts, blue_pair_counts
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