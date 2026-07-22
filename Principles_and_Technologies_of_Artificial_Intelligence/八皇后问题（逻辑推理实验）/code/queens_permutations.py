from itertools import permutations
from typing import List, Tuple

class NQueensSolver:
    def __init__(self, n: int = 8):
        self.N = n
    
    def is_safe(self, pos: Tuple[int, ...]) -> bool:
        """检查给定位置是否安全（无冲突）"""
        for i in range(len(pos)):
            for j in range(i + 1, len(pos)):
                if pos[i] == pos[j] or abs(pos[i] - pos[j]) == j - i:
                    return False
        return True
    
    def solve(self) -> List[Tuple[int, ...]]:
        """使用更高效的方式求解N皇后问题"""
        # 生成候选解
        candidates = permutations(range(self.N))
        # 过滤出有效解
        solutions = [pos for pos in candidates if self.is_safe(pos)]
        return solutions

def visualize_solution(solution, N):
    """可视化一个解决方案"""
    board = []
    for i in range(N):
        row = ['□'] * N
        row[solution[i]] = '♕'
        board.append(' '.join(row))
    return '\n'.join(board)

def main():
    # 创建求解器实例
    N = 8
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