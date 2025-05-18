# -*- coding: utf-8 -*-
import requests, time
import pandas as pd

def fetch_dlt_with_prizes(game_no=85, province_id=0, page_size=30, max_pages=None, since_date=None):
    url = "https://webapi.sporttery.cn/gateway/lottery/getHistoryPageListV1.qry"
    records = []
    page_no = 1
    needUpdate = 0
    enough = 0
    if since_date is not None:
        needUpdate = 1
    splitColumns = ['红1', '红2', '红3', '红4', '红5', '蓝1', '蓝2']
    while True:
        params = {
            'gameNo': game_no,
            'provinceId': province_id,
            'pageSize': page_size,
            'isVerify': 1,
            'pageNo': page_no
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/116.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Referer': 'https://www.lottery.gov.cn/kj/kjlb.html?dlt',
            'Connection': 'keep-alive',
            'Origin': 'https://static.sporttery.cn',
            'Referer': 'https://static.sporttery.cn/'
        }
        time.sleep(5)
        resp = requests.get(url, params=params, timeout=10, headers=headers)
        resp.encoding = resp.apparent_encoding
        if resp.status_code == 403:
            print(f"第{page_no}页被拒绝，请等待后稍后重试…")
            break
        data_list = resp.json().get('value', {}).get('list', [])
        if not data_list:
            break
        for entry in data_list:
            if needUpdate == 1 and since_date >= entry['lotteryDrawTime']:
                enough = 1
                # 更新数据日期大于等于已有数据,不插入更新且因为是倒序时间,后面同样都低于,直接结束
                break
            drawRes = entry.get('lotteryDrawResult', '').replace('+', ' | ')
            rec = {
                '期号': entry['lotteryDrawNum'],
                '日期': entry['lotteryDrawTime'],
                '出球顺序': entry.get('lotteryUnsortDrawresult', ''),
                '中奖号码': drawRes
            }
            rec.update(zip(splitColumns, drawRes.split()))
            # 将每个奖级的中奖人数提取为单独列
            for level in entry.get('prizeLevelList', []):
                lvl_name = level['prizeLevel']
                rec[f"{lvl_name}中奖人数"] = int(level['stakeCount'].replace(',', ''))
            records.append(rec)


        page_no += 1
        if max_pages and page_no > max_pages:
            break
        if needUpdate == 1 and enough == 1:
            break

    df = pd.DataFrame(records)
    return df

if __name__ == "__main__":
    # 抓取示例（前2页）
    df = fetch_dlt_with_prizes(page_size=30)
    print(df.head())
    # 保存为 CSV
    df.to_csv('dlt_with_prizes.csv', index=False, encoding='utf-8-sig')
    print(f"共抓取到 {len(df)} 条记录")