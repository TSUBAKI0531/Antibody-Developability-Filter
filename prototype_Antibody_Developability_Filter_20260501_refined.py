import logging
from typing import Dict, List, Optional

import pandas as pd
import streamlit as st
from Bio.SeqUtils.ProtParam import ProteinAnalysis

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

_GRAVY_THRESHOLD = 0.0
_PI_THRESHOLD = 9.0


def analyze_sequence(row_id: str, sequence: str) -> Optional[Dict[str, float]]:
    """単一のアミノ酸配列からDevelopability指標を算出する。

    Args:
        row_id: クローン識別子（ログおよび結果テーブルで使用）。
        sequence: アミノ酸一文字表記のVH/CDR配列。

    Returns:
        "id", "pI", "GRAVY" を格納したdict。
        無効な配列またはProteinAnalysis失敗時はNone。
    """
    cleaned = sequence.strip().upper()
    if not cleaned:
        logger.warning("id=%s: 空の配列をスキップします", row_id)
        return None
    try:
        pa = ProteinAnalysis(cleaned)
        result = {
            "id": row_id,
            "pI": round(pa.isoelectric_point(), 3),
            "GRAVY": round(pa.gravy(), 4),
        }
        logger.info("id=%s: pI=%.3f, GRAVY=%.4f", row_id, result["pI"], result["GRAVY"])
        return result
    except ValueError as e:
        logger.error("id=%s: 無効なアミノ酸配列 — %s", row_id, e)
        return None
    except Exception as e:
        logger.error("id=%s: 解析中に予期しないエラー — %s", row_id, e)
        return None


def compute_developability(df: pd.DataFrame) -> pd.DataFrame:
    """DataFrameの全行に対してDevelopability指標を一括算出する。

    Args:
        df: "id" 列と "sequence" 列を持つpandas DataFrame。
            CSVアップロード結果を想定。

    Returns:
        有効な配列のみを含む結果DataFrame（"id", "pI", "GRAVY" 列）。
        全行が無効な場合は空のDataFrameを返す。

    Raises:
        KeyError: "id" または "sequence" 列が存在しない場合。
    """
    if "id" not in df.columns or "sequence" not in df.columns:
        raise KeyError("CSVには 'id' と 'sequence' 列が必要です。")

    records: List[Dict[str, float]] = []
    for _, row in df.iterrows():
        result = analyze_sequence(str(row["id"]), str(row["sequence"]))
        if result is not None:
            records.append(result)

    logger.info(
        "バッチ解析完了: %d 件入力 / %d 件成功", len(df), len(records)
    )
    return pd.DataFrame(records)


def filter_candidates(res_df: pd.DataFrame) -> pd.DataFrame:
    """Developability基準を満たすクローンをフィルタリングする。

    基準: GRAVY < 0.0（親水性） かつ pI < 9.0（等電点が生理的範囲内）

    Args:
        res_df: compute_developability() が返すDataFrame。

    Returns:
        フィルタを通過したクローンのみを含むDataFrame。
    """
    if res_df.empty:
        logger.warning("フィルタ対象のデータが空です")
        return res_df
    passed = res_df[
        (res_df["GRAVY"] < _GRAVY_THRESHOLD) & (res_df["pI"] < _PI_THRESHOLD)
    ]
    logger.info(
        "フィルタ結果: %d 件中 %d 件が通過 (GRAVY<%.1f, pI<%.1f)",
        len(res_df), len(passed), _GRAVY_THRESHOLD, _PI_THRESHOLD,
    )
    return passed


def main() -> None:
    """AI-Antibody Developability FilterのStreamlitアプリエントリポイント。"""
    st.title("AI-Antibody Developability Filter")
    st.write("連携: Protein Hydrophobicity Profiler")

    st.caption(
        f"フィルタ基準: GRAVY < {_GRAVY_THRESHOLD}（親水性）"
        f" かつ pI < {_PI_THRESHOLD}（等電点）"
    )

    uploaded_file = st.file_uploader(
        "Upload CSV (columns: id, sequence)", type="csv"
    )

    if uploaded_file is None:
        return

    try:
        df = pd.read_csv(uploaded_file)
        logger.info("CSVアップロード完了: %d 行", len(df))
    except Exception as e:
        st.error(f"CSVの読み込みに失敗しました: {e}")
        logger.error("CSV読み込みエラー: %s", e)
        return

    try:
        res_df = compute_developability(df)
    except KeyError as e:
        st.error(str(e))
        logger.error("列不足エラー: %s", e)
        return

    if res_df.empty:
        st.warning("有効な配列が1件もありませんでした。CSVの内容を確認してください。")
        return

    st.subheader("全配列の解析結果")
    st.dataframe(res_df)

    passed = filter_candidates(res_df)

    st.subheader("フィルタ通過クローン")
    st.success(
        f"{len(df)} 件中 {len(passed)} 件が開発可能性フィルタを通過しました。"
    )
    st.dataframe(passed)


main()
