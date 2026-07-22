from kanren import run, var
from kanren.goals import not_equalo, membero, goalify

# 定义 N (棋盘大小，例如 6x6)
N = 4

# 逻辑约束：不在同一对角线
def not_same_diagonal(row1, row2):
    def inner(col1, col2):
        return (row1 + col1 != row2 + col2) and (row1 - col1 != row2 - col2)
    return inner

# 定义列范围
cols = tuple(range(N))

# 创建 N 个变量表示皇后的位置
queens = tuple(var() for _ in range(N))

# 约束1：每个皇后都必须位于 0~N-1 的列中
column_constraints = [membero(queen, cols) for queen in queens]

# 约束2：所有皇后必须在不同的列
column_unique_constraints = [
    (not_equalo, (queens[i], queens[j]), True)
    for i in range(N)
    for j in range(i + 1, N)
]

# 约束3：所有皇后不能在同一对角线
diagonal_constraints = [
    (goalify(not_same_diagonal(i, j)), (queens[i], queens[j]), True)
    for i in range(N)
    for j in range(i + 1, N)
]

# 运行求解
solutions = run(
    0,
    queens,
    *column_constraints,  # 皇后必须在棋盘列范围内
    *column_unique_constraints,  # 不能在同一列
    *diagonal_constraints,  # 不能在对角线上
)

# 打印解决方案
print(f"Total solutions: {len(solutions)}")
for idx, solution in enumerate(solutions, 1):
    print(f"Solution {idx}: {solution}")
