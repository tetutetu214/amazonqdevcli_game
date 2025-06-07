import pygame
import os
import random
import math
import sys
import numpy as np
from .board import Board

class UI:
    """
    ゲームのUI表示を担当するクラス。
    画面描画、ボタン処理、マウス操作などを管理。
    """
    
    # 色の定義
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    BOARD_COLOR = (219, 181, 113)  # 碁盤の色
    LINE_COLOR = (0, 0, 0)
    BLUE = (0, 0, 255, 128)  # 黒の確定陣地
    LIGHT_BLUE = (0, 191, 255, 128)  # 黒の影響圏
    RED = (255, 0, 0, 128)  # 白の確定陣地
    PINK = (255, 105, 180, 128)  # 白の影響圏
    GRAY = (128, 128, 128, 128)  # 重複領域
    LAST_MOVE_MARKER = (255, 0, 0)  # 最後の手のマーカー
    
    def __init__(self, screen, board):
        """
        UIの初期化
        
        Args:
            screen: pygameのスクリーンオブジェクト
            board: 盤面オブジェクト
        """
        self.screen = screen
        self.board = board
        self.width = screen.get_width()
        self.height = screen.get_height()
        
        # 盤面の描画パラメータ
        self.board_size = min(self.width * 0.6, self.height * 0.8)
        self.cell_size = self.board_size / (self.board.size + 1)
        self.board_margin = self.cell_size
        self.board_x = (self.width - self.board_size) / 2
        self.board_y = (self.height - self.board_size) / 2
        
        # フォントの初期化
        pygame.font.init()
        try:
            # 和風フォントを使用
            font_paths = [
                '/mnt/c/Windows/Fonts/HGRSKP.TTC',  # HG行書体
                '/mnt/c/Windows/Fonts/HGRGM.TTC',   # HG正楷書体
                '/mnt/c/Windows/Fonts/NotoSansJP-VF.ttf',  # Noto Sans JP
                '/usr/share/fonts/opentype/ipaexfont-gothic/ipaexg.ttf',  # IPAex Gothic
                '/usr/share/fonts/opentype/ipaexfont-mincho/ipaexm.ttf',  # IPAex Mincho
                '/usr/share/fonts/truetype/fonts-japanese-gothic.ttf',  # システムの日本語ゴシック
                '/usr/share/fonts/truetype/fonts-japanese-mincho.ttf'   # システムの日本語明朝
            ]
            
            for font_path in font_paths:
                if os.path.exists(font_path):
                    self.title_font = pygame.font.Font(font_path, 60)
                    self.large_font = pygame.font.Font(font_path, 36)
                    self.medium_font = pygame.font.Font(font_path, 24)
                    self.small_font = pygame.font.Font(font_path, 18)
                    print(f"日本語フォントを読み込みました: {font_path}")
                    break
            else:
                # フォントが見つからない場合はシステムフォントを使用
                self.title_font = pygame.font.SysFont(None, 60)
                self.large_font = pygame.font.SysFont(None, 36)
                self.medium_font = pygame.font.SysFont(None, 24)
                self.small_font = pygame.font.SysFont(None, 18)
                print("日本語フォントが見つかりませんでした。システムフォントを使用します。")
        except Exception as e:
            # フォントが見つからない場合はシステムフォントを使用
            print(f"フォント読み込みエラー: {e}")
            self.title_font = pygame.font.SysFont(None, 60)
            self.large_font = pygame.font.SysFont(None, 36)
            self.medium_font = pygame.font.SysFont(None, 24)
            self.small_font = pygame.font.SysFont(None, 18)
        
        # ボタンの定義
        self.start_button = pygame.Rect(self.width // 2 - 100, self.height * 0.5, 200, 50)
        self.pass_button = pygame.Rect(self.width // 2 - 110, self.height - 70, 100, 40)
        self.resign_button = pygame.Rect(self.width // 2 + 10, self.height - 70, 100, 40)
        self.play_again_button = pygame.Rect(self.width // 2 - 100, self.height * 0.7, 200, 50)
        self.back_to_title_button = pygame.Rect(self.width // 2 - 100, self.height * 0.85, 200, 50)
        
        # ゲーム開始ボタン（黒石のみ）
        self.black_button = pygame.Rect(self.width // 2 - 100, self.height * 0.4, 200, 50)
        
        # 画像の読み込み
        self.load_images()
        
        # ポップアップメッセージ
        self.popup_message = None
        self.popup_timer = 0
        
        # 最後の手の位置
        self.last_move = None
    
    def load_images(self):
        """画像リソースの読み込み"""
        # 画像ディレクトリのパス
        image_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'images')
        title_image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'image', 'title.png')
        
        # タイトル画像の読み込み
        if os.path.exists(title_image_path):
            self.title_img = pygame.image.load(title_image_path)
            # 画面の幅に合わせてリサイズ（高さは比率を維持）
            img_width = self.width * 0.8
            img_height = img_width * self.title_img.get_height() / self.title_img.get_width()
            self.title_img = pygame.transform.scale(self.title_img, (int(img_width), int(img_height)))
            print(f"タイトル画像を読み込みました: {title_image_path}")
        else:
            self.title_img = None
            print(f"タイトル画像が見つかりませんでした: {title_image_path}")
        
        # デフォルトの画像を作成（実際の画像がない場合用）
        self.create_default_images()
        
        # 背景画像の読み込み（存在する場合）
        bg_path = os.path.join(image_dir, 'background.jpg')
        if os.path.exists(bg_path):
            self.background_img = pygame.image.load(bg_path)
            self.background_img = pygame.transform.scale(self.background_img, (self.width, self.height))
        
        # 盤面テクスチャの読み込み（存在する場合）
        board_path = os.path.join(image_dir, 'board.jpg')
        if os.path.exists(board_path):
            self.board_img = pygame.image.load(board_path)
            self.board_img = pygame.transform.scale(self.board_img, (int(self.board_size), int(self.board_size)))
    
    def create_default_images(self):
        """デフォルトの画像を作成"""
        # デフォルトの背景（和紙風）
        self.background_img = pygame.Surface((self.width, self.height))
        self.background_img.fill((245, 240, 230))  # 薄い和紙色
        
        # 背景に和風の模様を追加
        for i in range(100):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            radius = random.randint(1, 3)
            color = (230, 225, 215)  # 少し暗い和紙の色
            pygame.draw.circle(self.background_img, color, (x, y), radius)
        
        # デフォルトの盤面（木目調）
        self.board_img = pygame.Surface((int(self.board_size), int(self.board_size)))
        self.board_img.fill((219, 181, 113))  # 碁盤の色
        
        # 木目模様を追加
        for i in range(50):
            x1 = random.randint(0, int(self.board_size))
            y1 = random.randint(0, int(self.board_size))
            length = random.randint(20, 100)
            thickness = random.randint(1, 3)
            angle = random.uniform(0, math.pi)
            x2 = x1 + int(length * math.cos(angle))
            y2 = y1 + int(length * math.sin(angle))
            color = (200, 160, 100)  # 木目の色
            pygame.draw.line(self.board_img, color, (x1, y1), (x2, y2), thickness)
    
    def draw_title_screen(self):
        """タイトル画面の描画"""
        # 背景をクリア
        self.screen.fill((0, 0, 0))  # 一度画面を黒でクリア
        # 背景
        self.screen.blit(self.background_img, (0, 0))
        
        # タイトル画像がある場合は表示
        if hasattr(self, 'title_img') and self.title_img is not None:
            # 画面上部に配置
            self.screen.blit(self.title_img, 
                            (self.width // 2 - self.title_img.get_width() // 2, 
                             self.height * 0.1))
        else:
            # タイトル画像がない場合はテキストを表示
            title_text = self.title_font.render("GOGO 囲碁", True, self.BLACK)
            self.screen.blit(title_text, (self.width // 2 - title_text.get_width() // 2, self.height * 0.2))
        
        # ゲーム開始ボタン
        pygame.draw.rect(self.screen, (50, 50, 50), self.black_button)
        pygame.draw.rect(self.screen, self.BLACK, self.black_button, 2)
        black_text = self.medium_font.render("ゲーム開始", True, self.WHITE)
        self.screen.blit(black_text, (self.black_button.centerx - black_text.get_width() // 2, 
                                    self.black_button.centery - black_text.get_height() // 2))
    
    # 用語集関連のメソッドを削除
    def draw_game_screen(self, player_turn, ai_thinking):
        """
        ゲーム画面の描画
        
        Args:
            player_turn: プレイヤーの手番かどうか
            ai_thinking: AIが思考中かどうか
        """
        # 背景
        self.screen.blit(self.background_img, (0, 0))
        
        # 盤面の描画
        self.draw_board()
        
        # 優位性グラフの描画（画面上部に配置）
        self.draw_advantage_bar()
        
        # プレイヤー情報（左側）
        self.draw_player_info()
        
        # AI情報（右側）
        self.draw_ai_info(ai_thinking)
        
        # パスボタン
        pygame.draw.rect(self.screen, (200, 200, 200), self.pass_button)
        pygame.draw.rect(self.screen, self.BLACK, self.pass_button, 2)
        pass_text = self.medium_font.render("パス", True, self.BLACK)
        self.screen.blit(pass_text, (self.pass_button.centerx - pass_text.get_width() // 2, 
                                    self.pass_button.centery - pass_text.get_height() // 2))
        
        # 投了ボタン
        pygame.draw.rect(self.screen, (200, 200, 200), self.resign_button)
        pygame.draw.rect(self.screen, self.BLACK, self.resign_button, 2)
        resign_text = self.medium_font.render("投了", True, self.BLACK)
        self.screen.blit(resign_text, (self.resign_button.centerx - resign_text.get_width() // 2, 
                                      self.resign_button.centery - resign_text.get_height() // 2))
        
        # ポップアップメッセージの表示
        self.draw_popup_message()
    
    def draw_board(self):
        """盤面の描画"""
        # 盤面の背景
        self.screen.blit(self.board_img, (self.board_x, self.board_y))
        
        # 陣地の描画
        self.draw_territories()
        
        # 格子線の描画
        for i in range(self.board.size):
            # 横線
            pygame.draw.line(self.screen, self.LINE_COLOR,
                            (self.board_x + self.board_margin, self.board_y + self.board_margin + i * self.cell_size),
                            (self.board_x + self.board_size - self.board_margin, self.board_y + self.board_margin + i * self.cell_size),
                            2)
            # 縦線
            pygame.draw.line(self.screen, self.LINE_COLOR,
                            (self.board_x + self.board_margin + i * self.cell_size, self.board_y + self.board_margin),
                            (self.board_x + self.board_margin + i * self.cell_size, self.board_y + self.board_size - self.board_margin),
                            2)
        
        # 星の位置（天元と四隅）
        if self.board.size == 9:
            star_points = [(2, 2), (2, 6), (4, 4), (6, 2), (6, 6)]
            for x, y in star_points:
                pygame.draw.circle(self.screen, self.BLACK,
                                  (int(self.board_x + self.board_margin + x * self.cell_size),
                                   int(self.board_y + self.board_margin + y * self.cell_size)),
                                  int(self.cell_size * 0.1))
        
        # 石の描画
        for y in range(self.board.size):
            for x in range(self.board.size):
                if self.board.board[y, x] != Board.EMPTY:
                    color = self.BLACK if self.board.board[y, x] == Board.BLACK else self.WHITE
                    stone_x = int(self.board_x + self.board_margin + x * self.cell_size)
                    stone_y = int(self.board_y + self.board_margin + y * self.cell_size)
                    stone_radius = int(self.cell_size * 0.45)
                    
                    # 石を描画
                    pygame.draw.circle(self.screen, color, (stone_x, stone_y), stone_radius)
                    
                    # 最後の手のマーカーを描画
                    if self.last_move and self.last_move == (x, y):
                        marker_radius = int(self.cell_size * 0.5)
                        pygame.draw.circle(self.screen, self.LAST_MOVE_MARKER, (stone_x, stone_y), marker_radius, 2)
        
        # プレビューの描画
        mouse_pos = pygame.mouse.get_pos()
        board_pos = self.get_board_position(mouse_pos)
        if board_pos:
            x, y = board_pos
            if self.board.is_valid_move(x, y):
                # プレイヤーは常に黒石
                preview_color = (0, 0, 0, 128)  # 黒の半透明
                s = pygame.Surface((int(self.cell_size * 0.9), int(self.cell_size * 0.9)), pygame.SRCALPHA)
                pygame.draw.circle(s, preview_color, (int(s.get_width() / 2), int(s.get_height() / 2)), int(self.cell_size * 0.45))
                self.screen.blit(s, (int(self.board_x + self.board_margin + x * self.cell_size - self.cell_size * 0.45),
                                    int(self.board_y + self.board_margin + y * self.cell_size - self.cell_size * 0.45)))
    
    def draw_territories(self):
        """陣地と影響圏の描画"""
        # プレビューがある場合はプレビューの陣地を表示
        if self.board.preview_board is not None:
            black_territory = self.board.preview_black_territory
            white_territory = self.board.preview_white_territory
            black_influence = self.board.preview_black_influence
            white_influence = self.board.preview_white_influence
        else:
            black_territory = self.board.black_territory
            white_territory = self.board.white_territory
            black_influence = self.board.black_influence
            white_influence = self.board.white_influence
        
        # 半透明のサーフェスを作成
        territory_surface = pygame.Surface((self.board_size, self.board_size), pygame.SRCALPHA)
        
        for y in range(self.board.size):
            for x in range(self.board.size):
                if self.board.board[y, x] == Board.EMPTY:
                    rect = pygame.Rect(
                        self.board_margin + x * self.cell_size - self.cell_size / 2,
                        self.board_margin + y * self.cell_size - self.cell_size / 2,
                        self.cell_size,
                        self.cell_size
                    )
                    
                    # 確定陣地
                    if black_territory[y, x]:
                        pygame.draw.rect(territory_surface, self.BLUE, rect)
                    elif white_territory[y, x]:
                        pygame.draw.rect(territory_surface, self.RED, rect)
                    # 影響圏（確定陣地でない場合）
                    elif black_influence[y, x] and white_influence[y, x]:
                        pygame.draw.rect(territory_surface, self.GRAY, rect)  # 重複領域
                    elif black_influence[y, x]:
                        pygame.draw.rect(territory_surface, self.LIGHT_BLUE, rect)
                    elif white_influence[y, x]:
                        pygame.draw.rect(territory_surface, self.PINK, rect)
        
        # 半透明のサーフェスを盤面に描画
        self.screen.blit(territory_surface, (self.board_x, self.board_y))
    
    def draw_player_info(self):
        """プレイヤー情報の描画（左側）"""
        # プレイヤーは常に黒石
        player_color = "黒"
        player_stone = Board.BLACK
        
        # プレイヤー名
        player_text = self.medium_font.render(f"プレイヤー（{player_color}）", True, self.BLACK)
        self.screen.blit(player_text, (self.width * 0.1, self.height * 0.2))
        
        # 取った石の数
        captures = self.board.black_captures
        captures_text = self.small_font.render(f"取った石: {captures}", True, self.BLACK)
        self.screen.blit(captures_text, (self.width * 0.1, self.height * 0.25))
        
        # 陣地ポイント
        territory_count = sum(sum(self.board.black_territory))
        territory_text = self.small_font.render(f"陣地: {territory_count}", True, self.BLACK)
        self.screen.blit(territory_text, (self.width * 0.1, self.height * 0.3))
        
        # 合計得点
        total_score = self.board.calculate_score(player_stone)
        score_text = self.medium_font.render(f"合計: {total_score}", True, self.BLACK)
        self.screen.blit(score_text, (self.width * 0.1, self.height * 0.35))
        
        # 陣地の色説明
        color_info = [
            ("確定陣地", self.BLUE),
            ("影響圏", self.LIGHT_BLUE)
        ]
        
        for i, (text, color) in enumerate(color_info):
            y_pos = self.height * 0.45 + i * 30
            pygame.draw.rect(self.screen, color, (self.width * 0.1, y_pos, 20, 20))
            text_surface = self.small_font.render(text, True, self.BLACK)
            self.screen.blit(text_surface, (self.width * 0.1 + 30, y_pos))
    
    def draw_ai_info(self, ai_thinking):
        """
        AI情報の描画（右側）
        
        Args:
            ai_thinking: AIが思考中かどうか
        """
        # AIは常に白石
        ai_color = "白"
        ai_stone = Board.WHITE
        
        # AI名
        ai_text = self.medium_font.render(f"AI（{ai_color}）", True, self.BLACK)
        self.screen.blit(ai_text, (self.width * 0.8, self.height * 0.2))
        
        # 取った石の数
        captures = self.board.white_captures
        captures_text = self.small_font.render(f"取った石: {captures}", True, self.BLACK)
        self.screen.blit(captures_text, (self.width * 0.8, self.height * 0.25))
        
        # 陣地ポイント
        territory_count = sum(sum(self.board.white_territory))
        territory_text = self.small_font.render(f"陣地: {territory_count}", True, self.BLACK)
        self.screen.blit(territory_text, (self.width * 0.8, self.height * 0.3))
        
        # コミ (白の場合のみ表示)
        komi_text = self.small_font.render("コミ: 3.5", True, self.BLACK)
        self.screen.blit(komi_text, (self.width * 0.8, self.height * 0.35))
        
        # 合計得点
        total_score = self.board.calculate_score(ai_stone) + 3.5  # 白の場合はコミを加算
        score_text = self.medium_font.render(f"合計: {total_score}", True, self.BLACK)
        self.screen.blit(score_text, (self.width * 0.8, self.height * 0.4))
        
        # 陣地の色説明
        color_info = [
            ("確定陣地", self.RED),
            ("影響圏", self.PINK)
        ]
        
        for i, (text, color) in enumerate(color_info):
            y_pos = self.height * 0.5 + i * 30
            pygame.draw.rect(self.screen, color, (self.width * 0.8, y_pos, 20, 20))
            text_surface = self.small_font.render(text, True, self.BLACK)
            self.screen.blit(text_surface, (self.width * 0.8 + 30, y_pos))
        
        # 重複領域の説明
        pygame.draw.rect(self.screen, self.GRAY, (self.width * 0.8, self.height * 0.5 + 60, 20, 20))
        overlap_text = self.small_font.render("争点", True, self.BLACK)
        self.screen.blit(overlap_text, (self.width * 0.8 + 30, self.height * 0.5 + 60))
        
        # AI思考中表示
        if ai_thinking:
            thinking_text = self.medium_font.render("AI思考中...", True, (200, 0, 0))
            self.screen.blit(thinking_text, (self.width * 0.8, self.height * 0.7))  # 位置を下に移動
    
    def draw_result_screen(self):
        """結果画面の描画"""
        # 背景をクリア
        self.screen.fill((0, 0, 0))  # 一度画面を黒でクリア
        # 背景
        self.screen.blit(self.background_img, (0, 0))
        
        # プレイヤーは常に黒石、AIは常に白石
        player_stone = Board.BLACK
        ai_stone = Board.WHITE
        
        # 結果タイトル
        result_text = self.large_font.render("対局結果", True, self.BLACK)
        self.screen.blit(result_text, (self.width // 2 - result_text.get_width() // 2, self.height * 0.2))
        
        # プレイヤーの得点
        player_score = self.board.calculate_score(player_stone)
        player_captures = self.board.black_captures
        player_territory = sum(sum(self.board.black_territory))
        
        player_text = self.medium_font.render(f"プレイヤー（黒）: {player_captures} + {player_territory} = {player_score}", True, self.BLACK)
        self.screen.blit(player_text, (self.width // 2 - player_text.get_width() // 2, self.height * 0.3))
        
        # AIの得点
        ai_score = self.board.calculate_score(ai_stone) + 3.5  # 白の場合はコミを加算
        ai_captures = self.board.white_captures
        ai_territory = sum(sum(self.board.white_territory))
        
        ai_text = self.medium_font.render(f"AI（白）: {ai_captures} + {ai_territory} + 3.5 = {ai_score}", True, self.BLACK)
        self.screen.blit(ai_text, (self.width // 2 - ai_text.get_width() // 2, self.height * 0.35))
        
        # 勝敗結果
        if self.board.winner == player_stone:
            result = "プレイヤーの勝利！"
        elif self.board.winner == ai_stone:
            result = "AIの勝利！"
        else:
            result = "引き分け"
        
        winner_text = self.large_font.render(result, True, self.BLACK)
        self.screen.blit(winner_text, (self.width // 2 - winner_text.get_width() // 2, self.height * 0.45))
        
        # もう一度プレイボタン
        pygame.draw.rect(self.screen, (200, 200, 200), self.play_again_button)
        pygame.draw.rect(self.screen, self.BLACK, self.play_again_button, 2)
        play_again_text = self.medium_font.render("もう一度プレイ", True, self.BLACK)
        self.screen.blit(play_again_text, (self.play_again_button.centerx - play_again_text.get_width() // 2, 
                                         self.play_again_button.centery - play_again_text.get_height() // 2))
        
        # タイトルに戻るボタン
        pygame.draw.rect(self.screen, (200, 200, 200), self.back_to_title_button)
        pygame.draw.rect(self.screen, self.BLACK, self.back_to_title_button, 2)
        back_text = self.medium_font.render("タイトルに戻る", True, self.BLACK)
        self.screen.blit(back_text, (self.back_to_title_button.centerx - back_text.get_width() // 2, 
                                    self.back_to_title_button.centery - back_text.get_height() // 2))
    
    def get_board_position(self, pos):
        """
        画面上の座標から盤面上の座標を取得
        
        Args:
            pos: 画面上の座標 (x, y)
            
        Returns:
            tuple or None: 盤面上の座標 (x, y) または盤面外の場合はNone
        """
        x, y = pos
        
        # 盤面の範囲内かチェック
        if (self.board_x + self.board_margin - self.cell_size / 2 <= x <= self.board_x + self.board_size - self.board_margin + self.cell_size / 2 and
            self.board_y + self.board_margin - self.cell_size / 2 <= y <= self.board_y + self.board_size - self.board_margin + self.cell_size / 2):
            
            # 盤面上の座標に変換
            board_x = round((x - self.board_x - self.board_margin) / self.cell_size)
            board_y = round((y - self.board_y - self.board_margin) / self.cell_size)
            
            # 盤面の範囲内かチェック
            if 0 <= board_x < self.board.size and 0 <= board_y < self.board.size:
                return (board_x, board_y)
        
        return None
    
    def is_start_button_clicked(self, pos):
        """
        スタートボタンがクリックされたかどうかを判定
        
        Args:
            pos: クリック位置の座標
            
        Returns:
            bool: ボタンがクリックされたかどうか
        """
        return self.start_button.collidepoint(pos)
    
    def is_pass_button_clicked(self, pos):
        """
        パスボタンがクリックされたかどうかを判定
        
        Args:
            pos: クリック位置の座標
            
        Returns:
            bool: ボタンがクリックされたかどうか
        """
        return self.pass_button.collidepoint(pos)
    
    def is_resign_button_clicked(self, pos):
        """
        投了ボタンがクリックされたかどうかを判定
        
        Args:
            pos: クリック位置の座標
            
        Returns:
            bool: ボタンがクリックされたかどうか
        """
        return self.resign_button.collidepoint(pos)
    
    def is_play_again_button_clicked(self, pos):
        """
        もう一度プレイボタンがクリックされたかどうかを判定
        
        Args:
            pos: クリック位置の座標
            
        Returns:
            bool: ボタンがクリックされたかどうか
        """
        return self.play_again_button.collidepoint(pos)
    
    def is_back_to_title_button_clicked(self, pos):
        """
        タイトルに戻るボタンがクリックされたかどうかを判定
        
        Args:
            pos: クリック位置の座標
            
        Returns:
            bool: ボタンがクリックされたかどうか
        """
        return self.back_to_title_button.collidepoint(pos)
    
    def show_popup_message(self, message):
        """
        ポップアップメッセージを表示
        
        Args:
            message: 表示するメッセージ
        """
        self.popup_message = message
        self.popup_timer = pygame.time.get_ticks()
    
    def show_invalid_move_guide(self, x, y):
        """
        禁手ガイドを表示
        
        Args:
            x, y: 石を置こうとした位置の座標
        """
        reason = self.board.get_invalid_move_reason(x, y)
        self.popup_message = reason
        self.popup_timer = pygame.time.get_ticks()
    
    def draw_popup_message(self):
        """ポップアップメッセージの描画"""
        if self.popup_message:
            current_time = pygame.time.get_ticks()
            if current_time - self.popup_timer < 3000:  # 3秒間表示（連続パス終了メッセージを見やすくするため延長）
                # 半透明の背景
                popup_surface = pygame.Surface((400, 80), pygame.SRCALPHA)
                popup_surface.fill((0, 0, 0, 180))
                
                # メッセージテキスト
                message_text = self.medium_font.render(self.popup_message, True, self.WHITE)
                popup_surface.blit(message_text, (200 - message_text.get_width() // 2, 40 - message_text.get_height() // 2))
                
                # 画面中央に表示
                self.screen.blit(popup_surface, (self.width // 2 - 200, self.height // 2 - 40))
            else:
                self.popup_message = None
    # 用語集関連のメソッドを削除
    def draw_advantage_bar(self):
        """優位性を示す横棒グラフを描画"""
        # プレイヤーは常に黒石、AIは常に白石
        player_stone = Board.BLACK
        ai_stone = Board.WHITE
        
        # グラフの位置とサイズ
        bar_width = self.width * 0.4
        bar_height = 30
        bar_x = (self.width - bar_width) / 2
        bar_y = 30  # 画面上部に配置
        
        # プレイヤーとAIの得点を計算（コミを含む）
        player_score = self.board.calculate_score(player_stone)
        ai_score = self.board.calculate_score(ai_stone)
        
        # 石の数と陣地の数を考慮した勝率計算
        player_stones = np.sum(self.board.board == player_stone)
        ai_stones = np.sum(self.board.board == ai_stone)
        
        # 陣地の数
        player_territory = np.sum(self.board.black_territory)
        ai_territory = np.sum(self.board.white_territory)
        
        # 取った石の数
        player_captures = self.board.black_captures
        ai_captures = self.board.white_captures
        
        # コミを考慮
        ai_score += 3.5  # AIが白の場合はコミを加算
        
        # 盤面の進行度に応じて重みを変える（序盤は石の数、中盤は取った石の数、終盤は陣地を重視）
        total_stones = player_stones + ai_stones
        board_progress = min(1.0, total_stones / (self.board.size * self.board.size * 0.7))  # 70%埋まったら終盤とみなす
        
        # 序盤は石の数と位置、中盤は取った石、終盤は陣地で勝率を計算
        if board_progress < 0.3:  # 序盤
            # 石の配置の良さを評価（中央に近いほど良い）
            player_position_score = 0
            ai_position_score = 0
            center = self.board.size // 2
            
            for y in range(self.board.size):
                for x in range(self.board.size):
                    if self.board.board[y, x] == player_stone:
                        # 中央からの距離が小さいほど高得点
                        distance = abs(x - center) + abs(y - center)
                        player_position_score += (self.board.size - distance) / 2
                    elif self.board.board[y, x] == ai_stone:
                        distance = abs(x - center) + abs(y - center)
                        ai_position_score += (self.board.size - distance) / 2
            
            # 序盤の評価（石の数と位置）
            player_eval = player_stones * 2 + player_position_score
            ai_eval = ai_stones * 2 + ai_position_score
            
        elif board_progress < 0.7:  # 中盤
            # 中盤の評価（石の数と取った石の数）
            player_eval = player_stones + player_captures * 2 + player_territory * 0.5
            ai_eval = ai_stones + ai_captures * 2 + ai_territory * 0.5
            
        else:  # 終盤
            # 終盤の評価（陣地と最終スコア）
            player_eval = player_score
            ai_eval = ai_score
        
        # 勝率の計算（シグモイド関数で0.1～0.9の範囲に収める）
        advantage = (player_eval - ai_eval) / max(10, (player_eval + ai_eval) * 0.5)
        player_win_rate = 1.0 / (1.0 + np.exp(-advantage * 3))  # シグモイド関数
        player_win_rate = max(0.1, min(0.9, player_win_rate))  # 0.1～0.9の範囲に制限
        
        # 手番によるわずかな補正（手番があるほうが有利）
        from .game import Game
        game_instance = None
        for frame in sys._current_frames().values():
            for local_var in frame.f_locals.values():
                if isinstance(local_var, Game):
                    game_instance = local_var
                    break
            if game_instance:
                break
                
        if game_instance and game_instance.player_turn:
            player_win_rate += 0.03
        else:
            player_win_rate -= 0.03
        
        player_win_rate = max(0.1, min(0.9, player_win_rate))  # 再度範囲を制限
        
        # プレイヤーの部分の幅を計算
        player_width = bar_width * player_win_rate
        
        # 背景（枠）を描画 - 半透明の背景を追加
        bg_surface = pygame.Surface((bar_width + 4, bar_height + 4), pygame.SRCALPHA)
        bg_surface.fill((255, 255, 255, 180))  # 半透明の白
        self.screen.blit(bg_surface, (bar_x - 2, bar_y - 2))
        
        pygame.draw.rect(self.screen, (200, 200, 200), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(self.screen, self.BLACK, (bar_x, bar_y, bar_width, bar_height), 2)
        
        # プレイヤー側（左側）
        player_color = (0, 0, 0, 200)  # 黒（半透明）
        pygame.draw.rect(self.screen, player_color, (bar_x, bar_y, player_width, bar_height))
        
        # AI側（右側）
        ai_color = (255, 255, 255, 200)  # 白（半透明）
        pygame.draw.rect(self.screen, ai_color, (bar_x + player_width, bar_y, bar_width - player_width, bar_height))
        
        # 中央線
        pygame.draw.line(self.screen, (100, 100, 100), 
                         (bar_x + bar_width / 2, bar_y), 
                         (bar_x + bar_width / 2, bar_y + bar_height), 2)
        
        # パーセンテージ表示
        player_percent = int(player_win_rate * 100)
        ai_percent = 100 - player_percent
        
        # プレイヤーのパーセンテージ
        player_text_color = self.WHITE  # 黒背景に白文字
        player_text = self.small_font.render(f"{player_percent}%", True, player_text_color)
        if player_width > player_text.get_width() + 10:  # 十分なスペースがある場合
            self.screen.blit(player_text, (bar_x + 10, bar_y + bar_height/2 - player_text.get_height()/2))
        
        # AIのパーセンテージ
        ai_text_color = self.BLACK  # 白背景に黒文字
        ai_text = self.small_font.render(f"{ai_percent}%", True, ai_text_color)
        if bar_width - player_width > ai_text.get_width() + 10:  # 十分なスペースがある場合
            self.screen.blit(ai_text, (bar_x + player_width + 10, bar_y + bar_height/2 - ai_text.get_height()/2))
        
        # 優位性の説明テキスト
        advantage_text = self.small_font.render("優勢", True, self.BLACK)
        self.screen.blit(advantage_text, (bar_x, bar_y - 25))
        
        # プレイヤーとAIのラベル
        player_text = self.small_font.render("プレイヤー", True, self.BLACK)
        self.screen.blit(player_text, (bar_x, bar_y + bar_height + 5))
        
        ai_text = self.small_font.render("AI", True, self.BLACK)
        self.screen.blit(ai_text, (bar_x + bar_width - ai_text.get_width(), bar_y + bar_height + 5))
    # 用語集関連のメソッドを削除
    def is_black_button_clicked(self, pos):
        """
        黒（先手）ボタンがクリックされたかどうかを判定
        
        Args:
            pos: クリック位置の座標
            
        Returns:
            bool: ボタンがクリックされたかどうか
        """
        return self.black_button.collidepoint(pos)
    
    def is_white_button_clicked(self, pos):
        """
        白（後手）ボタンがクリックされたかどうかを判定
        
        Args:
            pos: クリック位置の座標
            
        Returns:
            bool: ボタンがクリックされたかどうか
        """
        return self.white_button.collidepoint(pos)
        
    def set_last_move(self, x, y):
        """
        最後の手の位置を設定
        
        Args:
            x, y: 最後の手の座標
        """
        self.last_move = (x, y)
