-- DL
SELECT s.fio, s.contest_login, d.name, t.score as Зачет_score, sc.score as ДЗ_score, sc.is_ok_final as Зачет
FROM student_contest t
JOIN student s on t.student_id = s.id
JOIN student_department sd on s.id = sd.student_id
JOIN department d on sd.department_id = d.id
JOIN student_course sc on s.id = sc.student_id and sc.course_id = t.course_id
WHERE (contest_id = 'a4894cb5-f1d6-4844-a14f-16c1c99f0098' or contest_id = '643babdc-f205-42d4-a06f-c219817876f3')
AND t.score > 0
ORDER BY t.score DESC;


-- ML
SELECT s.fio, s.contest_login, d.name, t.score as Зачет_score, sc.is_ok_final as Зачет
FROM student_contest t
JOIN student s on t.student_id = s.id
JOIN student_department sd on s.id = sd.student_id
JOIN department d on sd.department_id = d.id
JOIN student_course sc on s.id = sc.student_id and sc.course_id = t.course_id
WHERE (contest_id = '49ab3671-3286-4c08-b355-2348d5e6ecd2' or contest_id = 'e1e5e1aa-04e1-40dd-9e4b-980e074207cc')
AND t.score > 0
ORDER BY t.score DESC;


-- DA
SELECT s.fio, s.contest_login, d.name, t.score as Зачет_score, sc.is_ok_final as Зачет, sc.is_ok
FROM student_contest t
JOIN student s on t.student_id = s.id
JOIN student_department sd on s.id = sd.student_id
JOIN department d on sd.department_id = d.id
JOIN student_course sc on s.id = sc.student_id and sc.course_id = t.course_id
WHERE (contest_id = 'a436830c-bc3f-4245-8102-f134cd89061e' or contest_id = '23b48464-6ba9-4860-b1fa-f19ba84dabc5')
AND t.score > 0
ORDER BY t.score DESC;


-- select count ok by department
SELECT d.name, count(sc.id) as count_ok
FROM student_course sc
JOIN student s on sc.student_id = s.id
JOIN student_department sd on s.id = sd.student_id
JOIN department d on sd.department_id = d.id
JOIN course c on sc.course_id = c.id
WHERE (sc.is_ok_final = true or sc.is_ok = true) and c.short_name = 'da_autumn_2022'
GROUP BY d.name
ORDER BY d.name;

SELECT count(sc.id) as count_ok
FROM student_course sc
JOIN course c on sc.course_id = c.id
WHERE (sc.is_ok_final = true or sc.is_ok = true) and c.short_name = 'da_autumn_2022';


-- select count ok by course auto
SELECT c.short_name, count(sc.id) as count_ok
FROM student_course sc
JOIN course c on sc.course_id = c.id
WHERE (sc.is_ok_final = false and sc.is_ok = true)
GROUP BY c.short_name;


-- select count ok by course final only
SELECT c.short_name, count(sc.id) as count_ok
FROM student_course sc
JOIN course c on sc.course_id = c.id
WHERE (sc.is_ok_final = true and sc.is_ok = false)
GROUP BY c.short_name;



SELECT s.fio as ФИО, d.name as Факультет_x
FROM student_course sc
JOIN student s on sc.student_id = s.id
JOIN student_department sd on s.id = sd.student_id
JOIN department d on sd.department_id = d.id
JOIN course c on sc.course_id = c.id
WHERE (sc.is_ok_final = true or sc.is_ok = true) and c.short_name = 'dl_autumn_2022'
ORDER BY s.fio;