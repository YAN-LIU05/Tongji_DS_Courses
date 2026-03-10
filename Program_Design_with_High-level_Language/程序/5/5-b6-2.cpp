/* 2352018 信06 刘彦 */
#include <iostream>  
#include <iomanip>
using namespace std;

void hanoi(int n, char src, char tmp, char dst);

int hanoi0[3][10];
int top[3];
int Count = 0;// 移动次数计数器

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

void printTower1(int tower[], char label)
{
    cout << label << ":";
    for (int i = 0; i < 10; ++i)
    {
        if (hanoi0[0][i] == 0)
        {
            cout << "  "; // 两个空格表示没有盘
        }
        else
        {
            cout << setw(2) << tower[i];
        }
    }
    cout << " ";
}
void printTower2(int tower[], char label)
{
    cout << label << ":";
    for (int i = 0; i < 10; ++i)
    {
        if (hanoi0[1][i] == 0)
        {
            cout << "  "; // 两个空格表示没有盘
        }
        else
        {
            cout << setw(2) << tower[i];
        }
    }
    cout << " ";
}
void printTower3(int tower[], char label)
{
    cout << label << ":";
    for (int i = 0; i < 10; ++i)
    {
        if (hanoi0[2][i] == 0)
        {
            cout << "  "; // 两个空格表示没有盘
        }
        else
        {
            cout << setw(2) << tower[i];
        }
    }
    cout << " ";
}
void print()
{
    printTower1(hanoi0[0], 'A');
    printTower2(hanoi0[1], 'B');
    printTower3(hanoi0[2], 'C');
}

void moveA(char dst)
{
    int a;
    a = hanoi0[0][--top[0]];
    hanoi0[0][top[0]] = 0;
    if (dst == 'B')
    {
        hanoi0[1][top[1]++] = a;
    }
    if (dst == 'C')
    {
        hanoi0[2][top[2]++] = a;
    }
}
void moveB(int dst)
{
    int b;
    b = hanoi0[1][--top[1]];
    hanoi0[1][top[1]] = 0;
    if (dst == 'A')
    {
        hanoi0[0][top[0]++] = b;
    }
    if (dst == 'C')
    {
        hanoi0[2][top[2]++] = b;
    }
}
void moveC(int dst)
{
    int c;
    c = hanoi0[2][--top[2]];
    hanoi0[2][top[2]] = 0;
    if (dst == 'A')
    {
        hanoi0[0][top[0]++] = c;
    }
    if (dst == 'B')
    {
        hanoi0[1][top[1]++] = c;
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
    int storey, i;
    char src, dst, tmp;
    tmp = 0;

    while (1)
    {
        cout << "请输入汉诺塔的层数(1-10)" << endl;
        cin >> storey;
        if (cin.good() && storey >= 1 && storey <= 10)
        {
            cin.ignore(65536, '\n');
            break;
        }
        else
        {
            cin.clear();
            cin.ignore(65536, '\n');
        }
    }
    while (1)
    {
        cout << "请输入起始柱(A-C)" << endl;
        cin >> src;
        src = capital(src);
        if (cin.good() && (src >= 'A' && src <= 'C'))
        {
            cin.ignore(65536, '\n');
            break;
        }
        else
        {
            cin.clear();
            cin.ignore(65536, '\n');
        }
    }
    while (1)
    {
        cout << "请输入目标柱(A-C)" << endl;
        cin >> dst;
        dst = capital(dst);
        if (dst == src)
        {
            cout << "目标柱(" << dst << ")不能与起始柱(" << src << ")相同" << endl;
            cin.clear();
            cin.ignore(65536, '\n');
        }
        else if (cin.good() == 1 && (dst >= 'A' && dst <= 'C'))
        {
            cin.ignore(65536, '\n');
            break;
        }
        else
        {
            cin.clear();
            cin.ignore(65536, '\n');
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

    // 初始化圆盘
    if (src == 'A')
    {
        for (i = 0; i < storey; i++)
        {
            hanoi0[0][i] = storey - i;
        }
        top[0] = storey;
    }
    if (src == 'B')
    {
        for (i = 0; i < storey; i++)
        {
            hanoi0[1][i] = storey - i;
        }
        top[1] = storey;
    }
    if (src == 'C')
    {
        for (i = 0; i < storey; i++)
        {
            hanoi0[2][i] = storey - i;
        }
        top[2] = storey;
    }
    // 打印初始状态
    cout << "初始:";
    cout << "                ";
    print();
    cout << endl;


    hanoi(storey, src, tmp, dst);
    return 0;
}

void hanoi(int n, char src, char tmp, char dst)
{
    if (n == 1) {
        Count++;
        cout << "第" << setw(4) << Count << " 步" << "(" << setw(2) << n << ")" << ": " << src << "-->" << dst << " ";
        move(src, dst);
        // 打印圆盘
        print();
        cout << endl;
    }
    else {
        hanoi(n - 1, src, dst, tmp);
        Count++;
        cout << "第" << setw(4) << Count << " 步" << "(" << setw(2) << n << ")" << ": " << src << "-->" << dst << " ";
        move(src, dst);
        // 打印圆盘
        print();
        cout << endl;
        hanoi(n - 1, tmp, src, dst);
    }
}