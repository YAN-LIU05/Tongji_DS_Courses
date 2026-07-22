#include <iostream>
using namespace std;

// 输入表达式
string s;
int num; // 变量数量
int map[26] = {0}; // 存储变量的值
int priority[128] = {0}; // 运算符优先级

const int N = 100; // 最大节点数

int root; // 树的根节点
int tree_x, tree_y; // 输出树的位置

char matrix[500][500]; // 存储绘制树的矩阵
int printLen[500]; // 每行打印长度

// 定义树节点类
class Node {
public:
    Node(int sub = -1, char blank = ' ', int left = -1, int right = -1, int value = 0)
    {
        this->children = sub; // 节点的索引
        this->c = blank; // 节点存储的字符
        this->l = left; // 左子节点
        this->r = right; // 右子节点
        this->value = value; // 节点的值
    }
    int children; // 子节点索引
    char c; // 存储的字符
    int l; // 左子节点索引
    int r; // 右子节点索引
    int value; // 节点的值
};

// 进行数学计算，根据符号
int domatrixh(Node* num, int& index_n, char sym, Node& fa)
{
    if (sym == '+')
    {
        int num1 = num[--index_n].value; // 取出最后一个数字
        fa.r = num[index_n].children; // 右子节点
        int num2 = num[--index_n].value; // 取出倒数第二个数字
        fa.l = num[index_n].children; // 左子节点
        return num1 + num2; // 返回结果
    }
    else if (sym == '-')
    {
        int num1 = num[--index_n].value; 
        fa.r = num[index_n].children; 
        int num2 = num[--index_n].value; 
        fa.l = num[index_n].children; 
        return num2 - num1; 
    }
    else if (sym == '*')
    {
        int num1 = num[--index_n].value; 
        fa.r = num[index_n].children; 
        int num2 = num[--index_n].value; 
        fa.l = num[index_n].children; 
        return num1 * num2; 
    }
    else if (sym == '/')
    {
        int num1 = num[--index_n].value; 
        fa.r = num[index_n].children; 
        int num2 = num[--index_n].value; 
        fa.l = num[index_n].children; 
        return num2 / num1; 
    }
    else
        return -1; // 处理错误情况
}

Node tree[N]; // 表达式树
Node stack_of_num[N]; // 数字栈
Node stack_of_operator[N]; // 运算符栈
int index_n = 0; // 数字栈索引
int index_priority = 0; // 运算符栈索引

// 计算表达式的值并构建表达式树
int cal_and_build_tree(string s)
{
    for (size_t i = 0; i < s.size(); i++)
    {
        Node node = Node(i, s[i]);
        tree[i] = node;

        // 判断是否为变量
        if (s[i] >= 'a' && s[i] <= 'z')
        {
            node.value = map[s[i] - 'a']; // 获取变量的值
            stack_of_num[index_n++] = node; // 存入数字栈
        }
        // 判断是否为运算符
        else
        {
            if (index_priority == 0 || s[i] == '(')
            {
                stack_of_operator[index_priority++] = node; // 存入运算符栈
            }
            else if (priority[int(stack_of_operator[index_priority - 1].c)] < priority[int(s[i])]) // 判断优先级
            {
                stack_of_operator[index_priority++] = node; // 存入运算符栈
            }
            else
            {
                if (s[i] == ')')
                {
                    while (stack_of_operator[index_priority - 1].c != '(')
                    {
                        Node nd = stack_of_operator[--index_priority]; // 弹出运算符栈
                        nd.value = domatrixh(stack_of_num, index_n, nd.c, nd); // 计算结果
                        tree[nd.children] = nd; // 更新树
                        stack_of_num[index_n++] = nd; // 将结果存入数字栈
                    }
                    index_priority--; // 弹出 '('
                }
                else
                {
                    while (index_priority > 0 && (priority[int(stack_of_operator[index_priority - 1].c)] >= priority[int(s[i])]))
                    {
                        Node nd = stack_of_operator[--index_priority]; // 弹出运算符栈
                        nd.value = domatrixh(stack_of_num, index_n, nd.c, nd); // 计算结果
                        tree[nd.children] = nd; // 更新树
                        stack_of_num[index_n++] = nd; // 将结果存入数字栈
                    }
                    stack_of_operator[index_priority++] = node; // 存入运算符栈
                }
            }
        }
    }

    // 处理剩余的运算符
    while (index_priority > 0)
    {
        Node nd = stack_of_operator[--index_priority]; // 弹出运算符栈
        nd.value = domatrixh(stack_of_num, index_n, nd.c, nd); // 计算结果
        tree[nd.children] = nd; // 更新树
        stack_of_num[index_n++] = nd; // 将结果存入数字栈
    }

    root = stack_of_num[index_n - 1].children; // 根节点

    return stack_of_num[index_n - 1].value; // 返回表达式值
}

// 反向遍历树并输出结果
void back_tranverse(int pos, int x, int y)
{
    if (tree[pos].l != -1) // 递归左子树
        back_tranverse(tree[pos].l, x - 1, y + 2);
    if (tree[pos].r != -1) // 递归右子树
        back_tranverse(tree[pos].r, x + 1, y + 2);

    cout << tree[pos].c; // 输出当前节点
}

