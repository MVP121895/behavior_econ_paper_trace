# 行为经济学顶刊追踪 Streamlit 应用

该项目将行为经济学顶刊追踪功能封装为一个 Streamlit Web 应用，可直接部署到 Streamlit Cloud 或 GitHub。应用通过 Crossref API 抓取近十年内包含指定关键词的论文，并支持筛选期刊、调整关键词、下载结果。

## 主要特性
- 覆盖经济学五大刊、金融三大刊及行为经济学核心期刊
- 自定义关键词、回溯年份、每刊最大返回数量
- 支持选择期刊组合、实时进度提示
- 结果表格可排序/筛选，并支持导出 CSV

## 快速运行
1. 创建并激活虚拟环境（可选）：
   ```bash
   cd /Users/joewong/PycharmProjects/streamlit_behavior_tracker
   python3 -m venv .venv
   source .venv/bin/activate  # Windows 使用 .venv\Scripts\activate
   ```
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
3. 启动 Streamlit 应用：
   ```bash
   streamlit run app.py
   ```
4. 浏览器访问命令行提示的本地链接即可使用。

## 部署到 Streamlit Cloud
1. 将仓库推送到 GitHub（例如 `streamlit_behavior_tracker`）。
2. 登录 [Streamlit Cloud](https://streamlit.io/cloud)，选择 “New app”。
3. 选择仓库与分支，填写 `app.py` 作为入口文件，点击部署。
4. 在 “Secrets” 中可配置 `MAILTO` 等环境变量（如需传给 Crossref）。

## 关键文件
- `app.py`：Streamlit 前端与抓取调用逻辑
- `utils.py`：Crossref 请求、数据解析工具
- `journals.py`：期刊列表与 ISSN 配置
- `requirements.txt`：运行所需依赖

## 自定义与扩展
- 在 `journals.py` 中调整期刊列表
- 在 `utils.py` 的 `fetch_articles` 中设置超时、重试策略
- 可添加缓存（如 `st.cache_data`）减少重复请求
- 如需更复杂的分析，可在抓取后增加情感分析、主题标注等处理


