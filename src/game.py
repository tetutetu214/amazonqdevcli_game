# -*- coding: utf-8 -*-
import pygame
import sys
from .board import Board
from .ai import AI
from .ui import UI

class Game:
    """
    ゲームのメインクラス。ゲームの状態管理と画面遷移を担当。
    """
    # ゲーム状態の定義
    STATE_TITLE = 0
    STATE_GAME = 1
    STATE_RESULT = 2

    def __init__(self):
        """ゲームの初期化"""
        pygame.init()
        self.screen_width = 1200
        self.screen_height = 700
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        
        # 日本語対応のタイトル設定
        pygame.display.set_caption("GOGO 囲碁")
        
        self.clock = pygame.time.Clock()
        self.state = Game.STATE_TITLE
        
        # ゲームコンポーネントの初期化
        self.board = Board()
        self.ai = AI(self.board)
        self.ui = UI(self.screen, self.board)
        
        # ゲーム状態変数
        self.player_turn = True  # True: プレイヤー(黒), False: AI(白)
        self.player_is_black = True  # プレイヤーは常に黒石（先手）
        self.consecutive_passes = 0
        self.ai_thinking = False
        self.ai_think_start_time = 0
        
    def run(self):
        """ゲームのメインループ"""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                self.handle_event(event)
            
            self.update()
            self.render()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()
    
    def handle_event(self, event):
        """イベント処理"""
        if self.state == Game.STATE_TITLE:
            self.handle_title_event(event)
        elif self.state == Game.STATE_GAME:
            self.handle_game_event(event)
        elif self.state == Game.STATE_RESULT:
            self.handle_result_event(event)
    
    def handle_title_event(self, event):
        """タイトル画面のイベント処理"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            # ゲーム開始ボタンがクリックされたかチェック
            if self.ui.is_black_button_clicked(event.pos):
                self.state = Game.STATE_GAME
                self.player_is_black = True  # プレイヤーは常に黒（先手）
                self.player_turn = True
                self.reset_game()
    
    def handle_game_event(self, event):
        """ゲーム画面のイベント処理"""
        if not self.player_turn or self.ai_thinking:
            return
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            # 盤面上の位置を取得
            board_pos = self.ui.get_board_position(event.pos)
            if board_pos:
                x, y = board_pos
                # 石を置く
                if self.board.is_valid_move(x, y):
                    player_stone = Board.BLACK  # プレイヤーは常に黒石
                    self.board.place_stone(x, y, player_stone)
                    self.ui.set_last_move(x, y)  # 最後の手を記録
                    self.consecutive_passes = 0
                    self.player_turn = False
                    self.ai_thinking = True
                    self.ai_think_start_time = pygame.time.get_ticks()
                else:
                    # 禁手ガイド表示
                    self.ui.show_invalid_move_guide(x, y)
            
            # パスボタンがクリックされたかチェック
            elif self.ui.is_pass_button_clicked(event.pos):
                print("プレイヤーがパスしました")
                self.consecutive_passes += 1
                print(f"連続パス数: {self.consecutive_passes}")
                self.ui.show_popup_message("プレイヤーがパスしました")
                
                # ゲーム終了条件を確認
                if self.check_game_end():
                    print("連続パスによりゲーム終了")
                    return  # ゲームが終了した場合は処理を終了
                
                # ゲームが続行する場合のみAIターンに変更
                self.player_turn = False
                self.ai_thinking = True
                self.ai_think_start_time = pygame.time.get_ticks()
            
            # 投了ボタンがクリックされたかチェック
            elif self.ui.is_resign_button_clicked(event.pos):
                self.state = Game.STATE_RESULT
                # プレイヤーが投了したので、AIの勝利
                self.board.winner = Board.WHITE if self.player_is_black else Board.BLACK
    
    def handle_result_event(self, event):
        """結果画面のイベント処理"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            # もう一度プレイボタンがクリックされたかチェック
            if self.ui.is_play_again_button_clicked(event.pos):
                self.state = Game.STATE_GAME
                self.reset_game()
            # タイトルに戻るボタンがクリックされたかチェック
            elif self.ui.is_back_to_title_button_clicked(event.pos):
                self.state = Game.STATE_TITLE
    
    def update(self):
        """ゲーム状態の更新"""
        if self.state == Game.STATE_GAME:
            # AIの思考処理
            if self.ai_thinking:
                # 0.5秒の思考時間を演出
                current_time = pygame.time.get_ticks()
                if current_time - self.ai_think_start_time >= 500:
                    self.ai_thinking = False
                    self.ai_move()
            
            # マウスホバー時のプレビュー更新
            if self.player_turn and not self.ai_thinking:
                mouse_pos = pygame.mouse.get_pos()
                board_pos = self.ui.get_board_position(mouse_pos)
                if board_pos:
                    self.board.update_preview(*board_pos)
            
            # ステータスバーの更新（常に更新）
            self.board.update_territories()
            
            # デバッグ情報（コンソールに連続パス数を表示）
            if self.consecutive_passes > 0:
                print(f"連続パス数: {self.consecutive_passes}")
                
            # 連続パスのチェック（念のため毎フレーム確認）
            if self.consecutive_passes >= 2:
                self.check_game_end()
    
    def ai_move(self):
        """AIの手を処理"""
        move = self.ai.get_move()
        if move:
            x, y = move
            ai_stone = Board.WHITE  # AIは常に白石
            self.board.place_stone(x, y, ai_stone)
            self.ui.set_last_move(x, y)  # 最後の手を記録
            self.consecutive_passes = 0
        else:
            # AIがパスする場合
            self.consecutive_passes += 1
            print(f"AIがパスしました。連続パス数: {self.consecutive_passes}")
            # AIがパスしたことをポップアップで表示
            self.ui.show_popup_message("AIがパスしました")
        
        # ゲーム終了条件を確認
        if self.check_game_end():
            print("ゲーム終了条件を満たしました")
            return  # ゲームが終了した場合は処理を終了
        
        # ゲームが続行する場合のみプレイヤーターンに変更
        self.player_turn = True
    
    def check_game_end(self):
        """ゲーム終了条件のチェック"""
        if self.consecutive_passes >= 2:
            print(f"連続パス数が{self.consecutive_passes}に達したため、ゲーム終了")
            self.ui.show_popup_message("連続パスによりゲーム終了")
            self.state = Game.STATE_RESULT
            # 勝敗判定
            black_score = self.board.calculate_score(Board.BLACK)
            white_score = self.board.calculate_score(Board.WHITE) + 3.5  # コミ
            
            print(f"黒の得点: {black_score}")
            print(f"白の得点: {white_score} (コミ3.5含む)")
            
            # 正確に比較して勝者を決定
            if black_score > white_score:
                self.board.winner = Board.BLACK
                print(f"黒の勝利: 黒={black_score} > 白={white_score}")
            else:
                self.board.winner = Board.WHITE
                print(f"白の勝利: 黒={black_score} <= 白={white_score}")
            
            # 明示的にプレイヤーターンをFalseにして、AIの思考を停止
            self.player_turn = False
            self.ai_thinking = False
            
            return True  # ゲーム終了を明示的に返す
        return False  # ゲーム継続
    
    def render(self):
        """画面描画"""
        if self.state == Game.STATE_TITLE:
            self.ui.draw_title_screen()
        elif self.state == Game.STATE_GAME:
            self.ui.draw_game_screen(self.player_turn, self.ai_thinking)
        elif self.state == Game.STATE_RESULT:
            self.ui.draw_result_screen()
    
    def reset_game(self):
        """ゲームのリセット"""
        self.board.reset()
        self.ui.last_move = None  # 最後の手をリセット
        
        # プレイヤーは常に黒（先手）
        self.player_turn = True
        self.player_is_black = True
            
        self.consecutive_passes = 0

if __name__ == "__main__":
    game = Game()
    game.run()
