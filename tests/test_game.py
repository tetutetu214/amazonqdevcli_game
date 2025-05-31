import unittest
import sys
import os
import pygame
from unittest.mock import MagicMock, patch

# テスト対象のモジュールをインポートするためにパスを追加
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.game import Game
from src.board import Board

class TestGame(unittest.TestCase):
    """ゲームクラスのテスト"""
    
    def setUp(self):
        """各テストの前に実行される"""
        # pygameの初期化をモック化
        self.pygame_init_patcher = patch('pygame.init')
        self.pygame_init_mock = self.pygame_init_patcher.start()
        
        # pygameのdisplay.set_modeをモック化
        self.set_mode_patcher = patch('pygame.display.set_mode')
        self.set_mode_mock = self.set_mode_patcher.start()
        self.set_mode_mock.return_value = MagicMock()
        
        # pygameのdisplay.set_captionをモック化
        self.set_caption_patcher = patch('pygame.display.set_caption')
        self.set_caption_mock = self.set_caption_patcher.start()
        
        # ゲームオブジェクトの作成
        self.game = Game()
        
        # UIのdraw_methodsをモック化
        self.game.ui.draw_title_screen = MagicMock()
        self.game.ui.draw_game_screen = MagicMock()
        self.game.ui.draw_result_screen = MagicMock()
        self.game.ui.get_board_position = MagicMock()
        self.game.ui.is_start_button_clicked = MagicMock()
        self.game.ui.is_pass_button_clicked = MagicMock()
        self.game.ui.is_resign_button_clicked = MagicMock()
        self.game.ui.is_play_again_button_clicked = MagicMock()
        self.game.ui.is_back_to_title_button_clicked = MagicMock()
        self.game.ui.show_invalid_move_guide = MagicMock()
    
    def tearDown(self):
        """各テストの後に実行される"""
        self.pygame_init_patcher.stop()
        self.set_mode_patcher.stop()
        self.set_caption_patcher.stop()
    
    def test_init(self):
        """初期化のテスト"""
        self.assertEqual(self.game.state, Game.STATE_TITLE)
        self.assertTrue(self.game.player_turn)
        self.assertEqual(self.game.consecutive_passes, 0)
        self.assertFalse(self.game.ai_thinking)
    
    def test_handle_title_event(self):
        """タイトル画面のイベント処理テスト"""
        # スタートボタンがクリックされた場合
        event = MagicMock()
        event.type = pygame.MOUSEBUTTONDOWN
        event.pos = (100, 100)
        
        self.game.ui.is_start_button_clicked.return_value = True
        
        self.game.handle_title_event(event)
        
        # ゲーム画面に遷移することを確認
        self.assertEqual(self.game.state, Game.STATE_GAME)
    
    def test_handle_game_event_place_stone(self):
        """ゲーム画面での石配置イベント処理テスト"""
        # 有効な手の場合
        event = MagicMock()
        event.type = pygame.MOUSEBUTTONDOWN
        event.pos = (100, 100)
        
        self.game.ui.get_board_position.return_value = (3, 3)
        self.game.board.is_valid_move = MagicMock(return_value=True)
        self.game.board.place_stone = MagicMock(return_value=True)
        
        self.game.handle_game_event(event)
        
        # 石が置かれたことを確認
        self.game.board.place_stone.assert_called_once_with(3, 3, Board.BLACK)
        self.assertFalse(self.game.player_turn)
        self.assertTrue(self.game.ai_thinking)
        
        # 無効な手の場合
        self.game.player_turn = True
        self.game.ai_thinking = False
        self.game.board.is_valid_move.return_value = False
        
        self.game.handle_game_event(event)
        
        # 禁手ガイドが表示されることを確認
        self.game.ui.show_invalid_move_guide.assert_called_once_with(3, 3)
    
    def test_handle_game_event_pass(self):
        """ゲーム画面でのパスイベント処理テスト"""
        # パスボタンがクリックされた場合
        event = MagicMock()
        event.type = pygame.MOUSEBUTTONDOWN
        event.pos = (100, 100)
        
        self.game.ui.get_board_position.return_value = None
        self.game.ui.is_pass_button_clicked.return_value = True
        
        self.game.handle_game_event(event)
        
        # パスが処理されることを確認
        self.assertEqual(self.game.consecutive_passes, 1)
        self.assertFalse(self.game.player_turn)
        self.assertTrue(self.game.ai_thinking)
    
    def test_handle_game_event_resign(self):
        """ゲーム画面での投了イベント処理テスト"""
        # 投了ボタンがクリックされた場合
        event = MagicMock()
        event.type = pygame.MOUSEBUTTONDOWN
        event.pos = (100, 100)
        
        self.game.ui.get_board_position.return_value = None
        self.game.ui.is_pass_button_clicked.return_value = False
        self.game.ui.is_resign_button_clicked.return_value = True
        
        self.game.handle_game_event(event)
        
        # 結果画面に遷移することを確認
        self.assertEqual(self.game.state, Game.STATE_RESULT)
        self.assertEqual(self.game.board.winner, Board.WHITE)
    
    def test_handle_result_event(self):
        """結果画面のイベント処理テスト"""
        # もう一度プレイボタンがクリックされた場合
        event = MagicMock()
        event.type = pygame.MOUSEBUTTONDOWN
        event.pos = (100, 100)
        
        self.game.ui.is_play_again_button_clicked.return_value = True
        
        self.game.handle_result_event(event)
        
        # ゲーム画面に遷移することを確認
        self.assertEqual(self.game.state, Game.STATE_GAME)
        
        # タイトルに戻るボタンがクリックされた場合
        self.game.ui.is_play_again_button_clicked.return_value = False
        self.game.ui.is_back_to_title_button_clicked.return_value = True
        
        self.game.handle_result_event(event)
        
        # タイトル画面に遷移することを確認
        self.assertEqual(self.game.state, Game.STATE_TITLE)
    
    def test_ai_move(self):
        """AIの手の処理テスト"""
        # AIが手を打つ場合
        self.game.ai.get_move = MagicMock(return_value=(3, 3))
        self.game.board.place_stone = MagicMock()
        
        self.game.ai_move()
        
        # 石が置かれることを確認
        self.game.board.place_stone.assert_called_once_with(3, 3, Board.WHITE)
        self.assertTrue(self.game.player_turn)
        self.assertEqual(self.game.consecutive_passes, 0)
        
        # AIがパスする場合
        self.game.ai.get_move.return_value = None
        self.game.player_turn = False
        self.game.consecutive_passes = 0
        
        self.game.ai_move()
        
        # パスが処理されることを確認
        self.assertTrue(self.game.player_turn)
        self.assertEqual(self.game.consecutive_passes, 1)
    
    def test_check_game_end(self):
        """ゲーム終了条件のチェックテスト"""
        # 連続パスでゲーム終了
        self.game.consecutive_passes = 2
        self.game.board.calculate_score = MagicMock()
        self.game.board.calculate_score.side_effect = [10, 5]  # 黒が勝つ
        
        self.game.check_game_end()
        
        # 結果画面に遷移することを確認
        self.assertEqual(self.game.state, Game.STATE_RESULT)
        self.assertEqual(self.game.board.winner, Board.BLACK)
        
        # 白が勝つ場合
        self.game.state = Game.STATE_GAME
        self.game.board.calculate_score.side_effect = [5, 10]  # 白が勝つ（コミ込み）
        
        self.game.check_game_end()
        
        # 結果画面に遷移することを確認
        self.assertEqual(self.game.state, Game.STATE_RESULT)
        self.assertEqual(self.game.board.winner, Board.WHITE)
    
    def test_reset_game(self):
        """ゲームリセットのテスト"""
        # 状態を変更
        self.game.board.place_stone(3, 3, Board.BLACK)
        self.game.player_turn = False
        self.game.consecutive_passes = 1
        self.game.ai_thinking = True
        
        # リセット
        self.game.reset_game()
        
        # 状態がリセットされることを確認
        self.assertTrue(self.game.player_turn)
        self.assertEqual(self.game.consecutive_passes, 0)
        self.assertFalse(self.game.ai_thinking)

if __name__ == '__main__':
    unittest.main()
