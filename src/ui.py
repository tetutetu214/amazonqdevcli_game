# -*- coding: utf-8 -*-
import pygame
import os
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
            # Windowsの日本語フォントを使用
            self.title_font = pygame.font.Font('/mnt/c/Windows/Fonts/NotoSansJP-VF.ttf', 48)
            self.large_font = pygame.font.Font('/mnt/c/Windows/Fonts/NotoSansJP-VF.ttf', 36)
            self.medium_font = pygame.font.Font('/mnt/c/Windows/Fonts/NotoSansJP-VF.ttf', 24)
            self.small_font = pygame.font.Font('/mnt/c/Windows/Fonts/NotoSansJP-VF.ttf', 18)
        except:
            # フォントが見つからない場合はシステムフォントを使用
            self.title_font = pygame.font.SysFont(None, 48)
            self.large_font = pygame.font.SysFont(None, 36)
            self.medium_font = pygame.font.SysFont(None, 24)
            self.small_font = pygame.font.SysFont(None, 18)
        
        # ボタンの定義
        self.start_button = pygame.Rect(self.width // 2 - 100, self.height * 0.6, 200, 50)
        self.glossary_button = pygame.Rect(self.width // 2 - 100, self.height * 0.7, 200, 50)
        self.pass_button = pygame.Rect(self.width // 2 - 110, self.height - 70, 100, 40)
        self.resign_button = pygame.Rect(self.width // 2 + 10, self.height - 70, 100, 40)
        self.play_again_button = pygame.Rect(self.width // 2 - 100, self.height * 0.7, 200, 50)
        self.back_to_title_button = pygame.Rect(self.width // 2 - 100, self.height * 0.85, 200, 50)  # 位置を下に移動
        
        # 画像の読み込み
        self.load_images()
        
        # ポップアップメッセージ
        self.popup_message = None
        self.popup_timer = 0
        
        # 画面状態
        self.show_glossary = False
    
    def load_images(self):
        """画像リソースの読み込み"""
        # 画像ディレクトリのパス
        image_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'images')
        
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
        # デフォルトの背景（畳風）
        self.background_img = pygame.Surface((self.width, self.height))
        self.background_img.fill((240, 230, 190))  # 薄い黄土色
        
        # デフォルトの盤面（木目調）
        self.board_img = pygame.Surface((int(self.board_size), int(self.board_size)))
        self.board_img.fill(self.BOARD_COLOR)
    
    def draw_title_screen(self):
        """タイトル画面の描画"""
        # 背景をクリア
        self.screen.fill((0, 0, 0))  # 一度画面を黒でクリア
        # 背景
        self.screen.blit(self.background_img, (0, 0))
        
        # タイトル
        title_text = self.title_font.render("GOGO囲碁", True, self.BLACK)
        self.screen.blit(title_text, (self.width // 2 - title_text.get_width() // 2, self.height * 0.2))
        
        if not self.show_glossary:
            # ゲーム説明
            description = [
                "初心者でも陣地の概念を視覚的に理解できる囲碁ゲームです。",
                "石を置くと自分の陣地が色分けされ、どこが良い手かが一目で分かります。"
            ]
            
            for i, line in enumerate(description):
                text = self.medium_font.render(line, True, self.BLACK)
                self.screen.blit(text, (self.width // 2 - text.get_width() // 2, self.height * 0.35 + i * 30))
            
            # スタートボタン
            pygame.draw.rect(self.screen, (200, 200, 200), self.start_button)
            pygame.draw.rect(self.screen, self.BLACK, self.start_button, 2)
            start_text = self.large_font.render("対戦開始", True, self.BLACK)
            self.screen.blit(start_text, (self.start_button.centerx - start_text.get_width() // 2, 
                                        self.start_button.centery - start_text.get_height() // 2))
            
            # 用語集ボタン
            pygame.draw.rect(self.screen, (200, 200, 200), self.glossary_button)
            pygame.draw.rect(self.screen, self.BLACK, self.glossary_button, 2)
            glossary_text = self.large_font.render("用語集", True, self.BLACK)
            self.screen.blit(glossary_text, (self.glossary_button.centerx - glossary_text.get_width() // 2, 
                                        self.glossary_button.centery - glossary_text.get_height() // 2))
        else:
            # 用語集画面
            self.draw_glossary()
            
            # 戻るボタン
            pygame.draw.rect(self.screen, (200, 200, 200), self.back_to_title_button)
            pygame.draw.rect(self.screen, self.BLACK, self.back_to_title_button, 2)
            back_text = self.large_font.render("戻る", True, self.BLACK)
            self.screen.blit(back_text, (self.back_to_title_button.centerx - back_text.get_width() // 2, 
                                        self.back_to_title_button.centery - back_text.get_height() // 2))
    
    def draw_glossary(self):
        """用語集画面の描画"""
        # 用語集タイトル
        glossary_title = self.large_font.render("【囲碁用語集】", True, self.BLACK)
        self.screen.blit(glossary_title, (self.width // 2 - glossary_title.get_width() // 2, self.height * 0.15))
        
        # 用語の定義
        terms = [
            ("確定陣地", "完全に自分の石で囲まれた領域。相手が侵入できない安全な空点。"),
            ("影響圏", "将来的に自分の陣地になりそうな領域。石から1〜2マス以内の空点。"),
            ("争点", "黒と白の両方の影響圏が重なっている場所。重要な戦略ポイント。"),
            ("アタリ", "石または石のグループが取られる一歩手前の状態。呼吸点が1つだけの状態。"),
            ("コウ", "同じ局面が繰り返されるのを防ぐルール。直前に取られた石と同じ場所に石を置けない。"),
            ("呼吸点", "石または石のグループに隣接する空点。呼吸点がなくなると石は取られる。"),
            ("自殺手", "置いた瞬間に自分の石が呼吸点を失って取られてしまう手。禁じ手。"),
            ("眼", "石のグループ内の空点。2つ以上の眼があると、そのグループは生きる。"),
            ("シチョウ", "石を連続してアタリにしていく手筋。逃げる側が盤端に追い詰められると取られる。"),
            ("コミ", "先手（黒）の有利を相殺するために後手（白）に与えられる得点。本ゲームでは3.5目。")
        ]
        
        # 用語を表示
        y_offset = self.height * 0.25
        for term, definition in terms:
            # 用語（太字）
            term_text = self.medium_font.render(term, True, self.BLACK)
            self.screen.blit(term_text, (self.width * 0.15, y_offset))
            
            # 定義（複数行に分割して表示）
            words = definition.split()
            line = ""
            line_height = self.small_font.get_height() + 5
            for word in words:
                test_line = line + word + " "
                test_text = self.small_font.render(test_line, True, self.BLACK)
                if test_text.get_width() > self.width * 0.7:
                    # 行が長すぎる場合は改行
                    text = self.small_font.render(line, True, self.BLACK)
                    self.screen.blit(text, (self.width * 0.25, y_offset + line_height))
                    line = word + " "
                    y_offset += line_height
                else:
                    line = test_line
            
            # 最後の行を表示
            if line:
                text = self.small_font.render(line, True, self.BLACK)
                self.screen.blit(text, (self.width * 0.25, y_offset + line_height))
            
            y_offset += line_height * 2
    
    def draw_game_screen(self, player_turn, ai_thinking):
        """
        ゲーム画面の描画
        
        Args:
            player_turn: プレイヤーの手番かどうか
            ai_thinking: AIが思考中かどうか
        """
        # 背景
        self.screen.blit(self.background_img, (0, 0))
        
        # 優位性グラフの描画（画面上部に配置）
        self.draw_advantage_bar()
        
        # 盤面の描画
        self.draw_board()
        
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
                    pygame.draw.circle(self.screen, color,
                                      (int(self.board_x + self.board_margin + x * self.cell_size),
                                       int(self.board_y + self.board_margin + y * self.cell_size)),
                                      int(self.cell_size * 0.45))
        
        # プレビューの描画
        mouse_pos = pygame.mouse.get_pos()
        board_pos = self.get_board_position(mouse_pos)
        if board_pos:
            x, y = board_pos
            if self.board.is_valid_move(x, y):
                # 半透明の黒石を表示
                s = pygame.Surface((int(self.cell_size * 0.9), int(self.cell_size * 0.9)), pygame.SRCALPHA)
                pygame.draw.circle(s, (0, 0, 0, 128), (int(s.get_width() / 2), int(s.get_height() / 2)), int(self.cell_size * 0.45))
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
        # プレイヤー名
        player_text = self.medium_font.render("プレイヤー（黒）", True, self.BLACK)
        self.screen.blit(player_text, (self.width * 0.1, self.height * 0.2))
        
        # 取った石の数
        captures_text = self.small_font.render(f"取った石: {self.board.black_captures}", True, self.BLACK)
        self.screen.blit(captures_text, (self.width * 0.1, self.height * 0.25))
        
        # 陣地ポイント
        territory_count = sum(sum(self.board.black_territory))
        territory_text = self.small_font.render(f"陣地: {territory_count}", True, self.BLACK)
        self.screen.blit(territory_text, (self.width * 0.1, self.height * 0.3))
        
        # 合計得点
        total_score = self.board.calculate_score(Board.BLACK)
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
        # AI名
        ai_text = self.medium_font.render("AI（白）", True, self.BLACK)
        self.screen.blit(ai_text, (self.width * 0.8, self.height * 0.2))
        
        # 取った石の数
        captures_text = self.small_font.render(f"取った石: {self.board.white_captures}", True, self.BLACK)
        self.screen.blit(captures_text, (self.width * 0.8, self.height * 0.25))
        
        # 陣地ポイント
        territory_count = sum(sum(self.board.white_territory))
        territory_text = self.small_font.render(f"陣地: {territory_count}", True, self.BLACK)
        self.screen.blit(territory_text, (self.width * 0.8, self.height * 0.3))
        
        # コミ
        komi_text = self.small_font.render("コミ: 3.5", True, self.BLACK)
        self.screen.blit(komi_text, (self.width * 0.8, self.height * 0.35))
        
        # 合計得点
        total_score = self.board.calculate_score(Board.WHITE) + 3.5  # コミを加算
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
        
        # 結果タイトル
        result_text = self.large_font.render("対局結果", True, self.BLACK)
        self.screen.blit(result_text, (self.width // 2 - result_text.get_width() // 2, self.height * 0.2))
        
        # プレイヤーの得点
        black_score = self.board.calculate_score(Board.BLACK)
        black_text = self.medium_font.render(f"プレイヤー（黒）: {self.board.black_captures} + {sum(sum(self.board.black_territory))} = {black_score}", True, self.BLACK)
        self.screen.blit(black_text, (self.width // 2 - black_text.get_width() // 2, self.height * 0.3))
        
        # AIの得点
        white_score = self.board.calculate_score(Board.WHITE) + 3.5  # コミを加算
        white_text = self.medium_font.render(f"AI（白）: {self.board.white_captures} + {sum(sum(self.board.white_territory))} + 3.5 = {white_score}", True, self.BLACK)
        self.screen.blit(white_text, (self.width // 2 - white_text.get_width() // 2, self.height * 0.35))
        
        # 勝敗結果
        if self.board.winner == Board.BLACK:
            result = "プレイヤーの勝利！"
        elif self.board.winner == Board.WHITE:
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
            if current_time - self.popup_timer < 2000:  # 2秒間表示
                # 半透明の背景
                popup_surface = pygame.Surface((300, 50), pygame.SRCALPHA)
                popup_surface.fill((0, 0, 0, 180))
                
                # メッセージテキスト
                message_text = self.medium_font.render(self.popup_message, True, self.WHITE)
                popup_surface.blit(message_text, (150 - message_text.get_width() // 2, 25 - message_text.get_height() // 2))
                
                # 画面中央に表示
                self.screen.blit(popup_surface, (self.width // 2 - 150, self.height // 2 - 25))
            else:
                self.popup_message = None
    def is_glossary_button_clicked(self, pos):
        """
        用語集ボタンがクリックされたかどうかを判定
        
        Args:
            pos: クリック位置の座標
            
        Returns:
            bool: ボタンがクリックされたかどうか
        """
        return self.glossary_button.collidepoint(pos)
    def draw_advantage_bar(self):
        """優位性を示す横棒グラフを描画"""
        # グラフの位置とサイズ
        bar_width = self.width * 0.6
        bar_height = 30
        bar_x = self.width * 0.2
        bar_y = self.height * 0.1  # 画面上部に配置
        
        # 黒と白の得点を計算（コミを含む）
        black_score = self.board.calculate_score(Board.BLACK)
        white_score = self.board.calculate_score(Board.WHITE) + 3.5  # コミを加算
        
        # 総得点
        total_score = black_score + white_score
        if total_score == 0:  # 0除算を防ぐ
            black_ratio = 0.5
        else:
            black_ratio = black_score / total_score
        
        # 黒の部分の幅を計算
        black_width = bar_width * black_ratio
        
        # 背景（枠）を描画
        pygame.draw.rect(self.screen, (200, 200, 200), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(self.screen, self.BLACK, (bar_x, bar_y, bar_width, bar_height), 2)
        
        # 黒側（左側）
        pygame.draw.rect(self.screen, (0, 0, 0, 200), (bar_x, bar_y, black_width, bar_height))
        
        # 白側（右側）
        pygame.draw.rect(self.screen, (255, 255, 255, 200), (bar_x + black_width, bar_y, bar_width - black_width, bar_height))
        
        # 中央線
        pygame.draw.line(self.screen, (100, 100, 100), 
                         (bar_x + bar_width / 2, bar_y), 
                         (bar_x + bar_width / 2, bar_y + bar_height), 2)
        
        # パーセンテージ表示
        black_percent = int(black_ratio * 100)
        white_percent = 100 - black_percent
        
        # 黒のパーセンテージ
        black_text = self.small_font.render(f"{black_percent}%", True, self.WHITE)
        if black_width > black_text.get_width() + 10:  # 十分なスペースがある場合
            self.screen.blit(black_text, (bar_x + 10, bar_y + bar_height/2 - black_text.get_height()/2))
        
        # 白のパーセンテージ
        white_text = self.small_font.render(f"{white_percent}%", True, self.BLACK)
        if bar_width - black_width > white_text.get_width() + 10:  # 十分なスペースがある場合
            self.screen.blit(white_text, (bar_x + black_width + 10, bar_y + bar_height/2 - white_text.get_height()/2))
        
        # 優位性の説明テキスト
        advantage_text = self.small_font.render("優位性", True, self.BLACK)
        self.screen.blit(advantage_text, (bar_x, bar_y - 25))
        
        # プレイヤーとAIのラベル
        player_text = self.small_font.render("プレイヤー", True, self.BLACK)
        self.screen.blit(player_text, (bar_x, bar_y + bar_height + 5))
        
        ai_text = self.small_font.render("AI", True, self.BLACK)
        self.screen.blit(ai_text, (bar_x + bar_width - ai_text.get_width(), bar_y + bar_height + 5))
