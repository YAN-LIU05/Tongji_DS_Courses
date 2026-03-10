from typing import List, Tuple

class NQueensSolver:
    def __init__(self, n: int = 8):
        self.N = n
        self.solutions: List[Tuple[int, ...]] = []

    def is_safe(self, board: List[int], row: int, col: int) -> bool:
        """检查在指定位置放置皇后是否安全"""
        # 检查之前的行
        for i in range(row):
            # 检查同列或对角线
            if (board[i] == col or 
                abs(board[i] - col) == abs(i - row)):
                return False
        return True

    def solve_recursive(self, board: List[int], row: int) -> None:
        """使用回溯法递归求解"""
        # 基本情况：已经放置了N个皇后
        if row == self.N:
            self.solutions.append(tuple(board))
            return

        # 尝试在当前行的每一列放置皇后
        for col in range(self.N):
            if self.is_safe(board, row, col):
                board[row] = col  # 放置皇后
                self.solve_recursive(board, row + 1)  # 递归处理下一行
                # 不需要显式回溯，因为下一次循环会覆盖当前位置

    def solve(self) -> List[Tuple[int, ...]]:
        """开始求解N皇后问题"""
        self.solutions = []  # 重置解决方案列表
        board = [-1] * self.N  # 初始化棋盘，-1表示未放置皇后
        self.solve_recursive(board, 0)  # 从第0行开始求解
        return self.solutions

def visualize_solution(solution: Tuple[int, ...], N: int) -> str:
    """可视化一个解决方案"""
    board = []
    for i in range(N):
        row = ['□'] * N
        row[solution[i]] = '♕'
        board.append(' '.join(row))
    return '\n'.join(board)

def main():
    # 创建求解器实例
    N = 12
    solver = NQueensSolver(N)
    
    # 求解
    solutions = solver.solve()
    
    # 输出结果
    print(f"找到 {len(solutions)} 个解决方案")
    for idx, solution in enumerate(solutions, 1):
        print(f"\n解决方案 {idx}: {solution}")
        print(visualize_solution(solution, N))
        print("\n" + "="*20)


if __name__ == "__main__":
    main()