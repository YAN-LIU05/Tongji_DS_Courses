/* 2352018 大数据 刘彦 */
#include <iostream>
#include <iomanip>
using namespace std;

#define STUDENT_NUM	4
#define SCORE_NUM	5

/* --- 不允许定义任何形式的全局变量 --- */

/***************************************************************************
  函数名称：
  功    能：求第一门课的平均分
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
void average(int (*score)[STUDENT_NUM])
{
    double sum = 0;  // 简单变量
    int* p = &(*score)[0]; // 指向第一个分数

    // 使用指针进行循环
    for (; p < &(*score)[0] + STUDENT_NUM; p++)
        sum += *p; // 累加分数

    cout << "第1门课平均分：" << sum / STUDENT_NUM << endl;
    cout << endl;
    /* 函数定义语句部分：
       1、本函数中仅允许定义 1个简单变量 + 1个指针变量 */

       /* 函数执行语句部分：
          1、不允许再定义任何类型的变量，包括 for (int i=0;...）等形式定义变量
          2、循环变量必须是指针变量，后续语句中不允许出现[]形式访问数组
             不允许：int a[10], i;
                     for(i=0; i<10; i++)
                         cout << a[i];
             允许  ：int a[10], p;
                     for(p=a; p<a+10; p++)
                         cout << *p;          */



}

/***************************************************************************
  函数名称：
  功    能：找出有两门以上课程不及格的学生
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
void fail(int (*score)[STUDENT_NUM])
{
    int failCount = 0; // 记录不及格科目数量
    int sum = 0; // 记录成绩总和

    /* 函数执行语句部分（要求同average）*/
    cout << "2门以上不及格的学生：" << endl;

    // 外循环遍历每个学生（按列）
    for (int* q = *score; q < *score + STUDENT_NUM; q++) 
    {
        failCount = 0; // 重置不及格科目数量
        sum = 0; // 重置成绩总和

        // 内循环遍历每门科目的成绩（按行）
        for (int (*p)[STUDENT_NUM] = score; p < score + SCORE_NUM; p++) 
        {
            // 检查当前科目是否不及格
            if (*(*p + (q - *score)) < 60)
                failCount++; // 不及格数量增加

            // 累加当前科目的成绩
            sum += *(*p + (q - *score));
        }

        // 如果不及格科目数量大于等于2，则输出该学生信息
        if (failCount >= 2) 
        {
            cout << "No：" << q - *score + 1 << " "; // 输出学生编号
            // 输出该学生的所有科目成绩
            for (int (*p)[STUDENT_NUM] = score; p < score + SCORE_NUM; p++)
                cout << *(*p + (q - *score)) << " ";

            // 输出该学生的平均分
            cout << "平均：" << (double)sum / SCORE_NUM << endl;
        }
    }
    cout << endl; // 输出换行
    /* 函数定义语句部分：
       1、本函数中仅允许定义 3个简单变量 + 1个行指针变量 + 1个简单指针变量 */

       /* 函数执行语句部分（要求同average）*/


}

/***************************************************************************
  函数名称：
  功    能：找出平均成绩在90分以上或全部成绩在85分以上的学生
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
void good(int (*score)[STUDENT_NUM])
{
    cout << "平均90以上或全部85以上的学生：" << endl;
    for (int* q = *score; q < *score + STUDENT_NUM; q++)
    {
        bool isGood = true;
        double sum = 0;
        for (int(*p)[STUDENT_NUM] = score; p < score + SCORE_NUM; p++)
        {
            sum += *(*p + (q - *score));
            if (*(*p + (q - *score)) < 85)
            {
                isGood = false;
            }
        }
        if (isGood || sum / SCORE_NUM >= 90)
        {
            cout << "No：" << q - *score + 1 << ' ';
            for (int(*p)[STUDENT_NUM] = score; p < score + SCORE_NUM; p++)
                cout << *(*p + (q - *score)) << " ";
            cout << "平均：" << sum / SCORE_NUM << endl;
        }
    }
    /* 函数定义语句部分：
       1、本函数中仅允许定义 3个简单变量 + 1个行指针变量 + 1个简单指针变量 */

       /* 函数执行语句部分（要求同average）*/

}

/***************************************************************************
  函数名称：
  功    能：
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
int main()
{
    int a[SCORE_NUM][STUDENT_NUM] = {
        {91,92,93,97},  //第1-4个学生的第1门课成绩
        {81,82,83,85},  //第1-4个学生的第2门课成绩
        {71,72,99,87},  //第1-4个学生的第3门课成绩
        {61,32,80,91},  //第1-4个学生的第4门课成绩
        {51,52,95,88} };//第1-4个学生的第5门课成绩
    /* 除上面的预置数组外，本函数中仅允许定义 1个行指针变量 + 1个简单指针变量 */

    /* 函数执行语句部分（要求同average）*/
    cout << "初始信息：" << endl;
    for (int (*p)[STUDENT_NUM] = a; p < a + SCORE_NUM; ++p)
    {
        cout << "No.1-4学生的第" << (p - a + 1) << "门课的成绩：";
        for (int *q = *p; q < *p + STUDENT_NUM; ++q)
        {
            cout << *q << " ";
        }
        cout << endl;
    }
    cout << endl;

    average(a);
    fail(a);
    good(a);

    return 0;
}