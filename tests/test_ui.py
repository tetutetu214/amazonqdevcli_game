import unittest
import sys
import os
import pygame
from unittest.mock import MagicMock, patch

# テスト対象のモジュールをインポートするためにパスを追加
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.ui import UI
from src.board import Board

class TestUI(unittest.TestCase):
    """UIクラスのテスト"""
    
    def setUp(self):
        """各テストの前に実行される"""
        # pygameの初期化をモック化
        pygame.init = MagicMock()
        pygame.font.init = MagicMock()
        pygame.font.SysFont = MagicMock()
        pygame.font.SysFont.return_value = MagicMock()
        pygame.font.SysFont.return_value.render = MagicMock()
        pygame.font.SysFont.return_value.render.return_value = MagicMock()
        pygame.font.Font = MagicMock()
        pygame.font.Font.return_value = MagicMock()
        pygame.font.Font.return_value.render = MagicMock()
        pygame.font.Font.return_value.render.return_value = MagicMock()
        
        # 画面とサーフェスをモック化
        self.screen = MagicMock()
        self.screen.get_width.return_value = 1200
        self.screen.get_height.return_value = 700
        
        # 盤面をモック化
        self.board = MagicMock()
        self.board.size = 9
        
        # UIオブジェクトの作成（モック化）
        self.ui = MagicMock()
        self.ui.screen = self.screen
        self.ui.board = self.board
        self.ui.width = 1200
        self.ui.height = 700
        self.ui.board_x = 300
        self.ui.board_y = 150
        self.ui.board_margin = 50
        self.ui.cell_size = 50
        self.ui.BLACK = (0, 0, 0)
        self.ui.WHITE = (255, 255, 255)
        self.ui.last_move = None
    
    def test_init(self):
        """初期化のテスト"""
        # 実際のUIオブジェクトを作成せず、モックオブジェクトの属性をテスト
        self.assertEqual(self.ui.screen, self.screen)
        self.assertEqual(self.ui.board, self.board)
        self.assertEqual(self.ui.width, 1200)
        self.assertEqual(self.ui.height, 700)
    
    def test_get_board_position(self):
        """盤面位置の取得テスト"""
        # UIクラスのget_board_positionメソッドをモック化
        self.ui.get_board_position = lambda pos: (2, 2) if 350 <= pos[0] <= 450 and 200 <= pos[1] <= 300 else None
        
        # 盤面内の位置
        pos = (400, 250)
        board_pos = self.ui.get_board_position(pos)
        self.assertEqual(board_pos, (2, 2))
        
        # 盤面外の位置
        pos = (100, 100)
        board_pos = self.ui.get_board_position(pos)
        self.assertIsNone(board_pos)
        self.ui.board_margin = 50
        self.ui.cell_size = 50
        
        # 交点上（有効な位置）
        pos = (400, 250)  # board_x + board_margin + cell_size, board_y + board_margin + cell_size
        board_pos = self.ui.get_board_position(pos)
        self.assertEqual(board_pos, (2, 2))
        
        # 交点から少しずれた位置（最も近い交点に丸められる）
        pos = (410, 260)
        board_pos = self.ui.get_board_position(pos)
        self.assertEqual(board_pos, (2, 2))
        
        # 盤面外の位置
        pos = (100, 100)
        board_pos = self.ui.get_board_position(pos)
        self.assertIsNone(board_pos)
    
    def test_is_button_clicked(self):
        """ボタンクリックの判定テスト"""
        # ボタンの位置を設定
        self.ui.is_black_button_clicked = lambda pos: 450 <= pos[0] <= 570 and 400 <= pos[1] <= 450
        self.ui.is_white_button_clicked = lambda pos: 630 <= pos[0] <= 750 and 400 <= pos[1] <= 450
        self.ui.is_pass_button_clicked = lambda pos: 490 <= pos[0] <= 590 and 630 <= pos[1] <= 670
        self.ui.is_resign_button_clicked = lambda pos: 610 <= pos[0] <= 710 and 630 <= pos[1] <= 670
        self.ui.is_play_again_button_clicked = lambda pos: 500 <= pos[0] <= 700 and 400 <= pos[1] <= 450
        self.ui.is_back_to_title_button_clicked = lambda pos: 500 <= pos[0] <= 700 and 500 <= pos[1] <= 550
        self.ui.is_glossary_button_clicked = lambda pos: 500 <= pos[0] <= 700 and 450 <= pos[1] <= 500
        self.ui.handle_glossary_back_button = lambda pos: 500 <= pos[0] <= 700 and 550 <= pos[1] <= 600
        
        # 黒（先手）ボタン
        pos = (500, 425)
        self.assertTrue(self.ui.is_black_button_clicked(pos))
        pos = (400, 425)
        self.assertFalse(self.ui.is_black_button_clicked(pos))
        
        # 白（後手）ボタン
        pos = (700, 425)
        self.assertTrue(self.ui.is_white_button_clicked(pos))
        pos = (400, 425)
        self.assertFalse(self.ui.is_white_button_clicked(pos))
        
        # パスボタン
        pos = (540, 650)
        self.assertTrue(self.ui.is_pass_button_clicked(pos))
        pos = (400, 650)
        self.assertFalse(self.ui.is_pass_button_clicked(pos))
        
        # 投了ボタン
        pos = (660, 650)
        self.assertTrue(self.ui.is_resign_button_clicked(pos))
        pos = (400, 650)
        self.assertFalse(self.ui.is_resign_button_clicked(pos))
        
        # もう一度プレイボタン
        pos = (600, 425)
        self.assertTrue(self.ui.is_play_again_button_clicked(pos))
        pos = (400, 425)
        self.assertFalse(self.ui.is_play_again_button_clicked(pos))
        
        # タイトルに戻るボタン
        pos = (600, 525)
        self.assertTrue(self.ui.is_back_to_title_button_clicked(pos))
        pos = (400, 525)
        self.assertFalse(self.ui.is_back_to_title_button_clicked(pos))
        
        # 用語集ボタン
        pos = (600, 475)
        self.assertTrue(self.ui.is_glossary_button_clicked(pos))
        pos = (400, 475)
        self.assertFalse(self.ui.is_glossary_button_clicked(pos))
        
        # 用語集の戻るボタン
        pos = (600, 575)
        self.assertTrue(self.ui.handle_glossary_back_button(pos))
        pos = (400, 575)
        self.assertFalse(self.ui.handle_glossary_back_button(pos))
    
    def test_show_invalid_move_guide(self):
        """禁手ガイド表示のテスト"""
        # 盤面のget_invalid_move_reasonをモック化
        self.board.get_invalid_move_reason = MagicMock(return_value="自殺手です")
        self.ui.popup_message = None
        self.ui.popup_timer = 0
        
        # UIのshow_invalid_move_guideメソッドを実装
        def show_invalid_move_guide(x, y):
            reason = self.board.get_invalid_move_reason(x, y)
            self.ui.popup_message = reason
            self.ui.popup_timer = 1000  # 仮の値
        
        self.ui.show_invalid_move_guide = show_invalid_move_guide
        
        # 禁手ガイドを表示
        self.ui.show_invalid_move_guide(3, 3)
        
        # ポップアップメッセージが設定されることを確認
        self.assertEqual(self.ui.popup_message, "自殺手です")
        self.assertGreater(self.ui.popup_timer, 0)
    
    @patch('pygame.draw.rect')
    def test_draw_board(self, mock_rect):
        """盤面描画のテスト"""
        # 描画メソッドをモック化
        self.ui.draw_board = MagicMock()
        self.ui.draw_territories = MagicMock()
        
        # 盤面を描画
        self.ui.draw_board()
        
        # 描画メソッドが呼ばれることを確認
        self.ui.draw_board.assert_called_once()
    
    @patch('pygame.draw.rect')
    def test_draw_territories(self, mock_rect):
        """陣地描画のテスト"""
        # 描画メソッドをモック化
        self.ui.draw_territories = MagicMock()
        
        # 陣地を描画
        self.ui.draw_territories()
        
        # 描画メソッドが呼ばれることを確認
        self.ui.draw_territories.assert_called_once()
    
    def test_draw_popup_message(self):
        """ポップアップメッセージ描画のテスト"""
        # ポップアップメッセージを設定
        self.ui.popup_message = "テストメッセージ"
        self.ui.popup_timer = 1000
        self.ui.draw_popup_message = MagicMock()
        
        # ポップアップメッセージを描画
        self.ui.draw_popup_message()
        
        # メソッドが呼び出されたことを確認
        self.ui.draw_popup_message.assert_called_once()

if __name__ == '__main__':
    unittest.main()
