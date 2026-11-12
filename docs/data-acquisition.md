# 数据获取方案

## 流程
1. 定时抓取银登网转让公告列表页（https://www.yindeng.com.cn/ 相关路径）
2. 解析新公告链接，下载PDF
3. 使用 pdfplumber 提取字段（参考 https://github.com/Mistborntt/PDFtoExcel ）
4. 结构化存储到数据库
5. 小程序后端API提供查询

## 技术选择
- Python + pdfplumber + requests
- 云函数（腾讯云/阿里云）定时触发
- 数据库：云开发或轻量方案

## 注意事项
- 仅抓取公开信息
- 控制频率，避免对网站造成压力
- 提取规则需随PDF格式变化调整
