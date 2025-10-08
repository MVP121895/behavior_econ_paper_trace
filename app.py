"""Streamlit app for tracking behaviour economics articles."""

from __future__ import annotations

from datetime import datetime
from typing import List

import pandas as pd
import streamlit as st

from journals import BEHAVIOR_JOURNALS
from utils import Article, default_from_date, fetch_articles


st.set_page_config(page_title="行为经济学顶刊追踪", layout="wide")

st.title("行为经济学顶刊追踪")
st.markdown("使用 OpenAlex API 抓取经济学、金融学及行为经济学顶刊相关论文，并展示摘要与相关概念。")


def fetch_for_selected_journals(selected_journals: List[str], keyword: str, years: int, max_results: int, mailto: str | None) -> List[Article]:
    articles: list[Article] = []
    from_date = default_from_date(years=years)

    progress = st.progress(0, text="开始抓取...")
    total = len(selected_journals)

    for idx, journal in enumerate(selected_journals, start=1):
        issn = BEHAVIOR_JOURNALS[journal]
        try:
            articles.extend(fetch_articles(issn=issn, keyword=keyword, from_date=from_date, max_results=max_results, mailto=mailto))
        except Exception as exc:  # noqa: BLE001
            st.warning(f"{journal} 抓取失败：{exc}")
        progress.progress(idx / total, text=f"{journal} 完成 ({idx}/{total})")

    progress.empty()
    return articles


with st.sidebar:
    st.header("参数设置")
    keyword = st.text_input("关键词", value="behavioral economics")
    years = st.slider("回溯年份", min_value=1, max_value=20, value=10)
    max_results = st.slider("每刊最大返回数", min_value=10, max_value=200, value=50, step=10)
    mailto = st.text_input("Contact Email (可选)")

    st.subheader("选择期刊")
    selected_journals = st.multiselect(
        "顶刊列表",
        options=list(BEHAVIOR_JOURNALS.keys()),
        default=list(BEHAVIOR_JOURNALS.keys()),
    )

    fetch_button = st.button("开始抓取", type="primary")


if fetch_button:
    if not selected_journals:
        st.error("至少选择一个期刊。")
    else:
        st.info("抓取过程中请耐心等待，完成后会显示结果。")
        articles = fetch_for_selected_journals(selected_journals, keyword, years, max_results, mailto or None)

        if not articles:
            st.warning("未获取到任何文章，可尝试更换关键词或延长时间范围。")
        else:
            df = pd.DataFrame(
                [
                    {
                        "title": article.title,
                        "authors": ", ".join(article.authors),
                        "journal": article.journal,
                        "published_date": article.published_date,
                        "doi": article.doi,
                        "url": article.url,
                        "abstract": article.abstract,
                        "concepts": ", ".join(article.concepts),
                    }
                    for article in articles
                ]
            )

            st.success(f"抓取完成，共 {len(df)} 篇文章")

            st.dataframe(
                df,
                use_container_width=True,
                column_config={
                    "title": st.column_config.TextColumn("标题", width="large"),
                    "authors": st.column_config.TextColumn("作者"),
                    "journal": st.column_config.TextColumn("期刊"),
                    "published_date": st.column_config.DateColumn("发布日期"),
                    "doi": st.column_config.TextColumn("DOI"),
                    "url": st.column_config.LinkColumn("链接"),
                    "abstract": st.column_config.TextColumn("摘要", width="large"),
                    "concepts": st.column_config.TextColumn("相关概念"),
                },
            )

            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("下载 CSV", data=csv, file_name="behavior_articles.csv", mime="text/csv")

else:
    st.info("在侧边栏调整参数并点击“开始抓取”即可获取最新文章。")



