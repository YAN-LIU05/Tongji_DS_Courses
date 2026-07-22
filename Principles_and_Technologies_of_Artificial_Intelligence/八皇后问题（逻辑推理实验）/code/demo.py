from kanren import run, var
from kanren.goals import not_equalo, membero, goalify
from itertools import chain

# 定义 N (棋盘大小，例如 6x6)
N = 6

# 逻辑约束：不在同一对角线
def not_same_diagonal(row1, row2):
    def inner(col1, col2):
        return (row1 + col1 != row2 + col2) and (row1 - col1 != row2 - col2)
    return inner

# 定义列范围
cols = tuple(range(N))

# 创建 N 个变量表示皇后的位置
queens = tuple(var() for _ in range(N))

# 运行求解
solutions = run(
    1,
    queens,
    *chain(
        (membero(queen, cols) for queen in queens),  # 限制皇后必须在棋盘列范围内
        (
            (not_equalo, (queens[i], queens[j]), True)  # 约束：不同列
            for i in range(N)
            for j in range(i + 1, N)
        ),
        (
            (
                goalify(not_same_diagonal(i, j)),  # 约束：不同对角线
                (queens[i], queens[j]),
                True,
            )
            for i in range(N)
            for j in range(i + 1, N)
        ),
    ),
)

# 打印解决方案
print(f"Total solutions: {len(solutions)}")
for idx, solution in enumerate(solutions, 1):
    print(f"Solution {idx}: {solution}")
