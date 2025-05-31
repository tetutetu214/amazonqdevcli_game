import random
import numpy as np
from board import Board

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
        
        if not valid_moves:
            return None  # パス
        
        # 各手の評価値を計算
        move_scores = {}
        for move in valid_moves:
            score = self.evaluate_move(move)
            move_scores[move] = score
        
        # 最も評価値の高い手を選択（同点の場合はランダム）
        best_score = max(move_scores.values())
        best_moves = [move for move, score in move_scores.items() if score == best_score]
        
        return random.choice(best_moves)
    
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
        
        # 一時的に石を置いてみる
        temp_board = self.board.board.copy()
        temp_board[y, x] = Board.WHITE
        
        # 1. アタリの処理（相手の石を取れる場合は高評価）
        captured = self.count_potential_captures(x, y)
        score += captured * 10
        
        # 2. 自分の石がアタリにならないようにする
        if self.is_self_atari(x, y):
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
    
    def count_potential_captures(self, x, y):
        """
        指定した位置に石を置いた場合に取れる相手の石の数を計算
        
        Args:
            x, y: 石を置く位置の座標
            
        Returns:
            int: 取れる石の数
        """
        # 一時的に石を置いてみる
        temp_board = self.board.board.copy()
        temp_board[y, x] = Board.WHITE
        
        captured_count = 0
        
        # 隣接する4方向をチェック
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.board.size and 0 <= ny < self.board.size and self.board.board[ny, nx] == Board.BLACK:
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
    
    def is_self_atari(self, x, y):
        """
        指定した位置に石を置くと自分の石がアタリになるかどうかを判定
        
        Args:
            x, y: 石を置く位置の座標
            
        Returns:
            bool: 自分の石がアタリになるかどうか
        """
        # 一時的に石を置いてみる
        temp_board = self.board.board.copy()
        temp_board[y, x] = Board.WHITE
        
        # 隣接する自分の石のグループを見つける
        adjacent_groups = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.board.size and 0 <= ny < self.board.size and self.board.board[ny, nx] == Board.WHITE:
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
        # 現在の影響圏の面積
        current_influence = np.sum(self.board.white_influence)
        
        # 一時的に石を置いてみる
        temp_board = self.board.board.copy()
        temp_board[y, x] = Board.WHITE
        
        # 新しい影響圏を計算
        new_influence = 0
        for ny in range(self.board.size):
            for nx in range(self.board.size):
                if temp_board[ny, nx] == Board.EMPTY:
                    # 白石からの距離を計算
                    min_dist_white = float('inf')
                    for cy in range(self.board.size):
                        for cx in range(self.board.size):
                            if temp_board[cy, cx] == Board.WHITE:
                                dist = abs(nx - cx) + abs(ny - cy)  # マンハッタン距離
                                min_dist_white = min(min_dist_white, dist)
                    
                    # 黒石からの距離を計算
                    min_dist_black = float('inf')
                    for cy in range(self.board.size):
                        for cx in range(self.board.size):
                            if temp_board[cy, cx] == Board.BLACK:
                                dist = abs(nx - cx) + abs(ny - cy)  # マンハッタン距離
                                min_dist_black = min(min_dist_black, dist)
                    
                    # 影響圏の判定（距離が2以下で、かつ相手より近い）
                    if min_dist_white <= 2 and (min_dist_white < min_dist_black or min_dist_black > 2):
                        new_influence += 1
        
        return new_influence - current_influence
    
    def calculate_invasion_value(self, x, y):
        """
        指定した位置に石を置いた場合の相手の陣地侵略価値を計算
        
        Args:
            x, y: 石を置く位置の座標
            
        Returns:
            int: 侵略価値
        """
        # 相手の影響圏内かどうかをチェック
        if self.board.black_influence[y, x]:
            return 5
        
        # 相手の確定陣地の近くかどうかをチェック
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.board.size and 0 <= ny < self.board.size and self.board.black_territory[ny, nx]:
                return 3
        
        return 0
    
    def evaluate_position(self, x, y):
        """
        指定した位置の基本的な評価値を計算
        
        Args:
            x, y: 石を置く位置の座標
            
        Returns:
            float: 評価値
        """
        # 盤面の中心からの距離
        center = self.board.size // 2
        distance_from_center = abs(x - center) + abs(y - center)
        
        # 3線、4線の価値
        line_x = min(x, self.board.size - 1 - x)
        line_y = min(y, self.board.size - 1 - y)
        
        # 9路盤の場合、2線と3線を重視
        if self.board.size == 9:
            if line_x == 1 or line_y == 1:  # 2線
                line_value = 1.5
            elif line_x == 2 or line_y == 2:  # 3線
                line_value = 2.0
            else:  # その他
                line_value = 1.0
        else:
            # 19路盤などの場合は3線、4線を重視
            if line_x == 2 or line_y == 2:  # 3線
                line_value = 2.0
            elif line_x == 3 or line_y == 3:  # 4線
                line_value = 1.8
            else:  # その他
                line_value = 1.0
        
        # 星の位置（天元）は特に価値が高い
        if x == center and y == center:
            star_value = 1.5
        # 9路盤の場合、四隅の星の位置
        elif self.board.size == 9 and ((x == 2 and y == 2) or (x == 2 and y == 6) or (x == 6 and y == 2) or (x == 6 and y == 6)):
            star_value = 1.3
        else:
            star_value = 1.0
        
        # 盤面の中心に近いほど価値が高い（ただし、線の価値も考慮）
        center_value = 1.0 - (distance_from_center / (self.board.size * 2))
        
        return line_value * star_value * center_value * 3
