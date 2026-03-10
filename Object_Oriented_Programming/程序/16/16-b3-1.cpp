/* 2352018 大数据 刘彦 */
#define _CRT_SECURE_NO_WARNINGS
#include <iostream>
#include <cstring>
using namespace std;

/* 此处允许添加必须的定义或声明（不允许全局变量） */
class Teacher;
/* Student 类的定义（成员函数不允许体内实现） */
class Student {
private:
	int num;	//学号
	char name[16];	//姓名
	char sex;	//性别，只能是 F/M 两种，大小写不敏感
	char addr[64];	//家庭住址
	//私有部分不允许添加任何内容
public:
	Student();
	Student(const int num1, const char* name1, const char sex1, const char* addr1);
	friend ostream& operator<<(ostream& out, const Student& stu);
	friend Teacher;
	//公有部分不允许添加任何内容
};

/* ----给出Student类成员函数及友元函数的体外实现---- */
Student::Student() 
{
	num = 2150000;
	sex = 'M';
	strcpy(name, "<学生S>");
	strcpy(addr, "四平路1239号");
}

Student::Student(const int num1, const char* name1, const char sex1, const char* addr1)
{
	num = num1;
	sex = sex1;
	strncpy(name, name1, 15);
	name[15] = '\0'; // 确保字符串以 '\0' 结束
	strncpy(addr, addr1, 63);
	addr[63] = '\0';
}

ostream& operator<<(ostream& out, const Student& stu) 
{
	out << stu.num << " " << stu.name << " " << stu.sex << " " << stu.addr;
	return out;
}
/* Teacher 类的定义（成员函数不允许体内实现） */
class Teacher {
private:
	int num;	//工号
	char name[16];	//姓名
	char sex;	//性别，只能是 F/M 两种，大小写不敏感
	char addr[64];	//家庭住址
	//私有部分不允许添加任何内容
public:
	Teacher();
	Teacher(const int num1, const char* name1, const char sex1, const char* addr1);
	friend ostream& operator<<(ostream& out, const Teacher& te);
	//公有部分允许添加成员函数（体外实现），不允许添加数据成员、友元声明
	Teacher& operator=(const Student& stu);
	operator Student() const;
};

/* ----给出Teacher类成员函数及友元函数的体外实现---- */
Teacher::Teacher()
{
	num = 21000; 
	sex = 'M';
	strcpy(name, "<教师T>");
	strcpy(addr, "四平路1239号衷和楼");
}

Teacher::Teacher(const int num1, const char* name1, const char sex1, const char* addr1)
{
	num = num1;
	sex = sex1;
	strncpy(name, name1, 15);
	name[15] = '\0';
	strncpy(addr, addr1, 63);
	addr[63] = '\0';
}

ostream& operator<<(ostream& out, const Teacher& te) 
{
	out << te.num << " " << te.name << " " << te.sex << " " << te.addr;
	return out;
}

Teacher& Teacher::operator=(const Student& stu)
{
	// 工号规则
	this->num = 21 * 1000 + stu.num % 1000;

	// 姓名规则
	strcpy(this->name, "教师");
	strncat(this->name, stu.name + 4, 14 - strlen(this->name)); // 拼接学生姓名从第3个字符开始

	// 性别规则
	this->sex = stu.sex;

	// 地址规则
	strncpy(this->addr, stu.addr, sizeof(this->addr) - 1);
	this->addr[sizeof(this->addr) - 1] = '\0';
	strncat(this->addr, "电信学院", sizeof(this->addr) - strlen(this->addr) - 1);

	return *this;
}

Teacher::operator Student() const
{
	Student stu;

	// 学号转换规则：学号 = 2150 + 工号后三位
	stu.num = 2150000 + this->num % 1000;

	// 姓名转换规则：前两个汉字替换为 "学生"
	strcpy(stu.name, "学生");
	strncat(stu.name, this->name + 4, sizeof(stu.name) - strlen(stu.name) - 1); // 拼接教师姓名的后续部分

	// 性别转换规则
	stu.sex = this->sex;

	// 地址转换规则：原地址后加 "101室"
	strncpy(stu.addr, this->addr, sizeof(stu.addr) - 1);
	stu.addr[sizeof(stu.addr) - 1] = '\0';
	strncat(stu.addr, "101室", sizeof(stu.addr) - strlen(stu.addr) - 1);

	return stu;
}




/***************************************************************************
  函数名称：
  功    能：
  输入参数：
  返 回 值：
  说    明：main函数不准动
***************************************************************************/
int main()
{
	Student s1;	//缺省值 - 学号：2150000 姓名：<学生S> 性别：M 地址：四平路1239号
	Student s2 = Student(2151234, "学生甲", 'M', "曹安公路4800号");
	Teacher t1;	//缺省值 - 工号：21000 姓名：<教师T> 性别：M 地址：四平路1239号衷和楼
	Teacher t2 = Teacher(21123, "教师A", 'F', "曹安公路4800号智信馆");

	/* 打印原始学生信息 */
	cout << "学生信息：" << s1 << endl;				//期望输出："学生信息：2150000 <学生S> M 四平路1239号"
	cout << "学生信息：" << s2 << endl;				//期望输出："学生信息：2151234 学生甲 M 曹安公路4800号"
	cout << endl;

	/* 打印原始教师信息 */
	cout << "教师信息：" << t1 << endl;				//期望输出："教师信息：21000 <教师T> M 四平路1239号衷和楼"
	cout << "教师信息：" << t2 << endl;				//期望输出："教师信息：21123 教师A F 曹安公路4800号智信馆"
	cout << endl;

	/* 学生转教师测试：
		学号转工号规则：工号 = 21 + 学号后三位
		姓名转换规则：前两个汉字转换为"教师"，后续字符不变
		性别转换规则：原样转换
		地址转换规则：原地址后加"电信学院"(不考虑字符串越界)    */
	t1 = s2;
	cout << "学生信息：" << s2 << endl;				//期望输出："学生信息：2151234 学生甲 M 曹安公路4800号"
	cout << "转换为教师的信息：" << t1 << endl;		//期望输出："转换为教师的信息：21234 教师甲 M 曹安公路4800号电信学院"
	cout << endl;

	/* 教师转学生测试：
		工号转学号规则：学号 = 2150 + 工号后三位
		姓名转换规则：前两个汉字转换为"学生"，后续字符不变
		性别转换规则：原样转换
		地址转换规则：原地址后加"101室"(不考虑字符串越界)    */
	s1 = t2;
	cout << "教师信息：" << t2 << endl;				//期望输出："教师信息：21123 教师A F 曹安公路4800号智信馆"
	cout << "转换为学生的信息：" << s1 << endl;		//期望输出："转换为学生的信息：2150123 学生A F 曹安公路4800号智信馆101室"
	cout << endl;

	return 0;
}