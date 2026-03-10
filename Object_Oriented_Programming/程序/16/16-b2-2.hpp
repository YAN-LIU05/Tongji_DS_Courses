/* 2352018 大数据 刘彦 */
#include <iostream>
#include <string>
using namespace std;

// 模板类 matrix
template <typename T, unsigned int ROW, unsigned int COL>
class matrix {
private:
    T value[ROW][COL]; // 用于存储矩阵的数据

public:
    // 默认构造函数：初始化为 T 的默认值
    matrix() {
        for (unsigned int i = 0; i < ROW; ++i) {
            for (unsigned int j = 0; j < COL; ++j) {
                value[i][j] = T();
            }
        }
    }

    // 矩阵加法操作符重载
    matrix operator+(const matrix& other) const {
        matrix result;
        for (unsigned int i = 0; i < ROW; ++i) {
            for (unsigned int j = 0; j < COL; ++j) {
                result.value[i][j] = value[i][j] + other.value[i][j];
            }
        }
        return result;
    }

    // 赋值操作符重载
    matrix& operator=(const matrix& other) {
        if (this != &other) { // 防止自我赋值
            for (unsigned int i = 0; i < ROW; ++i) {
                for (unsigned int j = 0; j < COL; ++j) {
                    value[i][j] = other.value[i][j];
                }
            }
        }
        return *this;
    }

    // 输入运算符重载
    friend istream& operator>>(istream& in, matrix& m) {
        for (unsigned int i = 0; i < ROW; ++i) {
            for (unsigned int j = 0; j < COL; ++j) {
                in >> m.value[i][j];
            }
        }
        return in;
    }

    // 输出运算符重载
    friend ostream& operator<<(ostream& out, const matrix& m) {
        for (unsigned int i = 0; i < ROW; ++i) {
            for (unsigned int j = 0; j < COL; ++j) {
                out << m.value[i][j] << " ";
            }
            out << endl;
        }
        return out;
    }
};
