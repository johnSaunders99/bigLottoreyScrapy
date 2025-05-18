from flask import Flask, render_template_string, request
import os
import pandas as pd

# 引入之前的抓取函数和分析函数
from scratch import fetch_dlt_with_prizes
from analyse import count_number_frequency, count_pair_frequency

app = Flask(__name__)
DATA_FILE = 'dlt_with_prizes.csv'

# HTML 模板，添加排序选项、并排展示表格
TEMPLATE = '''
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>大乐透微服务</title>
  <style>
    .container { width: 90%; margin: auto; }
    .flex { display: flex; gap: 20px; }
    .flex table { border-collapse: collapse; width: 100%; }
    table, th, td { border: 1px solid #888; padding: 4px; text-align: center; }
    th { background: #f0f0f0; }
  </style>
</head>
<body>
<div class="container">
  <h1>大乐透数据管理</h1>
  <form action="/update" method="post">
    <button type="submit">触发爬取/更新</button>
  </form>
  <br>
  <form action="/stats" method="get">
    开始日期: <input type="date" name="start">
    结束日期: <input type="date" name="end"><br><br>
    模式:
    <label><input type="radio" name="mode" value="pair" {% if mode!='single' %}checked{% endif %}> 组合频次</label>
    <label><input type="radio" name="mode" value="single" {% if mode=='single' %}checked{% endif %}> 单号码频次</label><br><br>
    排序:
    <select name="sort_by">
      <option value="key" {% if sort_by=='key' %}selected{% endif %}>按号码/组合</option>
      <option value="count" {% if sort_by=='count' %}selected{% endif %}>按出现次数</option>
    </select>
    <button type="submit">生成统计</button>
  </form>
  <br>
  <form action="/recommend" method="get">
    幸运号码: <input type="text" name="lucky" placeholder="如 05，必须两位数字">
    <button type="submit">推荐搭配</button>
  </form>
  {% if message is defined %}
    <p><strong>{{ message }}</strong></p>
  {% endif %}

  {% if mode == 'single' and red_stats is defined and blue_stats is defined %}
  <div class="flex">
    <div>
      <h2>红区出现频次</h2>
      <table>
        <tr><th>Number</th><th>Count</th></tr>
        {% for num, cnt in red_stats %}
        <tr><td>{{ num }}</td><td>{{ cnt }}</td></tr>
        {% endfor %}
      </table>
    </div>
    <div>
      <h2>蓝区出现频次</h2>
      <table>
        <tr><th>Number</th><th>Count</th></tr>
        {% for num, cnt in blue_stats %}
        <tr><td>{{ num }}</td><td>{{ cnt }}</td></tr>
        {% endfor %}
      </table>
    </div>
  </div>
  {% elif mode == 'pair' and red_stats is defined and blue_stats is defined %}
  <div class="flex">
    <div>
      <h2>红区组合频次</h2>
      <table>
        <tr><th>Pair</th><th>Count</th></tr>
        {% for pair, cnt in red_stats %}
        <tr><td>{{ pair }}</td><td>{{ cnt }}</td></tr>
        {% endfor %}
      </table>
    </div>
    <div>
      <h2>蓝区组合频次</h2>
      <table>
        <tr><th>Pair</th><th>Count</th></tr>
        {% for pair, cnt in blue_stats %}
        <tr><td>{{ pair }}</td><td>{{ cnt }}</td></tr>
        {% endfor %}
      </table>
    </div>
  </div>
  {% endif %}

  {% if rec_red is defined and rec_blue is defined %}
  <h2>针对幸运号码 {{ lucky }} 的推荐搭配（按出现次数降序）</h2>
  <div class="flex">
    <div>
      <h3>红区热配</h3>
      <table>
        <tr><th>Pair</th><th>Count</th></tr>
        {% for pair, cnt in rec_red %}
        <tr><td>{{ pair }}</td><td>{{ cnt }}</td></tr>
        {% endfor %}
      </table>
    </div>
    <div>
      <h3>蓝区热配</h3>
      <table>
        <tr><th>Pair</th><th>Count</th></tr>
        {% for pair, cnt in rec_blue %}
        <tr><td>{{ pair }}</td><td>{{ cnt }}</td></tr>
        {% endfor %}
      </table>
    </div>
  </div>
  {% endif %}
</div>
</body>
</html>
'''

