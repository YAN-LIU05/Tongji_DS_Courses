create table Student (
    No int,
    Name char(10),
    Grade float,
    Credit float,
    primary key (No)
);

insert into Student values (235001, '张三', 4.8, 120);
insert into Student values (235002, '李四', 4.7, 124.5);
insert into Student values (235003, '王五', 4.2, 99.5);
insert into Student values (2352018, '刘彦', 4.9, 110);

select No, Grade, Credit from Student;

UPDATE Student 
SET Grade = 4.82, Credit = 120 
WHERE No = 2350001;

UPDATE Student 
SET Grade = 4.65, Credit = 124.5 
WHERE No = 2350002;

UPDATE Student 
SET Grade = 4.2, Credit = 103.5 
WHERE No = 2350003;

delete from Student where No = 2350001;

select No
from Student
where Name = '刘彦';