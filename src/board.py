# -*- coding: utf-8 -*-
import numpy as np
from collections import deque

class Board:
    """
    囲碁の盤面を管理するクラス。
    石の配置、陣地計算、ルール判定などを担当。
    """
    # 盤面の状態定数
    EMPTY = 0
    BLACK = 1
    WHITE = 2
    
    # 勝敗結果
    DRAW = 0
    
    def __init__(self, size=9):
        """
        盤面の初期化
        
        Args:
            size: 盤面のサイズ（デフォルト: 9x9）
        """
        self.size = size
        self.reset()
    
    def reset(self):
        """盤面をリセット"""
        # 盤面の状態（0: 空, 1: 黒, 2: 白）
        self.board = np.zeros((self.size, self.size), dtype=int)
        
        # 陣地情報
        self.black_territory = np.zeros((self.size, self.size), dtype=bool)  # 確定陣地
        self.white_territory = np.zeros((self.size, self.size), dtype=bool)  # 確定陣地
        self.black_influence = np.zeros((self.size, self.size), dtype=bool)  # 影響圏
        self.white_influence = np.zeros((self.size, self.size), dtype=bool)  # 影響圏
        
        # 取った石のカウント
        self.black_captures = 0
        self.white_captures = 0
        
        # コウの位置（前の手で取られた単一の石の位置）
        self.ko = None
        
        # プレビュー用の一時的な盤面
        self.preview_board = None
        self.preview_black_territory = None
        self.preview_white_territory = None
        self.preview_black_influence = None
        self.preview_white_influence = None
        
        # 勝者
        self.winner = None
    
    def place_stone(self, x, y, color):
        """
        指定した位置に石を置く
        
        Args:
            x, y: 石を置く位置の座標
            color: 石の色（BLACK or WHITE）
            
        Returns:
            bool: 石を置くことができたかどうか
        """
        if not self.is_valid_move(x, y):
            return False
        
        # 石を置く
        self.board[y, x] = color
        
        # 相手の石を取る
        opponent = Board.WHITE if color == Board.BLACK else Board.BLACK
        captured = []
        
        # 隣接する4方向をチェック
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.size and 0 <= ny < self.size and self.board[ny, nx] == opponent:
                group = self.find_group(nx, ny)
                if not self.has_liberty(group):
                    # 石を取る
                    for gx, gy in group:
                        self.board[gy, gx] = Board.EMPTY
                        captured.append((gx, gy))
        
        # 自殺手のチェック
        group = self.find_group(x, y)
        if not self.has_liberty(group):
            # 自分の石を元に戻す
            self.board[y, x] = Board.EMPTY
            return False
        
        # コウのルール更新
        if len(captured) == 1 and len(group) == 1:
            self.ko = captured[0]
        else:
            self.ko = None
        
        # 取った石のカウントを更新
        if color == Board.BLACK:
            self.black_captures += len(captured)
        else:
            self.white_captures += len(captured)
        
        # 陣地情報を更新
        self.update_territories()
        
        return True
    
    def is_valid_move(self, x, y):
        """
        指定した位置に石を置けるかどうかを判定
        
        Args:
            x, y: 石を置く位置の座標
            
        Returns:
            bool: 石を置けるかどうか
        """
        # 盤外チェック
        if not (0 <= x < self.size and 0 <= y < self.size):
            return False
        
        # 空点チェック
        if self.board[y, x] != Board.EMPTY:
            return False
        
        # コウのルールチェック
        if self.ko == (x, y):
            return False
        
        return True
    
    def find_group(self, x, y):
        """
        指定した位置の石と繋がっている石のグループを取得
        
        Args:
            x, y: 石の位置の座標
            
        Returns:
            list: グループに属する石の座標のリスト
        """
        color = self.board[y, x]
        if color == Board.EMPTY:
            return []
        
        group = []
        visited = np.zeros((self.size, self.size), dtype=bool)
        queue = deque([(x, y)])
        visited[y, x] = True
        
        while queue:
            cx, cy = queue.popleft()
            group.append((cx, cy))
            
            # 隣接する4方向をチェック
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < self.size and 0 <= ny < self.size and not visited[ny, nx] and self.board[ny, nx] == color:
                    queue.append((nx, ny))
                    visited[ny, nx] = True
        
        return group
    
    def has_liberty(self, group):
        """
        指定したグループが呼吸点（自由点）を持っているかどうかを判定
        
        Args:
            group: 石のグループ（座標のリスト）
            
        Returns:
            bool: 呼吸点があるかどうか
        """
        for x, y in group:
            # 隣接する4方向をチェック
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.size and 0 <= ny < self.size and self.board[ny, nx] == Board.EMPTY:
                    return True
        return False
    
    def update_territories(self):
        """陣地情報を更新"""
        # 確定陣地の計算
        self.black_territory, self.white_territory = self.calculate_territories()
        
        # 影響圏の計算
        self.black_influence, self.white_influence = self.calculate_influence()
    
    def calculate_territories(self):
        """
        確定陣地を計算
        
        Returns:
            tuple: (黒の確定陣地, 白の確定陣地)
        """
        black_territory = np.zeros((self.size, self.size), dtype=bool)
        white_territory = np.zeros((self.size, self.size), dtype=bool)
        
        # 空点ごとに、それが誰の陣地かを判定
        for y in range(self.size):
            for x in range(self.size):
                if self.board[y, x] != Board.EMPTY:
                    continue
                
                # この空点が誰に囲まれているかを判定
                surrounded_by_black = True
                surrounded_by_white = True
                
                # 連結している空点のグループを取得
                empty_group = self.find_empty_group(x, y)
                
                # このグループの境界をチェック
                for ex, ey in empty_group:
                    for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                        nx, ny = ex + dx, ey + dy
                        if 0 <= nx < self.size and 0 <= ny < self.size:
                            if self.board[ny, nx] == Board.BLACK:
                                surrounded_by_white = False
                            elif self.board[ny, nx] == Board.WHITE:
                                surrounded_by_black = False
                
                # 確定陣地として登録
                if surrounded_by_black and not surrounded_by_white:
                    for ex, ey in empty_group:
                        black_territory[ey, ex] = True
                elif surrounded_by_white and not surrounded_by_black:
                    for ex, ey in empty_group:
                        white_territory[ey, ex] = True
        
        return black_territory, white_territory
    
    def find_empty_group(self, x, y):
        """
        指定した位置の空点と繋がっている空点のグループを取得
        
        Args:
            x, y: 空点の位置の座標
            
        Returns:
            list: グループに属する空点の座標のリスト
        """
        if self.board[y, x] != Board.EMPTY:
            return []
        
        group = []
        visited = np.zeros((self.size, self.size), dtype=bool)
        queue = deque([(x, y)])
        visited[y, x] = True
        
        while queue:
            cx, cy = queue.popleft()
            group.append((cx, cy))
            
            # 隣接する4方向をチェック
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < self.size and 0 <= ny < self.size and not visited[ny, nx] and self.board[ny, nx] == Board.EMPTY:
                    queue.append((nx, ny))
                    visited[ny, nx] = True
        
        return group
    
    def calculate_influence(self):
        """
        影響圏を計算
        
        Returns:
            tuple: (黒の影響圏, 白の影響圏)
        """
        black_influence = np.zeros((self.size, self.size), dtype=bool)
        white_influence = np.zeros((self.size, self.size), dtype=bool)
        
        # 各石から1~2マス以内の空点を影響圏とする
        for y in range(self.size):
            for x in range(self.size):
                if self.board[y, x] == Board.EMPTY:
                    # 黒石からの距離を計算
                    min_dist_black = self.calculate_min_distance(x, y, Board.BLACK)
                    # 白石からの距離を計算
                    min_dist_white = self.calculate_min_distance(x, y, Board.WHITE)
                    
                    # 影響圏の判定（距離が2以下で、かつ相手より近い）
                    if min_dist_black <= 2 and (min_dist_black < min_dist_white or min_dist_white > 2):
                        black_influence[y, x] = True
                    if min_dist_white <= 2 and (min_dist_white < min_dist_black or min_dist_black > 2):
                        white_influence[y, x] = True
        
        return black_influence, white_influence
    
    def calculate_min_distance(self, x, y, color):
        """
        指定した位置から最も近い指定色の石までの距離を計算
        
        Args:
            x, y: 位置の座標
            color: 石の色
            
        Returns:
            int: 最小距離（石がない場合は無限大）
        """
        min_dist = float('inf')
        
        for cy in range(self.size):
            for cx in range(self.size):
                if self.board[cy, cx] == color:
                    dist = abs(x - cx) + abs(y - cy)  # マンハッタン距離
                    min_dist = min(min_dist, dist)
        
        return min_dist
    
    def update_preview(self, x, y):
        """
        プレビュー用の一時的な盤面を更新
        
        Args:
            x, y: プレビュー位置の座標
        """
        if not self.is_valid_move(x, y):
            self.preview_board = None
            return
        
        # 現在の盤面をコピー
        self.preview_board = self.board.copy()
        self.preview_board[y, x] = Board.BLACK
        
        # プレビュー用の陣地計算
        preview_black_territory, preview_white_territory = self.calculate_preview_territories()
        preview_black_influence, preview_white_influence = self.calculate_preview_influence()
        
        self.preview_black_territory = preview_black_territory
        self.preview_white_territory = preview_white_territory
        self.preview_black_influence = preview_black_influence
        self.preview_white_influence = preview_white_influence
    
    def calculate_preview_territories(self):
        """
        プレビュー用の確定陣地を計算
        
        Returns:
            tuple: (黒の確定陣地, 白の確定陣地)
        """
        # プレビュー盤面がない場合は現在の陣地を返す
        if self.preview_board is None:
            return self.black_territory, self.white_territory
        
        black_territory = np.zeros((self.size, self.size), dtype=bool)
        white_territory = np.zeros((self.size, self.size), dtype=bool)
        
        # 空点ごとに、それが誰の陣地かを判定
        for y in range(self.size):
            for x in range(self.size):
                if self.preview_board[y, x] != Board.EMPTY:
                    continue
                
                # この空点が誰に囲まれているかを判定
                surrounded_by_black = True
                surrounded_by_white = True
                
                # 連結している空点のグループを取得
                empty_group = self.find_preview_empty_group(x, y)
                
                # このグループの境界をチェック
                for ex, ey in empty_group:
                    for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                        nx, ny = ex + dx, ey + dy
                        if 0 <= nx < self.size and 0 <= ny < self.size:
                            if self.preview_board[ny, nx] == Board.BLACK:
                                surrounded_by_white = False
                            elif self.preview_board[ny, nx] == Board.WHITE:
                                surrounded_by_black = False
                
                # 確定陣地として登録
                if surrounded_by_black and not surrounded_by_white:
                    for ex, ey in empty_group:
                        black_territory[ey, ex] = True
                elif surrounded_by_white and not surrounded_by_black:
                    for ex, ey in empty_group:
                        white_territory[ey, ex] = True
        
        return black_territory, white_territory
    
    def find_preview_empty_group(self, x, y):
        """
        プレビュー盤面での空点グループを取得
        
        Args:
            x, y: 空点の位置の座標
            
        Returns:
            list: グループに属する空点の座標のリスト
        """
        if self.preview_board is None or self.preview_board[y, x] != Board.EMPTY:
            return []
        
        group = []
        visited = np.zeros((self.size, self.size), dtype=bool)
        queue = deque([(x, y)])
        visited[y, x] = True
        
        while queue:
            cx, cy = queue.popleft()
            group.append((cx, cy))
            
            # 隣接する4方向をチェック
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < self.size and 0 <= ny < self.size and not visited[ny, nx] and self.preview_board[ny, nx] == Board.EMPTY:
                    queue.append((nx, ny))
                    visited[ny, nx] = True
        
        return group
    
    def calculate_preview_influence(self):
        """
        プレビュー用の影響圏を計算
        
        Returns:
            tuple: (黒の影響圏, 白の影響圏)
        """
        # プレビュー盤面がない場合は現在の影響圏を返す
        if self.preview_board is None:
            return self.black_influence, self.white_influence
        
        black_influence = np.zeros((self.size, self.size), dtype=bool)
        white_influence = np.zeros((self.size, self.size), dtype=bool)
        
        # 各石から1~2マス以内の空点を影響圏とする
        for y in range(self.size):
            for x in range(self.size):
                if self.preview_board[y, x] == Board.EMPTY:
                    # 黒石からの距離を計算
                    min_dist_black = self.calculate_preview_min_distance(x, y, Board.BLACK)
                    # 白石からの距離を計算
                    min_dist_white = self.calculate_preview_min_distance(x, y, Board.WHITE)
                    
                    # 影響圏の判定（距離が2以下で、かつ相手より近い）
                    if min_dist_black <= 2 and (min_dist_black < min_dist_white or min_dist_white > 2):
                        black_influence[y, x] = True
                    if min_dist_white <= 2 and (min_dist_white < min_dist_black or min_dist_black > 2):
                        white_influence[y, x] = True
        
        return black_influence, white_influence
    
    def calculate_preview_min_distance(self, x, y, color):
        """
        プレビュー盤面での最小距離計算
        
        Args:
            x, y: 位置の座標
            color: 石の色
            
        Returns:
            int: 最小距離（石がない場合は無限大）
        """
        if self.preview_board is None:
            return self.calculate_min_distance(x, y, color)
        
        min_dist = float('inf')
        
        for cy in range(self.size):
            for cx in range(self.size):
                if self.preview_board[cy, cx] == color:
                    dist = abs(x - cx) + abs(y - cy)  # マンハッタン距離
                    min_dist = min(min_dist, dist)
        
        return min_dist
    
    def calculate_score(self, color):
        """
        指定した色の得点を計算
        
        Args:
            color: 石の色
            
        Returns:
            int: 得点（取った石の数 + 陣地の数）
        """
        if color == Board.BLACK:
            territory_count = np.sum(self.black_territory)
            return self.black_captures + territory_count
        else:
            territory_count = np.sum(self.white_territory)
            return self.white_captures + territory_count
    
    def get_invalid_move_reason(self, x, y):
        """
        指定した位置に石を置けない理由を取得
        
        Args:
            x, y: 石を置く位置の座標
            
        Returns:
            str: 理由を示す文字列
        """
        # 盤外チェック
        if not (0 <= x < self.size and 0 <= y < self.size):
            return "盤外です"
        
        # 空点チェック
        if self.board[y, x] != Board.EMPTY:
            return "既に石が置かれています"
        
        # コウのルールチェック
        if self.ko == (x, y):
            return "コウのルールで置けません"
        
        # 自殺手チェック（仮に石を置いてみる）
        temp_board = self.board.copy()
        temp_board[y, x] = Board.BLACK
        
        # 隣接する相手の石を取れるかチェック
        can_capture = False
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.size and 0 <= ny < self.size and temp_board[ny, nx] == Board.WHITE:
                group = self.find_group(nx, ny)
                if not self.has_liberty(group):
                    can_capture = True
                    break
        
        # 自分の石のグループが呼吸点を持つかチェック
        has_liberty = False
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.size and 0 <= ny < self.size:
                if temp_board[ny, nx] == Board.EMPTY:
                    has_liberty = True
                    break
                elif temp_board[ny, nx] == Board.BLACK:
                    group = self.find_group(nx, ny)
                    if self.has_liberty(group):
                        has_liberty = True
                        break
        
        if not has_liberty and not can_capture:
            return "自殺手です"
        
        return "有効な手です"
