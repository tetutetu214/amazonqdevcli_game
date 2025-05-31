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
        
        # 画面とサーフェスをモック化
        self.screen = MagicMock()
        self.screen.get_width.return_value = 1200
        self.screen.get_height.return_value = 700
        
        # 盤面をモック化
        self.board = MagicMock()
        self.board.size = 9
        
        # UIオブジェクトの作成
        with patch('pygame.Surface'):
            with patch('os.path.exists', return_value=False):
                self.ui = UI(self.screen, self.board)
    
    def test_init(self):
        """初期化のテスト"""
        self.assertEqual(self.ui.screen, self.screen)
        self.assertEqual(self.ui.board, self.board)
        self.assertEqual(self.ui.width, 1200)
        self.assertEqual(self.ui.height, 700)
    
    def test_get_board_position(self):
        """盤面位置の取得テスト"""
        # 盤面内の位置
        self.ui.board_x = 300
        self.ui.board_y = 150
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
        self.ui.start_button = pygame.Rect(500, 400, 200, 50)
        self.ui.pass_button = pygame.Rect(490, 630, 100, 40)
        self.ui.resign_button = pygame.Rect(610, 630, 100, 40)
        self.ui.play_again_button = pygame.Rect(500, 400, 200, 50)
        self.ui.back_to_title_button = pygame.Rect(500, 500, 200, 50)
        
        # スタートボタン
        pos = (600, 425)
        self.assertTrue(self.ui.is_start_button_clicked(pos))
        pos = (400, 425)
        self.assertFalse(self.ui.is_start_button_clicked(pos))
        
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
    
    def test_show_invalid_move_guide(self):
        """禁手ガイド表示のテスト"""
        # 盤面のget_invalid_move_reasonをモック化
        self.board.get_invalid_move_reason = MagicMock(return_value="自殺手です")
        
        # 禁手ガイドを表示
        self.ui.show_invalid_move_guide(3, 3)
        
        # ポップアップメッセージが設定されることを確認
        self.assertEqual(self.ui.popup_message, "自殺手です")
        self.assertGreater(self.ui.popup_timer, 0)
    
    @patch('pygame.draw.rect')
    @patch('pygame.draw.line')
    @patch('pygame.draw.circle')
    def test_draw_board(self, mock_circle, mock_line, mock_rect):
        """盤面描画のテスト"""
        # 盤面の状態をモック化
        self.board.board = MagicMock()
        self.board.board.__getitem__ = lambda self, idx: [Board.EMPTY] * 9
        self.board.is_valid_move = MagicMock(return_value=True)
        
        # マウス位置をモック化
        pygame.mouse.get_pos = MagicMock(return_value=(400, 250))
        self.ui.get_board_position = MagicMock(return_value=(2, 2))
        
        # 描画メソッドをモック化
        self.ui.draw_territories = MagicMock()
        
        # 盤面を描画
        self.ui.draw_board()
        
        # 各描画メソッドが呼ばれることを確認
        self.ui.draw_territories.assert_called_once()
        self.assertTrue(mock_line.called)
        self.assertTrue(mock_circle.called)
    
    @patch('pygame.Surface')
    @patch('pygame.draw.rect')
    def test_draw_territories(self, mock_rect, mock_surface):
        """陣地描画のテスト"""
        # 盤面の状態をモック化
        self.board.board = MagicMock()
        self.board.board.__getitem__ = lambda self, idx: [Board.EMPTY] * 9
        self.board.preview_board = None
        self.board.black_territory = MagicMock()
        self.board.white_territory = MagicMock()
        self.board.black_influence = MagicMock()
        self.board.white_influence = MagicMock()
        
        # __getitem__の挙動を定義
        def getitem_side_effect(idx):
            y, x = idx
            if x == 1 and y == 1:
                return True
            return False
        
        self.board.black_territory.__getitem__ = MagicMock(side_effect=getitem_side_effect)
        self.board.white_territory.__getitem__ = MagicMock(side_effect=getitem_side_effect)
        self.board.black_influence.__getitem__ = MagicMock(side_effect=getitem_side_effect)
        self.board.white_influence.__getitem__ = MagicMock(side_effect=getitem_side_effect)
        
        # 陣地を描画
        self.ui.draw_territories()
        
        # 描画メソッドが呼ばれることを確認
        self.assertTrue(mock_rect.called)
        self.assertTrue(mock_surface.called)
    
    def test_draw_popup_message(self):
        """ポップアップメッセージ描画のテスト"""
        # ポップアップメッセージを設定
        self.ui.popup_message = "テストメッセージ"
        self.ui.popup_timer = pygame.time.get_ticks()
        
        # 描画メソッドをモック化
        pygame.Surface = MagicMock()
        pygame.Surface.return_value = MagicMock()
        
        # ポップアップメッセージを描画
        with patch('pygame.time.get_ticks', return_value=self.ui.popup_timer + 1000):
            self.ui.draw_popup_message()
        
        # メッセージが表示されることを確認
        self.assertEqual(self.ui.popup_message, "テストメッセージ")
        
        # タイムアウト後はメッセージがクリアされる
        with patch('pygame.time.get_ticks', return_value=self.ui.popup_timer + 3000):
            self.ui.draw_popup_message()
        
        # メッセージがクリアされることを確認
        self.assertIsNone(self.ui.popup_message)

if __name__ == '__main__':
    unittest.main()
