# 開発メモ

tascpy は個人で開発・保守しているライブラリです。このファイルは開発時の規約と手順をまとめた覚え書きです。

不具合に気づいた場合は GitHub Issue で知らせていただければ確認しますが、対応や返信の時期はお約束できません。

## 開発環境のセットアップ

```bash
git clone https://github.com/toruinaba/tascpy.git
cd tascpy
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e . -r requirements-dev.txt
```

## 確認コマンド

CI（`.github/workflows/tests.yml`）と同じ検査です。変更後はすべて通ることを確認します。

```bash
MPLBACKEND=Agg pytest -q   # テスト
pyright                    # 型検査
lint-imports               # numeric / core / domains の依存方向の検査
PYTHONPATH=src mkdocs build --strict   # ドキュメントのビルド
```

## コーディング規約

### 基本スタイル
- PEP 8 に準拠
- 行の長さは 88 文字を目安にする
- インデントは 4 スペース

### 命名規則
- クラス名: パスカルケース (`DomainCollectionFactory`)
- 関数/メソッド/変数名: スネークケース (`create_column_collection`, `result_column`)
- プライベートメンバー: アンダースコア接頭辞 (`_factories`)
- 定数: 大文字のスネークケース (`MAX_VALUE`)
- ファイル名: スネークケース (`factory.py`, `collection.py`)
- 変数名は英語のみ使用（日本語不可）

### 型ヒント
- 全ての関数とメソッドには型ヒントを付ける
- 複雑な型は `typing` モジュールを活用
- 戻り値の型も必ず指定

```python
from typing import Dict, Optional, Any

def function(param1: str, param2: Optional[int] = None) -> Dict[str, Any]:
    ...
```

### docstring スタイル
- Google スタイルを採用
- docstring は日本語で記述
- 敬語は「です・ます」調を使用

## ブランチとコミット

- 作業ごとにブランチを切り（`feature/...`、`fix/...`、`docs/...` など）、PR 経由で `master` にマージする
- コミットメッセージは `fix:`、`docs:`、`ci:` などの接頭辞を付ける

## リリース手順

1. `src/tascpy/__init__.py` の `__version__` を更新する（セマンティックバージョニング。`setup.py` はここから読む）
2. README のバージョンバッジを更新し、PR で `master` にマージする
3. `master` でタグを打って push する：
   ```bash
   git tag v0.7.1
   git push origin v0.7.1
   ```
4. `.github/workflows/release.yml` がビルド・検査し、タグと `__version__` が一致すれば PyPI に公開する
