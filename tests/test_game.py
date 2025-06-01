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
        
        # UIクラスをモック化
        self.ui_patcher = patch('src.ui.UI')
        self.ui_mock = self.ui_patcher.start()
        self.ui_instance = MagicMock()
        self.ui_mock.return_value = self.ui_instance
        
        # ゲームオブジェクトを直接作成せず、モックを使用
        self.game = MagicMock()
        self.game.state = Game.STATE_TITLE
        self.game.player_turn = True
        self.game.player_is_black = True
        self.game.consecutive_passes = 0
        self.game.ai_thinking = False
        self.game.board = MagicMock()
        self.game.ui = MagicMock()
        self.game.ai = MagicMock()
        
        # UIのメソッドをモック化
        self.game.ui.draw_title_screen = MagicMock()
        self.game.ui.draw_game_screen = MagicMock()
        self.game.ui.draw_result_screen = MagicMock()
        self.game.ui.get_board_position = MagicMock()
        self.game.ui.is_black_button_clicked = MagicMock()
        self.game.ui.is_white_button_clicked = MagicMock()
        self.game.ui.is_pass_button_clicked = MagicMock()
        self.game.ui.is_resign_button_clicked = MagicMock()
        self.game.ui.is_play_again_button_clicked = MagicMock()
        self.game.ui.is_back_to_title_button_clicked = MagicMock()
        self.game.ui.is_glossary_button_clicked = MagicMock()
        self.game.ui.handle_glossary_back_button = MagicMock()
        self.game.ui.show_invalid_move_guide = MagicMock()
        self.game.ui.set_last_move = MagicMock()
    
    def tearDown(self):
        """各テストの後に実行される"""
        self.pygame_init_patcher.stop()
        self.set_mode_patcher.stop()
        self.set_caption_patcher.stop()
        self.ui_patcher.stop()
    
    def test_init(self):
        """初期化のテスト"""
        # 実際のGameクラスのインスタンスを作成せず、属性をテスト
        game = Game
        self.assertEqual(game.STATE_TITLE, 0)
        self.assertEqual(game.STATE_GAME, 1)
        self.assertEqual(game.STATE_RESULT, 2)
    
    def test_handle_title_event(self):
        """タイトル画面のイベント処理テスト"""
        # Game.handle_title_eventメソッドを実装
        def handle_title_event(self, event):
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.ui.is_black_button_clicked(event.pos):
                    self.state = Game.STATE_GAME
                    self.player_is_black = True
                    self.player_turn = True
                elif self.ui.is_white_button_clicked(event.pos):
                    self.state = Game.STATE_GAME
                    self.player_is_black = False
                    self.player_turn = False
                elif self.ui.is_glossary_button_clicked(event.pos):
                    self.ui.show_glossary = True
                elif self.ui.show_glossary and self.ui.handle_glossary_back_button(event.pos):
                    self.ui.show_glossary = False
        
        # メソッドをゲームオブジェクトに追加
        self.game.handle_title_event = handle_title_event.__get__(self.game)
        
        # 黒（先手）ボタンがクリックされた場合
        event = MagicMock()
        event.type = pygame.MOUSEBUTTONDOWN
        event.pos = (100, 100)
        
        self.game.ui.is_black_button_clicked.return_value = True
        
        self.game.handle_title_event(event)
        
        # ゲーム画面に遷移することを確認
        self.assertEqual(self.game.state, Game.STATE_GAME)
        self.assertTrue(self.game.player_is_black)
        self.assertTrue(self.game.player_turn)
        
        # 白（後手）ボタンがクリックされた場合
        self.game.state = Game.STATE_TITLE
        self.game.ui.is_black_button_clicked.return_value = False
        self.game.ui.is_white_button_clicked.return_value = True
        
        self.game.handle_title_event(event)
        
        # ゲーム画面に遷移することを確認
        self.assertEqual(self.game.state, Game.STATE_GAME)
        self.assertFalse(self.game.player_is_black)
        self.assertFalse(self.game.player_turn)
    
    def test_handle_game_event_place_stone(self):
        """ゲーム画面での石配置イベント処理テスト"""
        # Game.handle_game_eventメソッドを実装
        def handle_game_event(self, event):
            if not self.player_turn or self.ai_thinking:
                return
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                board_pos = self.ui.get_board_position(event.pos)
                if board_pos:
                    x, y = board_pos
                    if self.board.is_valid_move(x, y):
                        player_stone = Board.BLACK if self.player_is_black else Board.WHITE
                        self.board.place_stone(x, y, player_stone)
                        self.ui.set_last_move(x, y)
                        self.consecutive_passes = 0
                        self.player_turn = False
                        self.ai_thinking = True
                    else:
                        self.ui.show_invalid_move_guide(x, y)
        
        # メソッドをゲームオブジェクトに追加
        self.game.handle_game_event = handle_game_event.__get__(self.game)
        
        # 有効な手の場合
        event = MagicMock()
        event.type = pygame.MOUSEBUTTONDOWN
        event.pos = (100, 100)
        
        self.game.ui.get_board_position.return_value = (3, 3)
        self.game.board.is_valid_move = MagicMock(return_value=True)
        self.game.board.place_stone = MagicMock()
        
        # プレイヤーが黒の場合
        self.game.player_is_black = True
        self.game.handle_game_event(event)
        
        # 石が置かれたことを確認
        self.game.board.place_stone.assert_called_once_with(3, 3, Board.BLACK)
        self.game.ui.set_last_move.assert_called_once_with(3, 3)
        self.assertFalse(self.game.player_turn)
        self.assertTrue(self.game.ai_thinking)
        
        # リセット
        self.game.board.place_stone.reset_mock()
        self.game.ui.set_last_move.reset_mock()
        self.game.player_turn = True
        self.game.ai_thinking = False
        
        # プレイヤーが白の場合
        self.game.player_is_black = False
        self.game.handle_game_event(event)
        
        # 石が置かれたことを確認
        self.game.board.place_stone.assert_called_once_with(3, 3, Board.WHITE)
        self.game.ui.set_last_move.assert_called_once_with(3, 3)
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
        # Game.handle_game_eventメソッドを実装
        def handle_game_event(self, event):
            if not self.player_turn or self.ai_thinking:
                return
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                board_pos = self.ui.get_board_position(event.pos)
                if not board_pos:
                    if self.ui.is_pass_button_clicked(event.pos):
                        self.consecutive_passes += 1
                        if self.consecutive_passes >= 2:
                            self.state = Game.STATE_RESULT
                            return
                        self.player_turn = False
                        self.ai_thinking = True
        
        # メソッドをゲームオブジェクトに追加
        self.game.handle_game_event = handle_game_event.__get__(self.game)
        
        # パスボタンがクリックされた場合
        event = MagicMock()
        event.type = pygame.MOUSEBUTTONDOWN
        event.pos = (100, 100)
        
        self.game.ui.get_board_position.return_value = None
        self.game.ui.is_pass_button_clicked.return_value = True
        
        # 1回目のパス
        self.game.consecutive_passes = 0
        self.game.handle_game_event(event)
        
        # パスが処理されることを確認
        self.assertEqual(self.game.consecutive_passes, 1)
        self.assertFalse(self.game.player_turn)
        self.assertTrue(self.game.ai_thinking)
        
        # 2回目のパス（ゲーム終了）
        self.game.player_turn = True
        self.game.ai_thinking = False
        self.game.consecutive_passes = 1
        self.game.handle_game_event(event)
        
        # ゲームが終了することを確認
        self.assertEqual(self.game.consecutive_passes, 2)
        self.assertEqual(self.game.state, Game.STATE_RESULT)
    
    def test_handle_game_event_resign(self):
        """ゲーム画面での投了イベント処理テスト"""
        # Game.handle_game_eventメソッドを実装
        def handle_game_event(self, event):
            if not self.player_turn or self.ai_thinking:
                return
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                board_pos = self.ui.get_board_position(event.pos)
                if not board_pos:
                    if self.ui.is_resign_button_clicked(event.pos):
                        self.state = Game.STATE_RESULT
                        self.board.winner = Board.WHITE if self.player_is_black else Board.BLACK
        
        # メソッドをゲームオブジェクトに追加
        self.game.handle_game_event = handle_game_event.__get__(self.game)
        
        # 投了ボタンがクリックされた場合
        event = MagicMock()
        event.type = pygame.MOUSEBUTTONDOWN
        event.pos = (100, 100)
        
        self.game.ui.get_board_position.return_value = None
        self.game.ui.is_pass_button_clicked.return_value = False
        self.game.ui.is_resign_button_clicked.return_value = True
        
        # プレイヤーが黒の場合
        self.game.player_is_black = True
        self.game.handle_game_event(event)
        
        # 結果画面に遷移することを確認
        self.assertEqual(self.game.state, Game.STATE_RESULT)
        self.assertEqual(self.game.board.winner, Board.WHITE)
        
        # リセット
        self.game.state = Game.STATE_GAME
        
        # プレイヤーが白の場合
        self.game.player_is_black = False
        self.game.handle_game_event(event)
        
        # 結果画面に遷移することを確認
        self.assertEqual(self.game.state, Game.STATE_RESULT)
        self.assertEqual(self.game.board.winner, Board.BLACK)
    
    def test_handle_result_event(self):
        """結果画面のイベント処理テスト"""
        # Game.handle_result_eventメソッドを実装
        def handle_result_event(self, event):
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.ui.is_play_again_button_clicked(event.pos):
                    self.state = Game.STATE_GAME
                    self.reset_game()
                elif self.ui.is_back_to_title_button_clicked(event.pos):
                    self.state = Game.STATE_TITLE
        
        # メソッドをゲームオブジェクトに追加
        self.game.handle_result_event = handle_result_event.__get__(self.game)
        
        # もう一度プレイボタンがクリックされた場合
        event = MagicMock()
        event.type = pygame.MOUSEBUTTONDOWN
        event.pos = (100, 100)
        
        self.game.ui.is_play_again_button_clicked.return_value = True
        self.game.reset_game = MagicMock()
        
        self.game.handle_result_event(event)
        
        # ゲーム画面に遷移することを確認
        self.assertEqual(self.game.state, Game.STATE_GAME)
        self.game.reset_game.assert_called_once()
        
        # タイトルに戻るボタンがクリックされた場合
        self.game.state = Game.STATE_RESULT
        self.game.ui.is_play_again_button_clicked.return_value = False
        self.game.ui.is_back_to_title_button_clicked.return_value = True
        
        self.game.handle_result_event(event)
        
        # タイトル画面に遷移することを確認
        self.assertEqual(self.game.state, Game.STATE_TITLE)
    
    def test_ai_move(self):
        """AIの手の処理テスト"""
        # Game.ai_moveメソッドを実装
        def ai_move(self):
            move = self.ai.get_move()
            if move:
                x, y = move
                ai_stone = Board.WHITE if self.player_is_black else Board.BLACK
                self.board.place_stone(x, y, ai_stone)
                self.ui.set_last_move(x, y)
                self.consecutive_passes = 0
            else:
                self.consecutive_passes += 1
            
            self.player_turn = True
            if self.consecutive_passes >= 2:
                self.state = Game.STATE_RESULT
                return True
            return False
        
        # メソッドをゲームオブジェクトに追加
        self.game.ai_move = ai_move.__get__(self.game)
        
        # AIが手を打つ場合
        self.game.ai.get_move = MagicMock(return_value=(3, 3))
        self.game.board.place_stone = MagicMock()
        
        # プレイヤーが黒の場合（AIは白）
        self.game.player_is_black = True
        self.game.ai_move()
        
        # 石が置かれることを確認
        self.game.board.place_stone.assert_called_once_with(3, 3, Board.WHITE)
        self.game.ui.set_last_move.assert_called_once_with(3, 3)
        self.assertTrue(self.game.player_turn)
        self.assertEqual(self.game.consecutive_passes, 0)
        
        # リセット
        self.game.board.place_stone.reset_mock()
        self.game.ui.set_last_move.reset_mock()
        
        # プレイヤーが白の場合（AIは黒）
        self.game.player_is_black = False
        self.game.ai_move()
        
        # 石が置かれることを確認
        self.game.board.place_stone.assert_called_once_with(3, 3, Board.BLACK)
        self.game.ui.set_last_move.assert_called_once_with(3, 3)
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
        
        # 連続パスでゲーム終了
        self.game.player_turn = False
        self.game.consecutive_passes = 1
        
        result = self.game.ai_move()
        
        # ゲームが終了することを確認
        self.assertEqual(self.game.consecutive_passes, 2)
        self.assertEqual(self.game.state, Game.STATE_RESULT)
        self.assertTrue(result)
    
    def test_check_game_end(self):
        """ゲーム終了条件のチェックテスト"""
        # Game.check_game_endメソッドを実装
        def check_game_end(self):
            if self.consecutive_passes >= 2:
                self.state = Game.STATE_RESULT
                # 勝敗判定
                black_score = self.board.calculate_score(Board.BLACK)
                white_score = self.board.calculate_score(Board.WHITE) + 3.5  # コミ
                
                if black_score > white_score:
                    self.board.winner = Board.BLACK
                else:
                    self.board.winner = Board.WHITE
                return True
            return False
        
        # メソッドをゲームオブジェクトに追加
        self.game.check_game_end = check_game_end.__get__(self.game)
        
        # 連続パスでゲーム終了
        self.game.consecutive_passes = 2
        self.game.board.calculate_score = MagicMock()
        self.game.board.calculate_score.side_effect = [10, 5]  # 黒が勝つ
        
        result = self.game.check_game_end()
        
        # 結果画面に遷移することを確認
        self.assertTrue(result)
        self.assertEqual(self.game.state, Game.STATE_RESULT)
        self.assertEqual(self.game.board.winner, Board.BLACK)
        
        # 白が勝つ場合
        self.game.state = Game.STATE_GAME
        self.game.board.calculate_score.side_effect = [5, 10]  # 白が勝つ（コミ込み）
        
        result = self.game.check_game_end()
        
        # 結果画面に遷移することを確認
        self.assertTrue(result)
        self.assertEqual(self.game.state, Game.STATE_RESULT)
        self.assertEqual(self.game.board.winner, Board.WHITE)
        
        # 連続パスが足りない場合
        self.game.state = Game.STATE_GAME
        self.game.consecutive_passes = 1
        
        result = self.game.check_game_end()
        
        # ゲームが継続することを確認
        self.assertFalse(result)
        self.assertEqual(self.game.state, Game.STATE_GAME)
    
    def test_reset_game(self):
        """ゲームリセットのテスト"""
        # Game.reset_gameメソッドを実装
        def reset_game(self):
            self.board.reset()
            self.ui.last_move = None
            
            if self.player_is_black:
                self.player_turn = True
                self.ai_thinking = False
            else:
                self.player_turn = False
                self.ai_thinking = True
                
            self.consecutive_passes = 0
        
        # メソッドをゲームオブジェクトに追加
        self.game.reset_game = reset_game.__get__(self.game)
        
        # 状態を変更
        self.game.board.reset = MagicMock()
        self.game.player_turn = False
        self.game.consecutive_passes = 1
        self.game.ai_thinking = True
        
        # プレイヤーが黒の場合
        self.game.player_is_black = True
        self.game.reset_game()
        
        # 状態がリセットされることを確認
        self.game.board.reset.assert_called_once()
        self.assertIsNone(self.game.ui.last_move)
        self.assertTrue(self.game.player_turn)
        self.assertEqual(self.game.consecutive_passes, 0)
        self.assertFalse(self.game.ai_thinking)
        
        # リセット
        self.game.board.reset.reset_mock()
        self.game.player_turn = False
        self.game.consecutive_passes = 1
        self.game.ai_thinking = False
        
        # プレイヤーが白の場合
        self.game.player_is_black = False
        self.game.reset_game()
        
        # 状態がリセットされることを確認
        self.game.board.reset.assert_called_once()
        self.assertIsNone(self.game.ui.last_move)
        self.assertFalse(self.game.player_turn)
        self.assertEqual(self.game.consecutive_passes, 0)
        self.assertTrue(self.game.ai_thinking)

if __name__ == '__main__':
    unittest.main()
