/* 2352018 ¥Û ˝æ› ¡ı—Â */ 
#pragma once
#include <iostream>
#include <fstream>
#include <iomanip>
#include <cstdlib>
#include <vector>
#include <string>
#include <sstream>
#include "hw_check.h"
#include "../include/class_aat.h"
#include "../include_mariadb_x86/mysql/mysql.h"
using namespace std;

class Student {
	friend class hw_check;
protected:
	string term;
	string grade;
	string no;
	string name;
	string sex;
	string majorfull;
	string majorshort;
	string cno;
public:
	Student();
	Student(const string& s1, const string& s2, const string& s3, const string& s4, const string& s5, const string& s6, const string& s7, const string& s8);
	friend FILE_SITUATIONS get_print_second(const string& filepath, vector<Student>& check_stulist, const string& own_no);
	friend FILE_SITUATIONS get_print_first(const string& filepath, const string& filename, const Student& student);
	friend FILE_SITUATIONS validate_student_info(const vector<string>& comitem, const string& own_no, vector<Student>& check_stulist);
};

class Homework {
	friend class hw_check;
protected:
	string kind;
	string cno;
	string number;
	string chapter;
	string week;
	string filename;
	string point;
public:
	Homework(const string& s1, const string& s2, const string& s3, const string& s4, const string& s5, const string& s6, const string& s7);
};

class Config {
protected:
	string db_host;
	int    db_port;
	string db_name;
	string db_username;
	string db_passwd;
	string db_currterm;
	string src_rootdir;
public:
	Config();
	int read_config(const string& cfgfile);
};

class hw_check : public Config {
protected:
	vector<Student> stulist;
	vector<Homework> hwlist;
public:
	string action;
	string cno;
	string stu;
	string file;
	string cfgfile;
	string display;
	int chapter;
	int week;
	hw_check();
	int read_cmd(const args_analyse_tools* const args);
	int hw_check_all();
	int read_db_content();
	void print_hw_check_result(int choice, const int filestatus_num[], const int total_filestatus_num[]);
	void cross_check(const vector<vector<Student>>& total_check_stulist, const vector<Student>& total_stulist);
	MYSQL_RES* execute_query(MYSQL* mysql, const string& query);
	bool check_file_validity();
	bool should_skip_status(int i, const int secondlinestatus_set[], const std::string& action);
	void print_student_info(const Student& student, bool file_is_all, bool stu_is_all, int& stunum_cnt, int max_stu_length, bool is_special = false);
	FILE_SITUATIONS check_and_record_file_status(const string& filepath, const string& filename, const Student& student, vector<vector<Student>>& total_check_stulist);
	void print_file_check_result(int pass_count, int total_count);
};