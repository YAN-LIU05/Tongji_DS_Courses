/* 2352018 信06 刘彦 */
#include <iostream>
#include <iomanip>
using namespace std;

/* ----具体要求----
   1、不允许添加其它头文件
   2、不允许定义全局变量、静态局部变量
   3、不允许添加其它函数
   4、main函数处理输入，允许循环
   --------------------------------------------------------------------- */

   /***************************************************************************
     函数名称：
     功    能：打印n层汉诺塔的移动顺序
     输入参数：int n：层数
               char src：起始柱
               char tmp：中间柱
               char dst：目标柱
     返 回 值：
     说    明：1、函数名、形参、返回类型均不准动
               2、本函数不允许出现任何形式的循环
   ***************************************************************************/
void hanoi(int n, char src, char tmp, char dst)
{
    if (n == 1) {
        cout << setw(2) << n << "# " << src << "-->" << dst << endl;
    }
    else {
        hanoi(n - 1, src, dst, tmp);
        cout << setw(2) << n << "# " << src << "-->" << dst << endl;
        hanoi(n - 1, tmp, src, dst);
    }
}

/***************************************************************************
  函数名称：
  功    能：
  输入参数：
  返 回 值：
  说    明：1、完成输入、调用递归函数
            2、处理输入错误时，允许使用循环
            3、为了统一检查，不再允许添加其它函数（输入起始/目标柱的代码不要求统一函数处理，均直接放在main中）
***************************************************************************/
int main()
{
    int storey;
    char src, dst, tmp;
    //tmp = 0;

    while (1)
    {
        cout << "请输入汉诺塔的层数(1-16)" << endl;
        cin >> storey;
        if (cin.good() && storey >= 1 && storey <= 16)
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
        if (src == 'a' || src == 'A')
            src = 'A';
        if (src == 'B' || src == 'b')
            src = 'B';
        if (src == 'c' || src == 'C')
            src = 'C';
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
        if (dst == 'a' || dst == 'A')
            dst = 'A';
        if (dst == 'b' || dst == 'B')
            dst = 'B';
        if (dst == 'c' || dst == 'C')
            dst = 'C';
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

    if ((src == 'b' || src == 'B') && (dst == 'c' || dst == 'C') || (src == 'c' || src == 'C') && (dst == 'b' || dst == 'B'))
        tmp = 'A';
    if ((src == 'a' || src == 'A') && (dst == 'c' || dst == 'C') || (src == 'c' || src == 'C') && (dst == 'a' || dst == 'A'))
        tmp = 'B';
    if ((src == 'a' || src == 'A') && (dst == 'b' || dst == 'B') || (src == 'b' || src == 'B') && (dst == 'a' || dst == 'A'))
        tmp = 'C';

    cout << "移动步骤为:" << endl;
    hanoi(storey, src, tmp, dst);
    return 0;
}