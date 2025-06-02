    def draw_board(self, surface, board):
        """
        盤面を描画
        
        Args:
            surface: 描画対象のサーフェス
            board: 盤面オブジェクト
        """
        # 背景
        surface.fill(self.BOARD_COLOR)
        
        # 格子線
        for i in range(board.size):
            # 横線
            pygame.draw.line(
                surface,
                self.LINE_COLOR,
                (self.MARGIN, self.MARGIN + i * self.CELL_SIZE),
                (self.MARGIN + (board.size - 1) * self.CELL_SIZE, self.MARGIN + i * self.CELL_SIZE),
                self.LINE_WIDTH
            )
            # 縦線
            pygame.draw.line(
                surface,
                self.LINE_COLOR,
                (self.MARGIN + i * self.CELL_SIZE, self.MARGIN),
                (self.MARGIN + i * self.CELL_SIZE, self.MARGIN + (board.size - 1) * self.CELL_SIZE),
                self.LINE_WIDTH
            )
        
        # 星（天元）
        if board.size == 9:
            star_points = [(2, 2), (2, 6), (4, 4), (6, 2), (6, 6)]
        elif board.size == 13:
            star_points = [(3, 3), (3, 9), (6, 6), (9, 3), (9, 9)]
        elif board.size == 19:
            star_points = [(3, 3), (3, 9), (3, 15), (9, 3), (9, 9), (9, 15), (15, 3), (15, 9), (15, 15)]
        else:
            star_points = []
        
        for x, y in star_points:
            pygame.draw.circle(
                surface,
                self.LINE_COLOR,
                (self.MARGIN + x * self.CELL_SIZE, self.MARGIN + y * self.CELL_SIZE),
                self.STAR_RADIUS
            )
        
        # 石
        for y in range(board.size):
            for x in range(board.size):
                if board.board[y, x] == board.BLACK:
                    self.draw_stone(surface, x, y, self.BLACK_COLOR, board.stone_safety[y, x])
                elif board.board[y, x] == board.WHITE:
                    self.draw_stone(surface, x, y, self.WHITE_COLOR, board.stone_safety[y, x])
        
        # プレビュー
        if board.preview_board is not None:
            for y in range(board.size):
                for x in range(board.size):
                    if board.preview_board[y, x] != board.board[y, x]:
                        if board.preview_board[y, x] == board.BLACK:
                            self.draw_stone(surface, x, y, self.PREVIEW_BLACK_COLOR, board.preview_stone_safety[y, x])
                        elif board.preview_board[y, x] == board.WHITE:
                            self.draw_stone(surface, x, y, self.PREVIEW_WHITE_COLOR, board.preview_stone_safety[y, x])
    
    def draw_stone(self, surface, x, y, color, safety=3):
        """
        石を描画
        
        Args:
            surface: 描画対象のサーフェス
            x, y: 石の位置
            color: 石の色
            safety: 石の安全度（0:死確定 〜 3:安全）
        """
        # 安全度に応じた色の調整
        if safety < 3:
            # 安全度が低いほど赤みを帯びる
            if color == self.BLACK_COLOR:
                r = min(255, color[0] + (3 - safety) * 60)
                g = max(0, color[1] - (3 - safety) * 20)
                b = max(0, color[2] - (3 - safety) * 20)
                color = (r, g, b)
            else:  # WHITE_COLOR
                r = min(255, color[0])
                g = max(0, color[1] - (3 - safety) * 40)
                b = max(0, color[2] - (3 - safety) * 40)
                color = (r, g, b)
        
        # 石を描画
        pygame.draw.circle(
            surface,
            color,
            (self.MARGIN + x * self.CELL_SIZE, self.MARGIN + y * self.CELL_SIZE),
            self.STONE_RADIUS
        )
        
        # 安全度が低い場合は警告マークを表示
        if safety == 0:
            # 死確定の場合は×印
            pygame.draw.line(
                surface,
                (255, 0, 0),
                (self.MARGIN + x * self.CELL_SIZE - 5, self.MARGIN + y * self.CELL_SIZE - 5),
                (self.MARGIN + x * self.CELL_SIZE + 5, self.MARGIN + y * self.CELL_SIZE + 5),
                2
            )
            pygame.draw.line(
                surface,
                (255, 0, 0),
                (self.MARGIN + x * self.CELL_SIZE + 5, self.MARGIN + y * self.CELL_SIZE - 5),
                (self.MARGIN + x * self.CELL_SIZE - 5, self.MARGIN + y * self.CELL_SIZE + 5),
                2
            )
        elif safety == 1:
            # 非常に危険な場合は!マーク
            pygame.draw.line(
                surface,
                (255, 100, 0),
                (self.MARGIN + x * self.CELL_SIZE, self.MARGIN + y * self.CELL_SIZE - 5),
                (self.MARGIN + x * self.CELL_SIZE, self.MARGIN + y * self.CELL_SIZE + 2),
                2
            )
            pygame.draw.circle(
                surface,
                (255, 100, 0),
                (self.MARGIN + x * self.CELL_SIZE, self.MARGIN + y * self.CELL_SIZE + 5),
                1
            )
