# GOGO囲碁 要件定義書

## 1. プロジェクト概要

GOGO囲碁は、囲碁初心者が陣地の概念を視覚的に理解しながら楽しく学べるゲームアプリケーションです。石を置くと自分の陣地が色分けされ、どこが良い手かが一目で分かる機能を提供します。

## 2. 機能要件

### 2.1 基本機能

- **9×9の囲碁盤**: 初心者向けの小さな盤面を提供
- **対局機能**: プレイヤー（黒石）とAI（白石）の対戦
- **石の配置**: クリックで石を置く
- **パス機能**: 手番をスキップする
- **投了機能**: ゲームを途中で終了する（投了した側の負け）
- **連続パス終了**: 連続2回のパスでゲーム終了
- **勝敗判定**: 陣地と取った石の数で勝敗を決定（コミ3.5目）

### 2.2 視覚化機能

- **陣地の可視化**: 確定陣地を色分けして表示
- **影響圏の表示**: 石の影響が及ぶ範囲を色分けして表示
- **プレビュー機能**: 石を置く前に結果をプレビュー表示
- **最後の手のマーク**: 直前に打たれた手を強調表示
- **優勢表示**: 現在の盤面での優勢状況をバーグラフで表示

### 2.3 AI機能

- **囲碁検定5級レベル**: 初心者向けの適切な強さのAI
- **思考時間の演出**: AIの思考中を表示（0.5秒）
- **パス判断**: 有効な手がない場合にのみパスする機能

### 2.4 UI/UX

- **和風デザイン**: 伝統的な囲碁のイメージに合ったデザイン
- **ポップアップメッセージ**: 重要な情報を通知（パス、連続パス終了など）
- **結果画面**: ゲーム終了時に詳細な結果を表示
- **リプレイ機能**: 同じ設定で再度対局できる機能
- **タイトル画面**: ゲーム開始時のタイトル画面

## 3. 非機能要件

### 3.1 パフォーマンス

- **応答性**: クリックからの石の配置は0.1秒以内
- **AI思考時間**: 1手あたり最大2秒以内（演出含む）
- **画面更新**: 60FPSでの滑らかな描画

### 3.2 互換性

- **対応OS**: Windows, macOS, Linux
- **Python要件**: Python 3.8以上
- **必要ライブラリ**: pygame 2.0.0以上, numpy 1.19以上

### 3.3 保守性

- **モジュール分割**: 機能ごとに適切に分割されたコード構造
  - board.py: 盤面と石の配置ロジック
  - ai.py: AI対戦ロジック
  - ui.py: ユーザーインターフェース
  - game.py: ゲームの状態管理
  - life_death.py: 石の生死判定ロジック
- **コメント**: 主要な関数とクラスには適切なドキュメントコメント
- **テストコード**: 主要機能のユニットテスト

## 4. 制約条件

- **言語**: Python
- **ライセンス**: MITライセンス
- **開発期間**: 2025年5月31日までに完成

## 5. 開発プロセス

### 5.1 開発手法

- **テスト駆動開発 (TDD)**: 機能実装前にテストを作成
- **継続的テスト**: 変更後は必ずすべてのテストを実行
- **コードレビュー**: 重要な機能実装後にレビューを実施
- **実機テスト**: 実際のゲームプレイでの動作確認を必ず実施

### 5.2 品質保証

- **単体テスト**: 各モジュールの機能テスト
- **結合テスト**: モジュール間の連携テスト
- **ユーザーテスト**: 実際のプレイ体験のテスト
- **エッジケーステスト**: 連続パスや投了などの特殊ケースのテスト

### 5.3 開発ルール

- **コーディング規約**: PEP 8に準拠
- **バージョン管理**: Gitを使用
- **修正プロセス**: 
  1. 修正内容の計画
  2. 必要に応じてテストの作成・更新
  3. 修正の実装
  4. すべてのテストの実行と確認
  5. 実機での動作確認
  6. コードレビュー
  7. マージ

## 6. 将来の拡張性

- **盤面サイズの選択**: 13×13や19×19の盤面サイズの追加
- **対局記録**: 棋譜の保存と読み込み
- **AIレベル調整**: 複数の難易度から選択可能に
- **オンライン対戦**: 他のプレイヤーとの対戦機能
- **チュートリアル**: 初心者向けの囲碁ルール解説

## 7. リスク管理

- **技術的リスク**: AIの思考ロジックの複雑さ
- **スケジュールリスク**: UI実装の遅延可能性
- **品質リスク**: バグの発生と対応時間
- **特殊ケースリスク**: 連続パスや特殊な盤面状況での不具合

## 8. 成功基準

- すべての機能要件の実装完了
- すべてのテストが通過
- 初心者ユーザーが直感的に操作できること
- 囲碁の基本概念が視覚的に理解できること
- 連続パスによるゲーム終了が正しく機能すること
- 優勢表示が盤面状況を適切に反映すること
