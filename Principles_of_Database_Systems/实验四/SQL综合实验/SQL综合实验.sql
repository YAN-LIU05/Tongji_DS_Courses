create database exp4;
use exp4;

CREATE TABLE Movie (
    Movie_no VARCHAR(10),
    Movie_name VARCHAR(50),
    Director VARCHAR(30),
    Rating DECIMAL(3,1),
    End_date DATETIME,
    PRIMARY KEY (Movie_no)
);
desc Movie;

CREATE TABLE Viewer (
    Viewer_no VARCHAR(10),
    Viewer_name VARCHAR(30), 
    Age INT,
    PRIMARY KEY (Viewer_no)
);
desc Viewer;

CREATE TABLE Watch (
    S_no VARCHAR(10),
    Viewer_no VARCHAR(10),  
    Movie_no VARCHAR(10),
    Watch_date DATETIME,
    PRIMARY KEY (S_no, Viewer_no, Movie_no),
    FOREIGN KEY (Viewer_no) REFERENCES Viewer(Viewer_no) ON DELETE CASCADE,
    FOREIGN KEY (Movie_no) REFERENCES Movie(Movie_no) ON DELETE CASCADE
);
desc Watch;

insert into Movie values
('M001', '星际穿越', '克里斯托弗·诺兰', 9.3, '2024-05-01'),
('M002', '泰坦尼克号', '詹姆斯·卡梅隆', 9.1, '2024-04-10'),
('M003', '盗梦空间', '克里斯托弗·诺兰', 8.8, '2024-04-20'),
('M004', '科幻冒险之旅', '张三', 7.5, '2024-04-18'),
('M005', '爱情故事', '李四', 7.0, '2024-04-25');

insert into Viewer values
('V001', '李明', 25),
('V002', '王红', 30),
('V003', '张磊', 22),
('V004', '赵颖', 28),
('V005', '孙阳', 35);

insert into Watch values
('1', 'V001', 'M001', '2024-03-15'),
('2', 'V001', 'M001', '2024-03-20'),
('2', 'V001', 'M002', '2024-03-20'),
('3', 'V002', 'M002', '2024-03-25'),
('1', 'V002', 'M003', '2024-04-01'),
('2', 'V003', 'M001', '2024-04-05'),
('2', 'V004', 'M002', '2024-04-12'),
('1', 'V005', 'M003', '2024-04-14');

SELECT Movie_name, Movie_no, Director, Rating, End_date
FROM Movie
WHERE Movie_name LIKE '%科幻%'
ORDER BY Rating DESC;

SELECT DISTINCT v.Viewer_no, v.Viewer_name, v.Age
FROM Viewer v
JOIN Watch w ON v.Viewer_no = w.Viewer_no
JOIN Movie m ON w.Movie_no = m.Movie_no
WHERE m.Movie_name = '泰坦尼克号'
ORDER BY v.Viewer_no ASC;

SELECT v.Viewer_no, m.Movie_name, w.Watch_date
FROM Viewer v
JOIN Watch w ON v.Viewer_no = w.Viewer_no
JOIN Movie m ON w.Movie_no = m.Movie_no
ORDER BY v.Viewer_no, w.Watch_date;

SELECT v.Viewer_no, v.Viewer_name, m.Movie_name, w.Watch_date
FROM Viewer v
JOIN Watch w ON v.Viewer_no = w.Viewer_no
JOIN Movie m ON w.Movie_no = m.Movie_no
WHERE m.End_date < '2025-04-15'
ORDER BY w.Watch_date DESC;

SELECT DISTINCT w1.Viewer_no
FROM Watch w1
JOIN Movie m1 ON w1.Movie_no = m1.Movie_no
LEFT JOIN (
    SELECT w2.Viewer_no
    FROM Watch w2
    JOIN Movie m2 ON w2.Movie_no = m2.Movie_no
    WHERE m2.Movie_name = '盗梦空间'
) w2 ON w1.Viewer_no = w2.Viewer_no
WHERE m1.Movie_name = '星际穿越'
AND w2.Viewer_no IS NULL
ORDER BY w1.Viewer_no ASC;

DELIMITER $$
CREATE PROCEDURE update_repeat_state()
BEGIN
    -- 1. 修改 Watch 表，增加 Repeat_state 字段，类型为 BOOLEAN
    ALTER TABLE Watch
    ADD COLUMN Repeat_state BOOLEAN DEFAULT FALSE;

    -- 2. 更新 Repeat_state 字段
    -- 使用子查询和 IF 语句判断每个 Viewer_no 和 Movie_no 组合的观看次数
    UPDATE Watch w
    SET Repeat_state = (
        SELECT IF(COUNT(*) > 1, TRUE, FALSE)
        FROM Watch w2
        WHERE w2.Viewer_no = w.Viewer_no 
        AND w2.Movie_no = w.Movie_no
    );
END$$
DELIMITER ;

CALL update_repeat_state();

SELECT v.Viewer_name, v.Viewer_no
FROM Viewer v
JOIN Watch w ON v.Viewer_no = w.Viewer_no
GROUP BY v.Viewer_no, v.Viewer_name
HAVING SUM(CASE WHEN w.Repeat_state = TRUE THEN 1 ELSE 0 END) = 0
ORDER BY v.Viewer_no;

CREATE UNIQUE INDEX Movie_name_index 
ON Movie (Movie_name DESC);
SHOW INDEX FROM Movie;