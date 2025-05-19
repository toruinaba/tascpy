"""日本語フォントサポートの機能テスト"""

import os
import pytest
import numpy as np
from pathlib import Path
import tempfile
import shutil

# Matplotlibのバックエンドを設定（グラフィカルバックエンドを使用しない）
import matplotlib

matplotlib.use("Agg")  # 非対話的なバックエンドを使用
import matplotlib.pyplot as plt

from tascpy.core.collection import ColumnCollection
from tascpy.core.column import Column


@pytest.fixture
def japanese_sample_collection():
    """日本語ラベルを含むサンプルデータを作成"""
    # 日本語のカラム名とラベルを含むCollectionを作成
    return ColumnCollection(
        step=[1, 2, 3, 4, 5],
        columns={
            "変位": Column("1", "変位", "mm", [1, 2, 3, 4, 5]),
            "荷重": Column("2", "荷重", "kN", [10, 20, 30, 40, 50]),
            "温度": Column("3", "温度", "℃", [25, 26, 27, 28, 29]),
        },
        metadata={"description": "日本語テスト用コレクション"},
    )


class TestJapaneseFont:
    """日本語フォントサポートのテスト"""

    def setup_method(self):
        """各テスト前に一時ディレクトリを作成"""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """各テスト後に一時ディレクトリを削除"""
        shutil.rmtree(self.temp_dir)

    def test_japanese_labels(self, japanese_sample_collection):
        """日本語のラベルとタイトルが正しく表示されるかテスト"""
        # プロットの作成
        fig, ax = plt.subplots(figsize=(8, 6))

        # 日本語タイトルとラベルを設定
        ax.set_title("日本語のタイトル")
        ax.set_xlabel("変位 (mm)")
        ax.set_ylabel("荷重 (kN)")

        # データのプロット
        ax.plot(
            japanese_sample_collection["変位"].values,
            japanese_sample_collection["荷重"].values,
            marker="o",
            label="試験データ",
        )

        # 凡例を追加
        ax.legend()
        ax.grid(True)

        # グラフを保存
        output_path = Path(self.temp_dir) / "japanese_labels.png"
        fig.savefig(output_path)
        plt.close(fig)

        # ファイルが作成され、サイズが0より大きいことを確認
        assert output_path.exists()
        assert output_path.stat().st_size > 0

    def test_japanese_operation_plot(self, japanese_sample_collection):
        """operations.core.plot を使用した日本語表示テスト"""
        from src.tascpy.operations.core.plot import plot

        # 日本語カラム名を使用したプロット
        result = plot(
            japanese_sample_collection,
            "変位",
            "荷重",
            plot_type="scatter",
        )

        # 図を保存
        output_path = Path(self.temp_dir) / "japanese_operation_plot.png"
        plt.savefig(output_path)
        plt.close()

        # ファイルが作成され、サイズが0より大きいことを確認
        assert output_path.exists()
        assert output_path.stat().st_size > 0

        # 戻り値がオリジナルのコレクションであることを確認
        assert result is japanese_sample_collection

    def test_japanese_text_in_figure(self, japanese_sample_collection):
        """図の中に日本語テキストを追加するテスト"""
        fig, ax = plt.subplots(figsize=(8, 6))

        # データのプロット
        ax.plot(
            japanese_sample_collection["変位"].values,
            japanese_sample_collection["荷重"].values,
        )

        # 日本語テキストを図に追加
        ax.text(2, 25, "テキスト注釈", fontsize=12)

        # 日本語を含むテキストボックスの追加
        textbox_props = dict(boxstyle="round", facecolor="wheat", alpha=0.5)
        ax.text(
            0.05,
            0.95,
            "情報ボックス:\n変位と荷重の関係を示すグラフ\n最大荷重: 50kN",
            transform=ax.transAxes,
            fontsize=10,
            verticalalignment="top",
            bbox=textbox_props,
        )

        # グラフを保存
        output_path = Path(self.temp_dir) / "japanese_text_in_figure.png"
        fig.savefig(output_path)
        plt.close(fig)

        # ファイルが作成され、サイズが0より大きいことを確認
        assert output_path.exists()
        assert output_path.stat().st_size > 0

    def test_japanese_axis_ticks(self, japanese_sample_collection):
        """日本語の目盛りラベルテスト"""
        fig, ax = plt.subplots(figsize=(8, 6))

        # データのプロット
        ax.plot(
            japanese_sample_collection["温度"].values,
            japanese_sample_collection["荷重"].values,
        )

        # 目盛りのカスタマイズ
        x_ticks = japanese_sample_collection["温度"].values
        x_labels = [f"測定点{i+1}: {v}℃" for i, v in enumerate(x_ticks)]

        y_ticks = japanese_sample_collection["荷重"].values
        y_labels = [f"{v}kN" for v in y_ticks]

        ax.set_xticks(x_ticks)
        ax.set_xticklabels(x_labels, rotation=45)
        ax.set_yticks(y_ticks)
        ax.set_yticklabels(y_labels)

        # タイトルと軸ラベル
        ax.set_title("温度と荷重の関係")
        ax.set_xlabel("温度")
        ax.set_ylabel("荷重")

        # グラフを保存
        output_path = Path(self.temp_dir) / "japanese_axis_ticks.png"
        fig.tight_layout()  # ラベルが切れないように調整
        fig.savefig(output_path)
        plt.close(fig)

        # ファイルが作成され、サイズが0より大きいことを確認
        assert output_path.exists()
        assert output_path.stat().st_size > 0


def test_visual_inspection_japanese():
    """手動視覚確認用のテスト（CIではスキップ）

    このテストはCIでは自動的にスキップされ、開発時の手動確認用です。
    """
    # CI環境変数が設定されている場合はスキップ
    if "CI" in os.environ:
        pytest.skip("CI環境では視覚確認テストをスキップ")

    # サンプルデータ作成
    sample = ColumnCollection(
        step=list(range(1, 11)),
        columns={
            "変位": Column("1", "変位", "mm", np.linspace(0, 10, 10)),
            "荷重": Column(
                "2", "荷重", "kN", np.sin(np.linspace(0, 2 * np.pi, 10)) * 50 + 50
            ),
        },
    )

    # 日本語プロットの表示
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(sample["変位"].values, sample["荷重"].values, "ro-")
    ax.set_title("日本語フォントテスト: 変位-荷重グラフ")
    ax.set_xlabel("変位 (mm)")
    ax.set_ylabel("荷重 (kN)")
    ax.grid(True)

    # テキストボックスの追加
    textbox_props = dict(boxstyle="round", facecolor="lightblue", alpha=0.5)
    ax.text(
        0.05,
        0.95,
        "日本語テキストボックス\n複数行の日本語テキスト\n特殊文字: ±×÷°℃",
        transform=ax.transAxes,
        fontsize=12,
        verticalalignment="top",
        bbox=textbox_props,
    )

    plt.show()  # 手動実行時のみ表示される