@app.route('/')
def index():
    # 默认参数
    return render_template_string(TEMPLATE, mode='pair', sort_by='key')

@app.route('/update', methods=['POST'])
def update_data():
    # 同之前逻辑
    if os.path.exists(DATA_FILE):
        df_local = pd.read_csv(DATA_FILE, dtype=str)
        first_issue = df_local.iloc[0]['issue']
    else:
        df_local = pd.DataFrame(); first_issue = None
    new_rows=[]; page=1
    while True:
        result=fetch_dlt_with_prizes(page_size=30,page=page)
        if result.empty: break
        for _,r in result.iterrows():
            if first_issue and r['issue']==first_issue:
                page=None; break
            new_rows.append(r)
        if page is None: break
        page+=1
    added=0
    if new_rows:
        df_new=pd.DataFrame(new_rows).drop_duplicates(subset=['issue'])
        df_merged=pd.concat([df_new,df_local],ignore_index=True)
        df_merged.sort_values(by='issue',ascending=False,inplace=True)
        df_merged.to_csv(DATA_FILE,index=False)
        added=len(df_new)
    message=f"更新完成，新增 {added} 条记录。"
    return render_template_string(TEMPLATE, message=message, mode='pair', sort_by='key')

@app.route('/stats')
def stats():
    start,end,mode,sort_by = request.args.get('start'),request.args.get('end'),request.args.get('mode','pair'),request.args.get('sort_by','key')
    df=pd.read_csv(DATA_FILE,dtype=str);
    df['日期']=pd.to_datetime(df['日期'],format='%Y-%m-%d')
    if start: df=df[df['日期']>=pd.to_datetime(start)]
    if end: df=df[df['日期']<=pd.to_datetime(end)]

    # 获取统计结果
    if mode=='single':
        red_counts,blue_counts=count_number_frequency(df)
        red=red_counts.items(); blue=blue_counts.items()
    else:
        red_counts,blue_counts=count_pair_frequency(df)
        red=red_counts.items(); blue=blue_counts.items()
    # 排序
    if sort_by=='count':
        red_stats=sorted(red,key=lambda x: x[1],reverse=True)
        blue_stats=sorted(blue,key=lambda x: x[1],reverse=True)
    else:
        red_stats=sorted(red,key=lambda x: x[0])
        blue_stats=sorted(blue,key=lambda x: x[0])

    return render_template_string(TEMPLATE, mode=mode, sort_by=sort_by,
        red_stats=red_stats, blue_stats=blue_stats)

@app.route('/recommend')
def recommend():
    lucky = request.args.get('lucky')
    df = pd.read_csv(DATA_FILE, dtype=str)
    # 红蓝区配对频次
    red_pairs, blue_pairs = count_pair_frequency(df)
    # 过滤包含幸运号码的配对
    rec_red = red_pairs[red_pairs.index.str.contains(lucky, regex=False)]
    rec_blue = blue_pairs[blue_pairs.index.str.contains(lucky, regex=False)]
    # 转列表并取前10
    rec_red = rec_red.sort_values(ascending=False).head(10).items()
    rec_blue = rec_blue.sort_values(ascending=False).head(10).items()
    message = f"基于号码 {lucky} 的推荐搭配如下："
    return render_template_string(
        TEMPLATE,
        rec_red=rec_red,
        rec_blue=rec_blue,
        lucky=lucky,
        message=message,
        mode='',
        sort_by=''
    )

if __name__=='__main__':
    app.run()
