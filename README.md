# GOGO 囲碁

GOGO囲碁は、初心者でも陣地の概念を視覚的に理解できる囲碁ゲームです。石を置くと自分の陣地が色分けされ、どこが良い手かが一目で分かります。

![GOGO囲碁](assets/images/screenshot.jpg)

## 特徴

- **陣地の可視化**: 確定陣地と影響圏が色分けされ、囲碁の基本概念を視覚的に理解できます
- **初心者向け**: 9×9の小さな盤面で、囲碁の基本ルールを学びやすい設計
- **AI対戦**: 囲碁検定5級レベルのAIと対戦可能
- **先手プレイ**: プレイヤーは黒石（先手）として対戦します
- **用語集**: 囲碁の基本用語を解説した用語集を搭載

## インストール方法

### 必要条件
- Python 3.8以上
- pygame 2.0.0以上
- numpy 1.19以上

### インストール手順

1. リポジトリをクローン
```bash
git clone https://github.com/tetutetu214/amazonqdevcli_game.git
cd amazonqdevcli_game
```

2. 必要なパッケージをインストール
```bash
pip install -r requirements.txt
```

## 使い方

1. ゲームを起動
```bash
python run.py
```

2. タイトル画面で「ゲーム開始」をクリック

3. ゲーム画面で以下の操作が可能:
   - 盤面をクリックして石を置く
   - 「パス」ボタンでパスする
   - 「投了」ボタンで投了する

## ゲームルール

- 標準的な囲碁のルールに従います
- 9×9の盤面を使用
- コミ: 白に3.5目
- 連続2回のパスでゲーム終了
- 陣地の多い方が勝利

## 開発者向け情報

- `src/board.py`: 盤面と石の配置ロジック
- `src/ai.py`: AI対戦ロジック
- `src/ui.py`: ユーザーインターフェース
- `src/game.py`: ゲームの状態管理
- `src/life_death.py`: 石の生死判定ロジック

### 開発手法

- **テスト駆動開発**: 機能の追加・修正を行う際は、必ず対応するテストを作成または更新してください
- **継続的テスト**: コード変更後は必ず全テストを実行し、すべてのテストが通ることを確認してください
- **リファクタリング**: コードの品質を維持するため、定期的にリファクタリングを行ってください

### テスト実行方法

```bash
# すべてのテストを実行
python -m unittest discover tests

# 特定のテストファイルを実行
python -m unittest tests/test_board.py
```

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 謝辞

- 囲碁のルールとAIロジックの参考資料: [囲碁入門サイト](https://www.nihonkiin.or.jp/learn/school/)
- UIデザインの参考: [和風デザインガイドライン](https://example.com/japanese-design)