// 计算树的深度
int cal_depth(int root1)
{
    int left = 0, right = 0;
    if (tree[root1].l != -1) 
        left = cal_depth(tree[root1].l);
    if (tree[root1].r != -1)
        right = cal_depth(tree[root1].r);
    return ((left >= right) ? left : right) + 1; // 返回深度
}

// 快速幂
int fps(int a, int p)
{
    int ans = 1;
    while (p)
    {
        if (p & 1) ans *= a;

        a *= a;
        p >>= 1; // 右移
    }
    return ans;
}

// 广度优先遍历，打印树结构
void bfs(int h)
{
    tree_x = 0; // 初始x坐标
    tree_y = (fps(2, h) - 1) / 2; // 初始y坐标

    Node stack[N]; // 存储当前节点的栈
    int stackIndex = 0; 
    Node currentNode = tree[root]; // 从根节点开始
    stack[stackIndex++] = currentNode;

    int posX[N] = {0}; // 记录x坐标
    int posY[N] = {0}; // 记录y坐标
    posX[0] = tree_x; // 初始化x坐标
    posY[0] = tree_y; // 初始化y坐标

    int index = 0;

    while (index < stackIndex)
    {
        currentNode = stack[index++]; // 当前节点
        int t_x = posX[index - 1]; // 当前x坐标
        int t_y = posY[index - 1]; // 当前y坐标

        // 根据当前节点的连接，调整位置
        if (t_x != 0 && matrix[t_x - 1][t_y] == '/')
            t_y -= (fps(2, h - t_x / 2 - 1) - 1);
        else if (t_x != 0 && matrix[t_x - 1][t_y] == '\\')
            t_y += (fps(2, h - t_x / 2 - 1) - 1);

        matrix[t_x][t_y] = currentNode.c; // 将当前节点字符放入矩阵

        // 处理左子节点
        if (currentNode.l != -1)
        {
            matrix[t_x + 1][t_y - 1] = '/'; // 绘制连接
            stack[stackIndex++] = tree[currentNode.l]; // 将左子节点入栈
            posX[stackIndex - 1] = t_x + 2; // 更新左子节点x坐标
            posY[stackIndex - 1] = t_y - 1; // 更新左子节点y坐标
        }

        // 处理右子节点
        if (currentNode.r != -1)
        {
            matrix[t_x + 1][t_y + 1] = '\\'; // 绘制连接
            stack[stackIndex++] = tree[currentNode.r]; // 将右子节点入栈
            posX[stackIndex - 1] = t_x + 2; // 更新右子节点x坐标
            posY[stackIndex - 1] = t_y + 1; // 更新右子节点y坐标
        }
        else
        {
            matrix[t_x + 1][t_y + 1] = ' '; // 如果没有右子节点，则空格
            matrix[t_x + 1][t_y - 1] = ' '; // 如果没有左子节点，则空格
        }
    }
}

int main()
{
    // 初始化运算符优先级
    priority['+'] = 1;
    priority['-'] = 1;
    priority['*'] = 2;
    priority['/'] = 2;
    priority['('] = 0;
    priority[')'] = 0;

    // 初始化矩阵
    for (int i = 0; i < 500; i++)
    {
        for (int j = 0; j < 500; j++)
        {
            matrix[i][j] = 'N'; // 标记为未使用
        }
    }

    // 输入表达式和变量数量
    cin >> s;
    cin >> num;

    // 输入变量的值
    for (int i = 1; i <= num; i++)
    {
        char vb;
        int n;
        cin >> vb >> n; // 输入变量名和其值
        map[vb - 'a'] = n; // 存储变量值
    }

    int res = cal_and_build_tree(s); // 计算表达式值
    int ht = cal_depth(root); // 计算树的高度

    tree_x = 0; // 初始化x坐标
    tree_y = (fps(2, ht) - 1) / 2; // 初始化y坐标

    back_tranverse(root, tree_x, tree_y); // 反向遍历并输出
    bfs(ht); // 广度优先遍历并绘制树

    cout << endl;

    // 打印树的结构
    for (int i = 0; i < ht * 2 - 1; i++)
    {
        int j = fps(2, ht - 1) * 2 - 1;
        while (matrix[i][j] == 'N') // 找到最后一个字符的位置
        {
            j--;
        }

        printLen[i] = j; // 记录打印长度

        while (j >= 0)
        {
            if (matrix[i][j] == 'N') matrix[i][j] = ' '; // 替换未使用的位置为' '
            j--;
        }
    }

    // 输出矩阵内容
    for (int i = 0; i < ht * 2 - 1; i++)
    {
        for (int j = 0; j <= printLen[i]; j++)
        {
            cout << matrix[i][j]; // 打印当前行
        }
        cout << endl; // 换行
    }

    cout << endl << res << endl; // 输出最终结果

    return 0; // 程序结束
}
