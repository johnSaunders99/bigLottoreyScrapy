# -*- coding: utf-8 -*-
"""
@author: 
@time: 
"""
from flask import Flask, render_template_string, request, send_file
import os
import pandas as pd
from datetime import datetime
import time

# 引入之前的抓取函数，做少量调整
from scratch import fetch_dlt_with_prizes  # 假设已放在同目录
from analyse import count_number_frequency, count_pair_frequency  # 假设已放在同目录

app = Flask(__name__)
DATA_FILE = 'dlt_with_prizes.csv'

# HTML 模板
TEMPLATE = '''
<!doctype html>
<title>大乐透微服务</title>
<h1>大乐透数据管理</h1>
<form action="/update" method="post">
    <button type="submit">触发爬取/更新</button>
</form>
<br>
<form action="/stats" method="get">
    开始日期: <input type="date" name="start">
    结束日期: <input type="date" name="end">
    <button type="submit">生成出现频次</button>
</form>
{% if stats is defined %}
    <h2>号码组合出现频次</h2>
    <table border="1">
        <tr><th>Pair</th><th>Count</th></tr>
        {% for pair, cnt in stats.items() %}
            <tr><td>{{ pair }}</td><td>{{ cnt }}</td></tr>
        {% endfor %}
    </table>
{% endif %}
'''


@app.route('/')
def index():
    return render_template_string(TEMPLATE)


@app.route('/update', methods=['POST'])
def update_data():
    # 如果文件不存在，则全量抓取；否则根据最新日期追加
    if os.path.exists(DATA_FILE):
        df_existing = pd.read_csv(DATA_FILE, dtype=str)
        df_existing['date'] = pd.to_datetime(df_existing['date'], format='%Y-%m-%d')
        last_date = df_existing['date'].max().strftime('%Y-%m-%d')
        # 抓取时只抓取新日期
        df_new = fetch_dlt_with_prizes(page_size=30, since_date=last_date)
        if not df_new.empty:
            # 去除已有期号
            new_issues = df_new[~df_new['issue'].isin(df_existing['issue'])]
            if not new_issues.empty:
                new_issues.to_csv(DATA_FILE, mode='a', header=False, index=False)
    else:
        df = fetch_dlt_with_prizes(page_size=30)
        df.to_csv(DATA_FILE, index=False)
    return send_file(DATA_FILE, as_attachment=True)


@app.route('/stats')
def stats():
    start = request.args.get('start')
    end = request.args.get('end')
    df = pd.read_csv(DATA_FILE, dtype=str)
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
    if start:
        df = df[df['date'] >= pd.to_datetime(start)]
    if end:
        df = df[df['date'] <= pd.to_datetime(end)]
    # 统计pair频次
    pairs = []
    for row in df[['红1', '红2', '红3', '红4', '红5', '蓝1', '蓝2']].values:
        nums = sorted(row)
        for i in range(len(nums)):
            for j in range(i + 1, len(nums)):
                pairs.append(f"{nums[i]}-{nums[j]}")
    freq = pd.Series(pairs).value_counts().to_dict()
    return render_template_string(TEMPLATE, stats=freq)


if __name__ == '__main__':
    app.run(debug=True)
