import random
import numpy as np
import sys
from .board import Board

class AI:
    """
    囲碁AIクラス。
    囲碁検定5級レベルの思考ロジックを実装。
    """
    
    def __init__(self, board):
        """
        AIの初期化
        
        Args:
            board: 盤面オブジェクト
        """
        self.board = board
    
    def get_move(self):
        """
        次の一手を決定する
        
        Returns:
            tuple or None: 石を置く座標 (x, y) またはパスの場合はNone
        """
        # 有効な手の候補を列挙
        valid_moves = []
        for y in range(self.board.size):
            for x in range(self.board.size):
                if self.board.is_valid_move(x, y):
                    valid_moves.append((x, y))
        
        # 有効な手がない場合はパス
        if not valid_moves:
            print("AIは有効な手がないためパスします")
            return None  # パス
        
        # 各手の評価値を計算
        move_scores = {}
        for move in valid_moves:
            score = self.evaluate_move(move)
            move_scores[move] = score
        
        # 最も評価値の高い手を選択（同点の場合はランダム）
        best_score = max(move_scores.values())
        best_moves = [move for move, score in move_scores.items() if score == best_score]
        
        # 最善手を選択
        best_move = random.choice(best_moves)
        print(f"AIは ({best_move[0]}, {best_move[1]}) に石を置きます")
        
        # 稀にパスする（デバッグ用）
        # if random.random() < 0.05:  # 5%の確率でパス
        #     print("AIはランダムにパスします")
        #     return None
            
        return best_move
    
    def evaluate_move(self, move):
        """
        指定した手の評価値を計算
        
        Args:
            move: 手の座標 (x, y)
            
        Returns:
            float: 評価値（高いほど良い手）
        """
        x, y = move
        score = 0
        
        # AIは常に白石
        ai_stone = Board.WHITE
        opponent_stone = Board.BLACK
        
        # 一時的に石を置いてみる
        temp_board = self.board.board.copy()
        temp_board[y, x] = ai_stone
        
        # 1. アタリの処理（相手の石を取れる場合は高評価）
        captured = self.count_potential_captures(x, y, ai_stone, opponent_stone)
        score += captured * 10
        
        # 2. 自分の石がアタリにならないようにする
        if self.is_self_atari(x, y, ai_stone):
            score -= 5
        
        # 3. 陣地の拡大（影響圏の増加）
        influence_gain = self.calculate_influence_gain(x, y)
        score += influence_gain * 3
        
        # 4. 相手の陣地侵略
        invasion_value = self.calculate_invasion_value(x, y)
        score += invasion_value * 2
        
        # 5. 基本的な配石（序盤は3線、4線を重視）
        position_value = self.evaluate_position(x, y)
        score += position_value
        
        # 6. ランダム性を少し加える（同じような状況で常に同じ手を打たないように）
        score += random.uniform(0, 0.5)
        
        return score
    
    def count_potential_captures(self, x, y, ai_stone=None, opponent_stone=None):
        """
        指定した位置に石を置いた場合に取れる相手の石の数を計算
        
        Args:
            x, y: 石を置く位置の座標
            ai_stone: AIの石の色 (デフォルト: Board.WHITE)
            opponent_stone: 相手の石の色 (デフォルト: Board.BLACK)
            
        Returns:
            int: 取れる石の数
        """
        # デフォルト値の設定
        if ai_stone is None:
            ai_stone = Board.WHITE
        if opponent_stone is None:
            opponent_stone = Board.BLACK
            
        # 一時的に石を置いてみる
        temp_board = self.board.board.copy()
        temp_board[y, x] = ai_stone
        
        captured_count = 0
        
        # 隣接する4方向をチェック
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.board.size and 0 <= ny < self.board.size and self.board.board[ny, nx] == opponent_stone:
                group = self.board.find_group(nx, ny)
                
                # この手を打った後にこのグループが呼吸点を持つかチェック
                has_liberty = False
                for gx, gy in group:
                    for gdx, gdy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                        ngx, ngy = gx + gdx, gy + gdy
                        if 0 <= ngx < self.board.size and 0 <= ngy < self.board.size:
                            if (ngx, ngy) != (x, y) and self.board.board[ngy, ngx] == Board.EMPTY:
                                has_liberty = True
                                break
                    if has_liberty:
                        break
                
                if not has_liberty:
                    captured_count += len(group)
        
        return captured_count
    
    def is_self_atari(self, x, y, ai_stone=None):
        """
        指定した位置に石を置くと自分の石がアタリになるかどうかを判定
        
        Args:
            x, y: 石を置く位置の座標
            ai_stone: AIの石の色 (デフォルト: Board.WHITE)
            
        Returns:
            bool: 自分の石がアタリになるかどうか
        """
        # デフォルト値の設定
        if ai_stone is None:
            ai_stone = Board.WHITE
            
        # 一時的に石を置いてみる
        temp_board = self.board.board.copy()
        temp_board[y, x] = ai_stone
        
        # 隣接する自分の石のグループを見つける
        adjacent_groups = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.board.size and 0 <= ny < self.board.size and self.board.board[ny, nx] == ai_stone:
                group = self.board.find_group(nx, ny)
                if group not in adjacent_groups:
                    adjacent_groups.append(group)
        
        # 自分の石を含むグループを追加
        self_group = [(x, y)]
        for group in adjacent_groups:
            self_group.extend(group)
        
        # このグループが呼吸点を1つしか持たないかチェック
        liberty_count = 0
        for gx, gy in self_group:
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = gx + dx, gy + dy
                if 0 <= nx < self.board.size and 0 <= ny < self.board.size and self.board.board[ny, nx] == Board.EMPTY:
                    liberty_count += 1
                    if liberty_count > 1:
                        return False
        
        return liberty_count <= 1
    
    def calculate_influence_gain(self, x, y):
        """
        指定した位置に石を置いた場合の影響圏の増加量を計算
        
        Args:
            x, y: 石を置く位置の座標
            
        Returns:
            int: 影響圏の増加量
        """
        # AIは常に白石
        ai_stone = Board.WHITE
        
        # 現在の影響圏の面積
        current_influence = np.sum(self.board.white_influence)
        
        # 一時的に石を置いてみる
        self.board.update_preview(x, y)
        
        # 石を置いた後の影響圏の面積
        if self.board.preview_board is not None:
            new_influence = np.sum(self.board.preview_white_influence)
            
            # プレビューをクリア
            self.board.preview_board = None
            self.board.preview_black_territory = None
            self.board.preview_white_territory = None
            self.board.preview_black_influence = None
            self.board.preview_white_influence = None
            
            return new_influence - current_influence
        
        return 0
    
    def calculate_invasion_value(self, x, y):
        """
        指定した位置に石を置いた場合の相手の陣地侵略の価値を計算
        
        Args:
            x, y: 石を置く位置の座標
            
        Returns:
            int: 侵略の価値
        """
        # AIは常に白石、相手は常に黒石
        ai_stone = Board.WHITE
        opponent_stone = Board.BLACK
        
        # 相手の影響圏かどうかをチェック
        opponent_influence = self.board.black_influence
        
        if opponent_influence[y, x]:
            # 相手の影響圏内なら高評価
            return 5
        
        # 相手の石に近いほど高評価
        min_dist = float('inf')
        for cy in range(self.board.size):
            for cx in range(self.board.size):
                if self.board.board[cy, cx] == opponent_stone:
                    dist = abs(x - cx) + abs(y - cy)  # マンハッタン距離
                    min_dist = min(min_dist, dist)
        
        if min_dist <= 2:
            return 3
        elif min_dist <= 4:
            return 1
        
        return 0
    
    def evaluate_position(self, x, y):
        """
        指定した位置の基本的な評価値を計算
        
        Args:
            x, y: 石を置く位置の座標
            
        Returns:
            float: 評価値
        """
        size = self.board.size
        center = size // 2
        
        # 盤面の進行度を計算
        stones_count = np.sum(self.board.board != Board.EMPTY)
        progress = stones_count / (size * size)
        
        # 序盤（進行度30%未満）
        if progress < 0.3:
            # 序盤は3線、4線を重視
            line = min(x, y, size-1-x, size-1-y)
            if line == 2 or line == 3:  # 3線、4線
                return 3
            elif line == 1:  # 2線
                return 1
            elif line == 0:  # 1線（端）
                return 0
            else:  # 中央
                return 2
        
        # 中盤（進行度30%～70%）
        elif progress < 0.7:
            # 中盤は中央を重視
            dist_from_center = abs(x - center) + abs(y - center)
            return max(0, 4 - dist_from_center)
        
        # 終盤（進行度70%以上）
        else:
            # 終盤は相手の影響圏への侵入を重視
            # AIは常に白石、相手は常に黒石
            ai_stone = Board.WHITE
            opponent_stone = Board.BLACK
            
            # 相手の影響圏かどうかをチェック
            opponent_influence = self.board.black_influence
            
            if opponent_influence[y, x]:
                return 4
            
            return 1
