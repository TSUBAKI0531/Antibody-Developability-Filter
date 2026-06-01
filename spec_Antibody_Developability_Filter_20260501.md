# 仕様書: AI-Antibody Developability Filter

## 1. 概要
OmniAb-LM等で生成された数百のCDR/VH配列候補を一括評価し、Developability（開発可能性）の基準を満たすクローンだけをフィルタリングする。

## 2. 主要機能
- CSV/FASTA形式による生成配列のバッチアップロード
- 等電点、親水性、電荷分布の一括計算
- 基準値外の配列をフィルタリングし、散布図として可視化

## 3. 技術スタック
- Python, Streamlit, pandas, BioPython, matplotlib/seaborn
