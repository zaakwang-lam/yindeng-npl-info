# 抓取银登公开公告

只读资产招商专区公开列表，默认只留标题含「个人」的公告。

```bash
pip install -r requirements.txt
python fetch_notices.py --pages 1 --details 8 --out ../data/notices.json
```

- `--pages` 从第 1 页往后翻。站点分页是 `index.html`、`index_{总页数-p+1}.html`。
- `--details` 限制跟进详情页的条数，避免一次打太多请求。
- `--sleep` 默认 1.2 秒。
- 没装 pypdf 时仍会写出标题、链接和 PDF 地址，`fields` 为空。空就是没抽到，不要手填。
- 起拍价不再公开，脚本不解析价格。
