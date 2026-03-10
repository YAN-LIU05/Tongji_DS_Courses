import pandas as pd

class st_lesson:
    def __init__(self, st_no):
        self.st_no = st_no
        self.st_name = ""
        self.st_py = ""
        self.st_sex = ""
        self.st_course_list = []
        self.st_schedule_list = [
            ["上课时间", "周一", "周二", "周三", "周四", "周五"],
            ["上午一二节", [], [], [], [], []],
            ["上午三四节", [], [], [], [], []],
            ["下午一二节", [], [], [], [], []],
            ["下午三四节", [], [], [], [], []]
        ]

        self.load_data_from_excel()

    def load_data_from_excel(self):
        df1 = pd.read_excel('xuanke.xls', sheet_name=0)
        student_data = df1[df1['学号'] == int(self.st_no)].iloc[0]

        self.st_name = student_data['姓名']
        self.st_py = student_data['英文姓名']
        self.st_sex = student_data['性别']

        df2 = pd.read_excel('xuanke.xls', sheet_name=1)
        student_courses = df2[df2['学号'] == int(self.st_no)]
        self.st_course_list = student_courses.columns[student_courses.iloc[0] == '√'].tolist()

        df3 = pd.read_excel('xuanke.xls', sheet_name=2)

        for _, row in df3.iterrows():
            time_slot = row['上课时间']
            index = self._get_time_index(time_slot)
            if index == -1:
                continue
            for day in range(1, 6):
                courses = row.iloc[day]
                if isinstance(courses, str):
                    for course in courses.split(','):
                        if course.strip() in self.st_course_list:
                            self.st_schedule_list[index][day].append(course.strip())

    def _get_time_index(self, time_slot):
        mapping = {
            "上午一二节": 1,
            "上午三四节": 2,
            "下午一二节": 3,
            "下午三四节": 4
        }
        return mapping.get(time_slot, -1)

    def display_schedule(self):
        print(f"学号：{self.st_no:<10} 姓名：{self.st_name:} 的课表\n")

        header_row = self.st_schedule_list[0]
        print("".join(f"{str(cell):<20}" for cell in header_row))

        for index, row in enumerate(self.st_schedule_list[1:], start=1):
            time_slot = row[0]
            print(f"{time_slot:<20}", end="")

            for day_index in range(1, len(header_row)):
                if day_index < len(row):
                    course_list = row[day_index]
                    print(f"{', '.join(course_list):<20}", end="")
                else:
                    print("{:<20}".format(""), end="")
            print()
    def check_conflict(self):
        conflicts = {}
        for time_index in range(1, len(self.st_schedule_list)):
            time_slot = self.st_schedule_list[time_index][0]
            for day_index in range(1, 6):
                current_courses = self.st_schedule_list[time_index][day_index]
                if len(set(current_courses)) > 1:
                    day_name = self.st_schedule_list[0][day_index]
                    conflict_key = f"{day_name}{time_slot}"
                    if conflict_key not in conflicts:
                        conflicts[conflict_key] = []
                    conflicts[conflict_key].extend(current_courses)

        if conflicts:
            conflict_list = []
            for conflict, courses in conflicts.items():
                course_list_str = ", ".join(courses)
                conflict_info = f"[{conflict}[{course_list_str}]]"
                conflict_list.append(conflict_info)
            print(f"{self.st_name}的选课冲突有：{' '.join(conflict_list)}")
        else:
            print(f"{self.st_name}没有选课冲突")

if __name__ == "__main__":
    student = st_lesson('2352018')
    student.display_schedule()
    student.check_conflict()
