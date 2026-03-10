#include <iostream>
#include <cstring>
using namespace std;

#define STACK_INIT_SIZE 1000
#define STACKINCREMENT 10

struct SqStack {
private:
    char* base;
    char* top;
    int stacksize;

public:
    SqStack();                    // 构造空栈
    ~SqStack();                   // 销毁已有的栈
    int ClearStack();             // 把现有栈置空栈
    int Top(char& e);             // 取栈顶元素
    int Pop(char& e);             // 弹出栈顶元素
    int Push(char e);             // 新元素入栈
    bool StackEmpty();            // 是否为空栈
};

SqStack::SqStack() {
    base = new(nothrow) char[STACK_INIT_SIZE];
    if (!base)
        exit(-2);
    top = base;
    stacksize = STACK_INIT_SIZE;
}

SqStack::~SqStack() {
    if (base)
        delete[] base;
    stacksize = 0;
}

int SqStack::ClearStack() {
    if (base)
        delete[] base;
    base = new(nothrow) char[STACK_INIT_SIZE];
    if (!base)
        exit(-2);
    top = base;
    stacksize = STACK_INIT_SIZE;
    return 0;
}

int SqStack::Top(char& e) {
    if (top == base)
        return -1;
    e = *(top - 1);
    return 0;
}

int SqStack::Pop(char& e) {
    if (top == base)
        return -1;
    e = *(--top);
    return 0;
}

int SqStack::Push(char e) {
    if (top - base >= stacksize) {
        char* newbase = new(nothrow) char[stacksize + STACKINCREMENT];
        if (!newbase)
            exit(-2);
        memcpy(newbase, base, sizeof(char) * stacksize);
        delete[] base;
        base = newbase;
        top = base + stacksize;
        stacksize += STACKINCREMENT;
    }
    *top = e;
    top++;
    return 0;
}

bool SqStack::StackEmpty() {
    return base == top;
}

void Operate(SqStack& Value, SqStack& Operator) {
    char v1, v2, o; // 声明变量 v1, v2 为操作数，o 为运算符
    Operator.Pop(o); // 弹出栈顶运算符
    switch (o) {
        case '!': // 处理逻辑非运算
            Value.Pop(v1); // 弹出一个操作数
            Value.Push(v1 == 'V' ? 'F' : 'V'); // 如果为 'V' 则压入 'F'，反之亦然
            break;
        case '&': // 处理逻辑与运算
            Value.Pop(v1); // 弹出两个操作数
            Value.Pop(v2);
            Value.Push((v1 == 'V' && v2 == 'V') ? 'V' : 'F'); // 两个都是 'V' 时压入 'V'
            break;
        case '|': // 处理逻辑或运算
            Value.Pop(v1); // 弹出两个操作数
            Value.Pop(v2);
            Value.Push((v1 == 'V' || v2 == 'V') ? 'V' : 'F'); // 只要有一个是 'V' 就压入 'V'
            break;
    }
}

// 处理运算符的函数，根据输入的运算符更新值栈和运算符栈
void processOperator(char ch, SqStack& Value, SqStack& Operator) {
    char get; // 用于临时存储栈顶运算符
    switch (ch) {
        case '(': // 遇到左括号时直接压入运算符栈
            Operator.Push(ch);
            break;
        case ')': // 遇到右括号时处理运算符
            // 弹出栈内运算符直到遇到左括号
            while (!Operator.StackEmpty() && (Operator.Top(get), get != '(')) {
                Operate(Value, Operator); // 执行运算
            }
            Operator.Pop(get); // 弹出左括号
            break;
        case '!': // 处理逻辑非运算符
            Operator.Push(ch); // 压入运算符栈
            break;
        case '&': // 处理逻辑与运算符
            // 弹出栈内优先级高于或等于 '&' 的运算符
            while (!Operator.StackEmpty() && (Operator.Top(get), get == '!')) {
                Operate(Value, Operator);
            }
            Operator.Push(ch); // 压入当前运算符
            break;
        case '|': // 处理逻辑或运算符
            // 弹出栈内优先级高于或等于 '|' 的运算符
            while (!Operator.StackEmpty() && ((Operator.Top(get), get == '!') || get == '&')) {
                Operate(Value, Operator);
            }
            Operator.Push(ch); // 压入当前运算符
            break;
    }
}

// 主函数，读取输入并评估布尔表达式
int main() {
    SqStack Value, Operator; // 创建值栈和运算符栈

    char ch; // 用于读取字符
    int times = 0; // 计算表达式数量
    while ((ch = getchar()) != EOF) { // 逐字符读取输入直到 EOF
        if (ch == '\n') { // 当遇到换行符时
            cout << "Expression " << ++times << ": "; // 输出当前表达式编号
            // 清空运算符栈，进行计算
            while (!Operator.StackEmpty())
                Operate(Value, Operator); // 执行所有剩余运算

            char Answer; // 存储最终结果
            Value.Top(Answer); // 获取值栈顶的结果
            cout << Answer << endl; // 输出结果
            Value.ClearStack(); // 清空值栈以准备下一个表达式
        }

        // 如果是操作数 'F' 或 'V'，压入值栈
        if (ch == 'F' || ch == 'V')
            Value.Push(ch);
        else { // 否则处理运算符
            processOperator(ch, Value, Operator);
        }
    }

    return 0; // 程序结束
}


