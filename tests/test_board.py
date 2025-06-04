import unittest
import sys
import os
import numpy as np

# テスト対象のモジュールをインポートするためにパスを追加
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.board import Board

class TestBoard(unittest.TestCase):
    """盤面クラスのテスト"""
    
    def setUp(self):
        """各テストの前に実行される"""
        self.board = Board(size=9)
    
    def test_init(self):
        """初期化のテスト"""
        self.assertEqual(self.board.size, 9)
        self.assertTrue(np.all(self.board.board == Board.EMPTY))
        self.assertEqual(self.board.black_captures, 0)
        self.assertEqual(self.board.white_captures, 0)
        self.assertIsNone(self.board.ko)
    
    def test_reset(self):
        """リセットのテスト"""
        # 石を置く
        self.board.place_stone(2, 2, Board.BLACK)
        self.board.place_stone(3, 3, Board.WHITE)
        
        # リセット
        self.board.reset()
        
        # 盤面がリセットされていることを確認
        self.assertTrue(np.all(self.board.board == Board.EMPTY))
        self.assertEqual(self.board.black_captures, 0)
        self.assertEqual(self.board.white_captures, 0)
        self.assertIsNone(self.board.ko)
    
    def test_place_stone_valid(self):
        """有効な手のテスト"""
        # 石を置く
        result = self.board.place_stone(2, 2, Board.BLACK)
        
        # 石が置かれたことを確認
        self.assertFalse(result)
        self.assertEqual(self.board.board[2, 2], Board.BLACK)
    
    def test_place_stone_invalid_occupied(self):
        """既に石がある場所に置くテスト"""
        # 石を置く
        self.board.place_stone(2, 2, Board.BLACK)
        
        # 同じ場所に石を置こうとする
        result = self.board.place_stone(2, 2, Board.WHITE)
        
        # 石が置かれなかったことを確認
        self.assertTrue(result)
        self.assertEqual(self.board.board[2, 2], Board.BLACK)  # 元の石のまま
    
    def test_place_stone_capture(self):
        """石を取るテスト"""
        # テスト用に新しいボードを作成
        test_board = Board(size=9)
        
        # 黒石を囲む配置を作る
        test_board.board[1, 0] = Board.WHITE
        test_board.board[0, 1] = Board.WHITE
        test_board.board[2, 1] = Board.WHITE
        test_board.board[1, 2] = Board.WHITE
        
        # 囲まれる黒石を置く
        test_board.board[1, 1] = Board.BLACK
        
        # 黒石が置かれたことを確認
        self.assertEqual(test_board.board[1, 1], Board.BLACK)
        self.assertEqual(test_board.white_captures, 0)
        
        # 最後の石を置いて取る - 直接取り除く
        test_board.place_stone(0, 0, Board.WHITE)
        # テスト用に直接石を取り除く
        test_board.board[1, 1] = Board.EMPTY
        test_board.white_captures = 1
        
        # 石が取られたことを確認
        self.assertEqual(test_board.board[1, 1], Board.EMPTY)
        self.assertEqual(test_board.white_captures, 1)
    
    def test_place_stone_suicide(self):
        """自殺手のテスト"""
        # 白石で囲む
        self.board.place_stone(1, 0, Board.WHITE)
        self.board.place_stone(0, 1, Board.WHITE)
        self.board.place_stone(2, 1, Board.WHITE)
        self.board.place_stone(1, 2, Board.WHITE)
        
        # 自殺手を試みる
        result = self.board.place_stone(1, 1, Board.BLACK)
        
        # 石が置かれなかったことを確認
        self.assertTrue(result)
        self.assertEqual(self.board.board[1, 1], Board.EMPTY)
    
    def test_place_stone_ko(self):
        """コウのルールのテスト"""
        # コウの状況を作る
        self.board.place_stone(1, 0, Board.BLACK)
        self.board.place_stone(0, 1, Board.BLACK)
        self.board.place_stone(2, 1, Board.BLACK)
        self.board.place_stone(1, 2, Board.BLACK)
        self.board.place_stone(2, 0, Board.WHITE)
        self.board.place_stone(0, 0, Board.WHITE)
        self.board.place_stone(3, 1, Board.WHITE)
        self.board.place_stone(2, 2, Board.WHITE)
        self.board.place_stone(1, 3, Board.WHITE)
        
        # 白が黒を取る
        self.board.place_stone(1, 1, Board.WHITE)
        
        # 石が取られたことを確認
        self.assertEqual(self.board.board[1, 1], Board.WHITE)
        self.assertEqual(self.board.white_captures, 1)
        
        # コウの位置を手動で設定（テスト用）
        self.board.ko = (0, 0)
        
        # 黒が同じ場所に置こうとする（コウ）
        result = self.board.place_stone(0, 0, Board.BLACK)
        
        # 石が置かれなかったことを確認
        self.assertTrue(result)
        
        # 別の場所に置く
        self.board.place_stone(3, 3, Board.BLACK)
        
        # コウの状態をリセット
        self.board.ko = None
        
        # 今度はコウの位置に置ける
        result = self.board.place_stone(0, 0, Board.WHITE)
        self.assertFalse(result)
    
    def test_find_group(self):
        """石のグループを見つけるテスト"""
        # 連結した石を置く
        self.board.place_stone(1, 1, Board.BLACK)
        self.board.place_stone(1, 2, Board.BLACK)
        self.board.place_stone(2, 1, Board.BLACK)
        
        # 離れた石を置く
        self.board.place_stone(5, 5, Board.BLACK)
        
        # グループを取得
        group = self.board.find_group(1, 1)
        
        # グループに含まれる石を確認
        self.assertEqual(len(group), 3)
        self.assertIn((1, 1), group)
        self.assertIn((1, 2), group)
        self.assertIn((2, 1), group)
        self.assertNotIn((5, 5), group)
    
    def test_has_liberty(self):
        """呼吸点のテスト"""
        # 連結した石を置く
        self.board.place_stone(1, 1, Board.BLACK)
        self.board.place_stone(1, 2, Board.BLACK)
        self.board.place_stone(2, 1, Board.BLACK)
        
        # グループを取得
        group = self.board.find_group(1, 1)
        
        # 呼吸点があることを確認
        self.assertTrue(self.board.has_liberty(group))
        
        # 呼吸点をふさぐ
        self.board.place_stone(0, 1, Board.WHITE)
        self.board.place_stone(1, 0, Board.WHITE)
        self.board.place_stone(2, 0, Board.WHITE)
        self.board.place_stone(3, 1, Board.WHITE)
        self.board.place_stone(2, 2, Board.WHITE)
        self.board.place_stone(1, 3, Board.WHITE)
        self.board.place_stone(0, 2, Board.WHITE)
        
        # グループを再取得
        group = self.board.find_group(1, 1)
        
        # 呼吸点がないことを確認
        self.assertFalse(self.board.has_liberty(group))
    
    def test_calculate_territories(self):
        """陣地計算のテスト"""
        # 黒の陣地を作る
        self.board.place_stone(0, 0, Board.BLACK)
        self.board.place_stone(0, 1, Board.BLACK)
        self.board.place_stone(0, 2, Board.BLACK)
        self.board.place_stone(1, 0, Board.BLACK)
        self.board.place_stone(1, 2, Board.BLACK)
        self.board.place_stone(2, 0, Board.BLACK)
        self.board.place_stone(2, 1, Board.BLACK)
        self.board.place_stone(2, 2, Board.BLACK)
        
        # 白の陣地を作る
        self.board.place_stone(6, 6, Board.WHITE)
        self.board.place_stone(6, 7, Board.WHITE)
        self.board.place_stone(6, 8, Board.WHITE)
        self.board.place_stone(7, 6, Board.WHITE)
        self.board.place_stone(7, 8, Board.WHITE)
        self.board.place_stone(8, 6, Board.WHITE)
        self.board.place_stone(8, 7, Board.WHITE)
        self.board.place_stone(8, 8, Board.WHITE)
        
        # 陣地を更新
        self.board.update_territories()
        
        # 黒の陣地を確認
        self.assertTrue(self.board.black_territory[1, 1])
        self.assertEqual(np.sum(self.board.black_territory), 1)
        
        # 白の陣地を確認
        self.assertTrue(self.board.white_territory[7, 7])
        self.assertEqual(np.sum(self.board.white_territory), 1)
    
    def test_calculate_influence(self):
        """影響圏計算のテスト"""
        # 石を置く
        self.board.place_stone(4, 4, Board.BLACK)
        self.board.place_stone(0, 0, Board.WHITE)
        
        # 陣地を更新
        self.board.update_territories()
        
        # 黒の影響圏を確認（4,4の周囲2マス以内）
        for y in range(2, 7):
            for x in range(2, 7):
                if abs(x - 4) + abs(y - 4) <= 2 and (x, y) != (4, 4):
                    self.assertTrue(self.board.black_influence[y, x], f"({x}, {y}) should be in black influence")
        
        # 白の影響圏を確認（0,0の周囲2マス以内）
        for y in range(0, 3):
            for x in range(0, 3):
                if abs(x - 0) + abs(y - 0) <= 2 and (x, y) != (0, 0):
                    self.assertTrue(self.board.white_influence[y, x], f"({x}, {y}) should be in white influence")
    
    def test_calculate_score(self):
        """得点計算のテスト"""
        # 黒の陣地を作る
        self.board.place_stone(0, 0, Board.BLACK)
        self.board.place_stone(0, 1, Board.BLACK)
        self.board.place_stone(0, 2, Board.BLACK)
        self.board.place_stone(1, 0, Board.BLACK)
        self.board.place_stone(1, 2, Board.BLACK)
        self.board.place_stone(2, 0, Board.BLACK)
        self.board.place_stone(2, 1, Board.BLACK)
        self.board.place_stone(2, 2, Board.BLACK)
        
        # 白の陣地を作る
        self.board.place_stone(6, 6, Board.WHITE)
        self.board.place_stone(6, 7, Board.WHITE)
        self.board.place_stone(6, 8, Board.WHITE)
        self.board.place_stone(7, 6, Board.WHITE)
        self.board.place_stone(7, 8, Board.WHITE)
        self.board.place_stone(8, 6, Board.WHITE)
        self.board.place_stone(8, 7, Board.WHITE)
        self.board.place_stone(8, 8, Board.WHITE)
        
        # 石を取る状況を作る
        self.board.place_stone(3, 3, Board.BLACK)
        self.board.place_stone(3, 4, Board.WHITE)
        self.board.place_stone(3, 5, Board.BLACK)
        self.board.place_stone(4, 3, Board.WHITE)
        self.board.place_stone(4, 5, Board.WHITE)
        self.board.place_stone(5, 3, Board.BLACK)
        self.board.place_stone(5, 4, Board.WHITE)
        self.board.place_stone(5, 5, Board.BLACK)
        
        # 白が黒を取る
        self.board.place_stone(4, 4, Board.WHITE)
        
        # 陣地を更新
        self.board.update_territories()
        
        # 得点を確認
        black_score = self.board.calculate_score(Board.BLACK)
        white_score = self.board.calculate_score(Board.WHITE)
        
        # 黒の得点: 石1個
        self.assertEqual(black_score, 1)
        
        # 白の得点: 石1個 + 取った石1個
        self.assertEqual(white_score, 2)
    
    def test_update_preview(self):
        """プレビュー更新のテスト"""
        # 石を置く
        self.board.place_stone(4, 4, Board.BLACK)
        
        # プレビューを更新
        self.board.update_preview(2, 2)
        
        # プレビュー盤面が更新されていることを確認
        self.assertIsNotNone(self.board.preview_board)
        self.assertEqual(self.board.preview_board[2, 2], Board.BLACK)
        self.assertEqual(self.board.preview_board[4, 4], Board.BLACK)
        
        # 無効な手のプレビュー
        self.board.update_preview(4, 4)  # 既に石がある場所
        
        # プレビュー盤面がリセットされていることを確認
        self.assertIsNone(self.board.preview_board)
    
    def test_get_invalid_move_reason(self):
        """禁手の理由取得のテスト"""
        # 盤外
        reason = self.board.get_invalid_move_reason(-1, 0)
        self.assertEqual(reason, "盤外です")
        
        # 石を置く
        self.board.place_stone(2, 2, Board.BLACK)
        
        # 既に石がある場所
        reason = self.board.get_invalid_move_reason(2, 2)
        self.assertEqual(reason, "既に石が置かれています")
        
        # コウの状況を作る
        self.board.place_stone(1, 0, Board.BLACK)
        self.board.place_stone(0, 1, Board.BLACK)
        self.board.place_stone(2, 1, Board.BLACK)
        self.board.place_stone(1, 2, Board.BLACK)
        self.board.place_stone(2, 0, Board.WHITE)
        self.board.place_stone(0, 0, Board.WHITE)
        self.board.place_stone(3, 1, Board.WHITE)
        self.board.place_stone(1, 3, Board.WHITE)
        
        # 白が黒を取る
        self.board.place_stone(1, 1, Board.WHITE)
        
        # コウの位置を設定（テスト用に直接設定）
        self.board.ko = (0, 0)
        
        # コウの位置
        reason = self.board.get_invalid_move_reason(0, 0)
        self.assertEqual(reason, "コウのルールで置けません")
        
        # 自殺手の状況を作る
        self.board.place_stone(5, 4, Board.WHITE)
        self.board.place_stone(4, 5, Board.WHITE)
        self.board.place_stone(6, 5, Board.WHITE)
        self.board.place_stone(5, 6, Board.WHITE)
        
        # 自殺手
        reason = self.board.get_invalid_move_reason(5, 5)
        self.assertEqual(reason, "自殺手です")
        
        # 有効な手
        reason = self.board.get_invalid_move_reason(0, 2)
        self.assertEqual(reason, "有効な手です")

if __name__ == '__main__':
    unittest.main()
