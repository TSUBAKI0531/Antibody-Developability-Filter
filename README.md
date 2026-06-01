# Antibody Developability Filter

**テーマ**: 深層生成モデルによる抗体設計

## 概要

深層生成モデル（GAN、Diffusion、AbLM等）が生成した抗体配列の製造適性（Developability）を物理化学的特性から予測するフィルタリングツールです。溶解度・発現量・開発適性スコアをシミュレーション算出し、沈殿・凝集リスクの高い配列を初期段階でスクリーニングします。結果はPass/Alert 2段階で判定し、製造ラインへの投入可否の判断を支援します。

## 入力

- アミノ酸配列（VH/VL または CDR3）
- 形式: FASTAまたはプレーンテキスト

## 出力

| スコア | 説明 |
|--------|------|
| Calculated solubility index | 溶解度インデックス |
| Estimated expression yield (g/L) | 発現量予測値 |
| Overall developability score | 総合開発適性スコア |

判定: **Pass / Alert** 2段階（アラート閾値はサイドバーで調整可能）

## 使用技術

- Python
- Streamlit
- BioPython（ProteinAnalysis: MW / pI / Aromaticity / GRAVY 算出）

## ローカル起動方法

```bash
pip install -r requirements.txt
streamlit run app.py
```
