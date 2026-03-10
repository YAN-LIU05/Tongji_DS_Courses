/* 2352018 大数据 刘彦 */
#include <iostream>
#include <cmath>
using namespace std;

class Shape {
protected:
    //根据需要加入相应的成员，也可以为空
    const double pai = 3.14159;
public:
    virtual void ShapeName() = 0; //此句不准动
    //根据需要加入相应的成员，也可以为空
    virtual double area() = 0;
};

//此处给出五个类的定义及实现(成员函数采用体外实现形式)
class Circle : public Shape {
protected:
    double r;
public:
    Circle(double _r);
    virtual void ShapeName();
    virtual double area();
};
class Square : public Shape {
protected:
    double a;
public:
    Square(double _a);
    virtual void ShapeName();
    virtual double area();
};
class Rectangle : public Shape {
protected:
    double a, b;
public:
    Rectangle(double _a, double _b);
    virtual void ShapeName();
    virtual double area();
};
class Trapezoid : public Shape {
protected:
    double a, b, h;
public:
    Trapezoid(double _a, double _b, double _h);
    virtual void ShapeName();
    virtual double area();
};
class Triangle : public Shape {
protected:
    double a, b, c;
public:
    Triangle(double _a, double _b, double _c);
    virtual void ShapeName();
    virtual double area();
};

//构造函数
Square::Square(double _a)
{
    a = _a;
}
Circle::Circle(double _r)
{
    r = _r;
}
Rectangle::Rectangle(double _a, double _b)
{
    a = _a;
    b = _b;
}
Trapezoid::Trapezoid(double _a, double _b, double _h)
{
    a = _a;
    b = _b;
    h = _h;
}
Triangle::Triangle(double _a, double _b, double _c)
{
    a = _a;
    b = _b;
    c = _c;
}
//图形名称
void Circle::ShapeName()
{
    cout << "Circle" << endl;
}
void Square::ShapeName()
{
    cout << "Square" << endl;
}
void Rectangle::ShapeName()
{
    cout << "Rectangle" << endl;
}
void Trapezoid::ShapeName()
{
    cout << "Trapezoid" << endl;
}
void Triangle::ShapeName()
{
    cout << "Triangle" << endl;
}
//面积计算函数
double Circle::area()
{
    if (r <= 0)
        return 0.0;
    else
        return pai * r * r;
}
double Square::area()
{
    if (a <= 0)
        return 0.0;
    else
        return a * a;
}
double Rectangle::area()
{
    if (a <= 0 || b <= 0)
        return 0.0;
    else
        return a * b;
}
double Trapezoid::area()
{
    if (a <= 0 || b <= 0 || h <= 0)
        return 0.0;
    else
        return (a + b) * h / 2;
}
double Triangle::area()
{
    if (a <= 0 || b <= 0 || c <= 0 || a + b <= c || a + c <= b || b + c <= a)
        return 0.0;
    double p = (a + b + c) / 2;
    return sqrt(p * (p - a) * (p - b) * (p - c));
}
/* -- 替换标记行 -- 本行不要做任何改动 -- 本行不要删除 -- 在本行的下面不要加入任何自己的语句，作业提交后从本行开始会被替换 -- 替换标记行 -- */

/***************************************************************************
  函数名称：
  功    能：
  输入参数：
  返 回 值：
  说    明：给出的是main函数的大致框架，允许进行微调或改变初值
***************************************************************************/
int main()
{
    if (1) {
        Circle    c1(5.2);           //半径（如果<=0，面积为0）
        Square    s1(5.2);           //边长（如果<=0，面积为0）
        Rectangle r1(5.2, 3.7);      //长、宽（如果任一<=0，面积为0）
        Trapezoid t1(2.3, 4.4, 3.8); //上底、下底、高（如果任一<=0，面积为0）
        Triangle  t2(3, 4, 5);       //三边长度（如果任一<=0或不构成三角形，面积为0）
        Shape* s[5] = { &c1, &s1, &r1, &t1, &t2 };

        int   i;
        for (i = 0; i < 5; i++) {
            s[i]->ShapeName(); //分别打印不同形状图形的名称（格式参考demo）
            cout << s[i]->area() << endl; //分别打印不同形状图形的面积（格式参考demo）
            cout << endl;
        }
    }

    if (1) {
        Circle    c1(-1);           //半径（如果<=0，面积为0）
        Square    s1(-1);           //边长（如果<=0，面积为0）
        Rectangle r1(5.2, -1);      //长、宽（如果任一<=0，面积为0）
        Trapezoid t1(2.3, -1, 3.8); //上底、下底、高（如果任一<=0，面积为0）
        Triangle  t2(3, 4, -1);       //三边长度（如果任一<=0或不构成三角形，面积为0）
        Shape* s[5] = { &c1, &s1, &r1, &t1, &t2 };

        cout << "============" << endl;
        int   i;
        for (i = 0; i < 5; i++) {
            s[i]->ShapeName(); //分别打印不同形状图形的名称（格式参考demo）
            cout << s[i]->area() << endl; //分别打印不同形状图形的面积（格式参考demo）
            cout << endl;
        }
    }

    return 0;
}
