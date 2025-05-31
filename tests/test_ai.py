import unittest
import sys
import os
import numpy as np

# テスト対象のモジュールをインポートするためにパスを追加
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.board import Board
from src.ai import AI

class TestAI(unittest.TestCase):
    """AIクラスのテスト"""
    
    def setUp(self):
        """各テストの前に実行される"""
        self.board = Board(size=9)
        self.ai = AI(self.board)
    
    def test_init(self):
        """初期化のテスト"""
        self.assertEqual(self.ai.board, self.board)
    
    def test_get_move(self):
        """次の一手の決定テスト"""
        # 空の盤面での手
        move = self.ai.get_move()
        
        # 有効な手が返されることを確認
        self.assertIsNotNone(move)
        x, y = move
        self.assertTrue(0 <= x < self.board.size)
        self.assertTrue(0 <= y < self.board.size)
        
        # 石を置いていく
        for i in range(20):
            move = self.ai.get_move()
            if move is None:  # パスの場合
                break
            x, y = move
            self.board.place_stone(x, y, Board.WHITE)
            
            # プレイヤーの手も置く
            for j in range(self.board.size):
                for k in range(self.board.size):
                    if self.board.is_valid_move(j, k):
                        self.board.place_stone(j, k, Board.BLACK)
                        break
                else:
                    continue
                break
        
        # 最後まで有効な手が返されることを確認
        self.assertTrue(True)  # ここまで例外なく到達できれば成功
    
    def test_evaluate_move(self):
        """手の評価テスト"""
        # 空の盤面での評価
        score = self.ai.evaluate_move((4, 4))  # 天元
        
        # 評価値が返されることを確認
        self.assertIsInstance(score, float)
        
        # 天元は高評価であることを確認
        corner_score = self.ai.evaluate_move((0, 0))  # 隅
        self.assertGreater(score, corner_score)
        
        # アタリを取る手の評価
        self.board.place_stone(1, 1, Board.BLACK)
        self.board.place_stone(0, 1, Board.WHITE)
        self.board.place_stone(1, 0, Board.WHITE)
        self.board.place_stone(2, 1, Board.WHITE)
        
        atari_score = self.ai.evaluate_move((1, 2))  # アタリを完成させる手
        normal_score = self.ai.evaluate_move((3, 3))  # 普通の手
        
        # アタリを取る手が高評価であることを確認
        self.assertGreater(atari_score, normal_score)
    
    def test_count_potential_captures(self):
        """取れる石の数の計算テスト"""
        # アタリの状況を作る
        self.board.place_stone(1, 1, Board.BLACK)
        self.board.place_stone(0, 1, Board.WHITE)
        self.board.place_stone(1, 0, Board.WHITE)
        self.board.place_stone(2, 1, Board.WHITE)
        
        # 取れる石の数を確認
        captures = self.ai.count_potential_captures(1, 2)
        self.assertEqual(captures, 1)
        
        # 複数の石を取れる状況
        self.board.place_stone(3, 3, Board.BLACK)
        self.board.place_stone(3, 4, Board.BLACK)
        self.board.place_stone(2, 3, Board.WHITE)
        self.board.place_stone(2, 4, Board.WHITE)
        self.board.place_stone(3, 2, Board.WHITE)
        self.board.place_stone(3, 5, Board.WHITE)
        self.board.place_stone(4, 3, Board.WHITE)
        
        # 取れる石の数を確認
        captures = self.ai.count_potential_captures(4, 4)
        self.assertEqual(captures, 2)
    
    def test_is_self_atari(self):
        """自分の石がアタリになるかのテスト"""
        # アタリになる状況を作る
        self.board.place_stone(1, 0, Board.BLACK)
        self.board.place_stone(0, 1, Board.BLACK)
        self.board.place_stone(2, 1, Board.BLACK)
        
        # アタリになることを確認
        self.assertTrue(self.ai.is_self_atari(1, 1))
        
        # アタリにならない状況
        self.assertFalse(self.ai.is_self_atari(3, 3))
    
    def test_calculate_influence_gain(self):
        """影響圏の増加量の計算テスト"""
        # 石を置く
        self.board.place_stone(4, 4, Board.WHITE)
        
        # 影響圏の増加量を確認
        gain1 = self.ai.calculate_influence_gain(2, 2)
        gain2 = self.ai.calculate_influence_gain(6, 6)
        
        # 両方とも正の値であることを確認
        self.assertGreaterEqual(gain1, 0)
        self.assertGreaterEqual(gain2, 0)
    
    def test_calculate_invasion_value(self):
        """相手の陣地侵略価値の計算テスト"""
        # 黒の影響圏を作る
        self.board.place_stone(4, 4, Board.BLACK)
        self.board.update_territories()
        
        # 侵略価値を確認
        value1 = self.ai.calculate_invasion_value(3, 3)  # 黒の影響圏内
        value2 = self.ai.calculate_invasion_value(0, 0)  # 黒の影響圏外
        
        # 影響圏内の方が高評価であることを確認
        self.assertGreater(value1, value2)
    
    def test_evaluate_position(self):
        """位置の基本評価値の計算テスト"""
        # 各位置の評価値を確認
        center_value = self.ai.evaluate_position(4, 4)  # 天元
        corner_value = self.ai.evaluate_position(0, 0)  # 隅
        side_value = self.ai.evaluate_position(0, 4)    # 辺
        
        # 天元 > 辺 > 隅 の順に評価が高いことを確認
        self.assertGreater(center_value, side_value)
        self.assertGreater(side_value, corner_value)

if __name__ == '__main__':
    unittest.main()
