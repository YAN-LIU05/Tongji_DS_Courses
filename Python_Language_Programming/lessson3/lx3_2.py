import json

def read_json_file(filename):
    # 读取JSON文件并返回解析后的数据
    with open(filename, 'r', encoding='utf-8') as file:
        return json.load(file)

def filter_scores_by_course(student, course_name):
    # 过滤学生的成绩列表，只保留包含指定课程的成绩记录
    filtered_scores = [
        {"学期": score["学期"], course_name: score[course_name]}
        for score in student["score"] if course_name in score
    ]
    student["score"] = filtered_scores
    return student

def find_course_scores(students_data, student_id, course_name):
    # 查找指定学号的学生，并过滤成绩列表
    for student in students_data:
        if student['学号'] == student_id:
            filtered_student = filter_scores_by_course(student, course_name)
            if filtered_student["score"]:  # 确保过滤后有成绩记录
                return filtered_student
    return "该学号对应的{}成绩没找到".format(course_name)

if __name__ == '__main__':
    students_data = read_json_file('course.txt')

    student_id_input = input("请输入学号：")
    course_name_input = input("请输入课程名称：")

    result = find_course_scores(students_data, student_id_input, course_name_input)

    print(result)