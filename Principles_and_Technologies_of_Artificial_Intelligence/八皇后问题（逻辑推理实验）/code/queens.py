from kanren import run, var  # 导入kanren库的核心功能
from kanren.goals import not_equalo, membero, goalify  # 导入约束相关的功能

class NQueens:
    def __init__(self, n=6):
        """初始化N皇后问题求解器
        Args:
            n (int): 棋盘大小和皇后数量，默认为6
        """
        self.N = n  # 设置棋盘大小
        self.cols = tuple(range(n))  # 创建列值域(0到n-1)
        self.queens = tuple(var() for _ in range(n))  # 创建n个逻辑变量表示皇后
    
    def get_constraints(self):
        """生成所有约束条件，包括列范围、列互异和对角线约束
        Returns:
            list: 包含所有约束的列表
        """
        # 约束1：列范围约束 - 确保每个皇后的列值在合法范围内(0到N-1)
        column_constraints = [
            membero(queen, self.cols) for queen in self.queens
        ]
        
        # 约束2：列互异约束 - 确保任意两个皇后不在同一列
        # not_equalo用于确保两个变量的值不相等
        column_unique_constraints = [
            (not_equalo, (self.queens[i], self.queens[j]), True)
            for i in range(self.N)  # 遍历每个皇后
            for j in range(i + 1, self.N)  # 只需要检查i之后的皇后
        ]
        
        # 约束3：对角线约束 - 确保任意两个皇后不在同一对角线上
        diagonal_constraints = []
        for i in range(self.N):
            for j in range(i + 1, self.N):
                # 创建lambda函数检查对角线冲突
                # i,j是行号，col1,col2是列号
                # abs(i-j)是行差，abs(col1-col2)是列差
                # 如果行差等于列差，说明在同一对角线上
                check_diagonal = lambda col1, col2, i=i, j=j: (
                    abs(i - j) != abs(col1 - col2)  # 检查主对角线和副对角线
                )
                # 使用goalify将lambda函数转换为逻辑约束
                diagonal_constraints.append(
                    (goalify(check_diagonal), (self.queens[i], self.queens[j]), True)
                )
        
        # 合并所有约束条件并返回
        return column_constraints + column_unique_constraints + diagonal_constraints
    
    def solve(self):
        """求解N皇后问题
        Returns:
            tuple: 所有可能的解决方案
        """
        return run(0, self.queens, *self.get_constraints())
    
    def visualize_solution(self, solution):
        """将解决方案可视化为棋盘样式
        Args:
            solution (tuple): 一个解决方案，表示每行皇后的列位置
        Returns:
            str: 可视化的棋盘字符串
        """
        board = []
        for i in range(self.N):
            row = ['□'] * self.N  # 创建空棋盘行
            row[solution[i]] = '♕'  # 在对应位置放置皇后
            board.append(' '.join(row))
        return '\n'.join(board)

def main():
    """程序入口函数"""
    # 创建 N 皇后问题实例
    n_queens = NQueens(6)
    solutions = n_queens.solve()
    
    # 打印结果
    print(f"找到 {len(solutions)} 个解决方案")
    
    # 遍历并展示每个解决方案
    for idx, solution in enumerate(solutions, 1):
        print(f"\n解决方案 {idx}: {solution}")
        print(n_queens.visualize_solution(solution))
        print("\n" + "="*20)

# 程序入口
if __name__ == "__main__":
    main()