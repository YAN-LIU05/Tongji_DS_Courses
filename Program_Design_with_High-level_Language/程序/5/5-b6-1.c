/* 2352018 信06 刘彦 */
#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>

void hanoi(int n, char src, char tmp, char dst);
void init(int n, int arr[]);

// 全局变量声明
int A[10], B[10], C[10]; // 圆盘编号数组
int topA = 0, topB = 0, topC = 0; // 栈顶指针
int Count = 0; // 移动次数计数器

char capital(char x)
{
    if (x == 'a' || x == 'A')
        x = 'A';
    if (x == 'B' || x == 'b')
        x = 'B';
    if (x == 'c' || x == 'C')
        x = 'C';
    return x;
}

void printTower(int tower[], char label) {
    printf("%c:", label);
    for (int i = 0; i < 10; ++i) {
        if (tower[i] == 0) {
            printf("  "); // 两个空格表示没有盘
        }
        else {
            printf("%2d", tower[i]);
        }
    }
    printf(" ");
}
void print()
{
    printTower(A, 'A');
    printTower(B, 'B');
    printTower(C, 'C');
}

void moveA(char dst)
{
    int a;
    a = A[--topA];   // 从源柱子上移除一个圆盘
    A[topA] = 0;
    if (dst == 'B')
    {
        B[topB++] = a;    // 将圆盘移动到目标柱子
    }
    if (dst == 'C')
    {
        C[topC++] = a;
    }
}
void moveB(char dst)
{
    int b;
    b = B[--topB];
    B[topB] = 0;
    if (dst == 'A')
    {
        A[topA++] = b;
    }
    if (dst == 'C')
    {
        C[topC++] = b;
    }
}
void moveC(char dst)
{
    int c;
    c = C[--topC];
    C[topC] = 0;
    if (dst == 'A')
    {
        A[topA++] = c;
    }
    if (dst == 'B')
    {
        B[topB++] = c;
    }
}
void move(char src, char dst)
{
    if (src == 'A')
        moveA(dst);
    if (src == 'B')
        moveB(dst);
    if (src == 'C')
        moveC(dst);
}

int main()
{
    int n, ret, ret1, ret2, i;
    char src, dst, tmp = 0;
    while (1)
    {
        printf("请输入汉诺塔的层数(1-10):\n");
        ret = scanf("%d", &n);
        if (ret == 1 && n >= 1 && n <= 10)
        {
            while (getchar() != '\n');
            break;
        }
        else
        {
            while (getchar() != '\n');
        }
    }

    while (1)
    {
        printf("请输入起始柱(A-C)\n");
        ret1 = scanf("%c", &src);
        src = capital(src);
        if (ret1 == 1 && (src >= 'A' && src <= 'C'))
        {
            while (getchar() != '\n');
            break;
        }
        else
        {
            while (getchar() != '\n');
        }
    }
    while (1)
    {
        printf("请输入目标柱(A-C)\n");
        ret2 = scanf("%c", &dst);
        dst = capital(dst);
        if (dst == src)
        {
            printf("目标柱(%c)不能与起始柱(%c)相同\n", dst, src);
            while (getchar() != '\n');
        }
        else if (ret2 == 1 && (dst >= 'A' && dst <= 'C'))
        {
            while (getchar() != '\n');
            break;
        }
        else
        {
            while (getchar() != '\n');
        }
    }
    src = capital(src);
    dst = capital(dst);
    if ((src == 'B' && dst == 'C') || (src == 'C' && dst == 'B'))
        tmp = 'A';
    if ((src == 'A' && dst == 'C') || (src == 'C' && dst == 'A'))
        tmp = 'B';
    if ((src == 'A' && dst == 'B') || (src == 'B' && dst == 'A'))
        tmp = 'C';   //确定辅助柱

    //初始化圆盘
    if (src == 'A')
    {
        init(n, A);
        topA = n;
    }
    if (src == 'B')
    {
        init(n, B);
        topB = n;
    }
    if (src == 'C')
    {
        init(n, C);
        topC = n;
    }

    // 打印初始状态
    printf("初始:");
    printf("                ");
    printf("A:");
    for (i = 0; i < 10; i++)
    {
        if (A[i] != 0)
        {
            printf("%2d", A[i]);
        }
        else
        {
            printf("  ");
        }
    }
    printf(" ");
    printf("B:");
    for (i = 0; i < 10; i++)
    {
        if (B[i] != 0)
        {
            printf("%2d", B[i]);
        }
        else
        {
            printf("  ");
        }
    }
    printf(" ");
    printf("C:");
    for (i = 0; i < 10; i++)
    {
        if (C[i] != 0)
        {
            printf("%2d", C[i]);
        }
        else
        {
            printf("  ");
        }
    }
    printf("\n");

    // 递归求解
    hanoi(n, src, tmp, dst);
    return 0;
}
// 初始化圆盘
void init(int n, int arr[]) 
{
        for (int i = 0; i < n; i++) 
        {
            arr[i] = n - i ;
        }
}

// 汉诺塔函数
void hanoi(int n, char src, char tmp, char dst)
{
    if (n == 1) 
    {
        Count++; // 增加移动次数
        printf("第%4d步(%2d):%c-->%c   ", Count, n, src, dst);   // 打印移动步骤
        move(src, dst);
        // 打印圆盘
        print();
        printf("\n");
    }
    else
    {
        hanoi(n - 1, src, dst, tmp);
        Count++;

        printf("第%4d步(%2d):%c-->%c   ", Count, n, src, dst);
        move(src, dst);
        // 打印圆盘
        print();
        printf("\n");
        hanoi(n - 1, tmp, src, dst);
    }
}