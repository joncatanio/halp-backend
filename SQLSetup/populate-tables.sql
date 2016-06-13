INSERT INTO Schools VALUES
   (NULL, 'California Polytechnic State University', 'United States', 'California', 'San Luis Obispo'),
   (NULL, 'Stanford', 'United States', 'California', 'Palo Alto')
;

INSERT INTO  Colleges VALUES
   (NULL, 'College of Agriculture, Food & Environmental Science', 1),
   (NULL, 'College of Architecture & Environmental Design', 1),
   (NULL, 'College of Engineering', 1),
   (NULL, 'College of Liberal Arts', 1),
   (NULL, 'College of Science & Mathematics', 1),
   (NULL, 'Orfalea College of Business', 1),
   (NULL, 'School of Business', 2),
   (NULL, 'School of Earth, Energy & Environmental Sciences', 2),
   (NULL, 'School of Education', 2),
   (NULL, 'School of Engineering', 2),
   (NULL, 'School of Humanities and Sciences', 2),
   (NULL, 'School of Law', 2),
   (NULL, 'School of Medicine', 2)
;

INSERT INTO Classes VALUES
   (NULL, 1, 'Basic principles of algorithmic problem solving and programming using methods of top-down design, stepwise refinement and procedural abstraction. Basic control structures, data types, and input/output. Introduction to the software development process: design, implementation, testing and documentation. The syntax and semantics of a modern programming language. Credit not available for students who have taken', 0),
   (NULL, 1, 'Role and impact of entrepreneurship; characteristics and traits of entrepreneurs; social, economic, cultural and policy conditions conducive to entrepreneurship; entrepreneurial thinking; opportunity identification and assessment; the management team; organizational and legal issues; business models; acquiring social and financial capital; managing startup to growth; entrepreneurial behavior in existing organizations; realizing and harvesting value.', 0),
   (NULL, 1, 'C programming language from a system programming perspective. Standard C language including operators, I/O functions, and data types in the context of system functions. Unix commands, shell scripting, file system, editors.', 0)
;

INSERT INTO Majors VALUES
   (NULL, 1, 'Computer Engineering', 'CPE', 3),
   (NULL, 1, 'Computer Science', 'CSC', 3),
   (NULL, 1, 'Software Engineering', 'SE', 3),
   (NULL, 1, 'Electrical Engineering', 'EE', 3),
   (NULL, 1, 'Materials Engineering', 'MATE', 3),
   (NULL, 1, 'Mechanical Engineering', 'ME', 3),
   (NULL, 1, 'Liberal Arts and Engineering Studies', 'LAES', 3),
   (NULL, 1, 'Biomedical Engineering', 'BMED', 3),
   (NULL, 1, 'Civil Engineering', 'CE', 3),
   (NULL, 1, 'Aerospace Engineering', 'AERO', 3),
   (NULL, 1, 'Art and Design', 'ART', 4),
   (NULL, 1, 'Communication Studies', 'COMS', 4),
   (NULL, 1, 'English', 'ENGL', 4),
   (NULL, 1, 'Ethnic Studies', 'ES', 4),
   (NULL, 1, 'Graphic Communication', 'GRC', 4),
   (NULL, 1, 'History', 'HIST', 4),
   (NULL, 1, 'Journalism', 'JOUR', 4),
   (NULL, 1, 'Music', 'MU', 4),
   (NULL, 1, 'Finance', 'BUS', 6),
   (NULL, 1, 'Industrial Technology and Packaging', 'BUS', 6),
   (NULL, 1, 'Entrepreneurship', 'BUS', 6),
   (NULL, 1, 'Management and Human Resources', 'BUS', 6),
   (NULL, 1, 'Marketing', 'BUS', 6),
   (NULL, 1, 'Information Systems', 'BUS', 6),
   (NULL, 1, 'Biological Sciences', 'BIO', 5),
   (NULL, 1, 'Chemistry and Biochemisty', 'CHEM', 5),
   (NULL, 1, 'Kinesiolgy', 'KINE', 5),
   (NULL, 1, 'Liberal Studies', 'LS', 5),
   (NULL, 1, 'Mathematics', 'MATH', 5),
   (NULL, 1, 'Physics', 'PHYS', 5),
   (NULL, 1, 'Statistics', 'STATS', 5),
   (NULL, 1, 'Agribusiness', 'AGB', 1),
   (NULL, 1, 'Agricultural Education and Communication', 'AGC', 1),
   (NULL, 1, 'Animal Science', 'ASCI', 1),
   (NULL, 1, 'Food Science and Nutrition', 'FSN', 1),
   (NULL, 1, 'Wine and Viticulture', 'WVIT', 1),
   (NULL, 1, 'Architecture', 'ARCH', 2),
   (NULL, 1, 'Architectural Engineering', 'ARCHE', 2),
   (NULL, 1, 'Construction Management', 'CM', 2),
   (NULL, 1, 'Landscape Architecture', 'LA', 2),
   (NULL, 2, 'Computer Science', 'CS', 10),
   (NULL, 2, 'Civil Engineering', 'CEE', 10),
   (NULL, 2, 'Chemical Engineering', 'CHEMENG', 10),
   (NULL, 2, 'Chemistry', 'CHEM', 11),
   (NULL, 2, 'Art Practice', 'ARTSTUDI', 11),
   (NULL, 2, 'Art History', 'ARTHIST', 11),
   (NULL, 2, 'English', 'ENGLISH', 11),
   (NULL, 2, 'Italian', 'ITALIAN', 11),
   (NULL, 2, 'History', 'HISTORY', 11),
   (NULL, 2, 'Biomedical Computation', 'BMC', 13),
   (NULL, 2, 'Communication', 'COMM', 11),
   (NULL, 2, 'Archaeology', 'ARCHLGY', 11),
   (NULL, 2, 'American Studies', 'AMSTUD', 11),
   (NULL, 2, 'Comparative Literature', 'COMPLIT', 11),
   (NULL, 2, 'Anthropology', 'ANTHRO', 11),
   (NULL, 2, 'Geological Sciences', 'GS', 8),
   (NULL, 2, 'Earth Systems Science', 'ESS', 8),
   (NULL, 2, 'Energy Resources Engineering', 'ERE', 8),
   (NULL, 2, 'Aeronautics and Astronautics', 'AA', 10)
;

INSERT INTO ClassNames VALUES
   (1, 'CPE 101', 1, 'Fundamentals of Computer Science I', 0),
   (1, 'CSC 101', 2, 'Fundamentals of Computer Science I', 0),
   (2, 'BUS 310', 21, 'Introduction to Entrepreneurship', 0),
   (3, 'CPE 357', 1, 'Systems Programming', 0),
   (3, 'CSC 357', 2, 'Systems Programming', 0)
;

-- Password for joncatanio & kendog is 'password' unhashed on clientside.
INSERT INTO Users VALUES
   (NULL, 'Jon', 'Catanio', 'joncatanio', 'fake@fake.com', '5303566442', '1995-06-16', 'TA for 357 and other courses!', 'M', '$2b$12$gOBCUl821jzRqInQXsvqrOMoRoUc/aP2ewJL84RQrpAT8ZDlyDa3G', 1, 2, '4', 1, '2016-06-03 15:28:22', 1, 0),
   (NULL, 'Test', 'User', 'testman', 'test@test.com', '0000000000', '1995-08-31', 'Need halp!', 'F', 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx', 2, 41, '1', 0, '2016-06-03 15:31:53', 1, 0),
   (NULL, 'Kendall', 'Gassner', 'kendog', 'kendog@test.com', '0000000000', '1996-01-15', 'Bi-yooo!', 'F', '$2b$12$gOBCUl821jzRqInQXsvqrOMoRoUc/aP2ewJL84RQrpAT8ZDlyDa3G', 1, 2, '4', 1, '2016-06-04 15:26:22', 1, 0)
;

INSERT INTO Tutors VALUES
   (1, 3, 'A', 0),
   (1, 1, 'B+', 0),
   (1, 2, 'A', 0)
;

INSERT INTO Posts VALUES
   (NULL, 2, 'Need help with 101, pointers are confusing!', '$15', 1, '2016-06-03 15:43:39', 0, 1, 0),
   (NULL, 2, 'What is the MVP?', ';)', 2, '2016-06-03 15:51:57', 0, 0, 0),
   (NULL, 2, 'Halp my grades have fallen and I can\'t get them up', ';)', 2, '2016-06-03 15:51:57', 1, 1, 0),
   (NULL, 2, 'Random need help yo', 'Monay', 2, '2016-06-03 15:51:57', 0, 0, 0),
   (NULL, 3, 'Never need help', '$$', 3, '2016-06-03 17:51:57', 1, 1, 0),
   (NULL, 3, 'Deleted post should not ever show', '$$', 3, '2016-06-03 17:51:57', 1, 1, 1),
   (NULL, 3, 'Randy post', '$5', 3, '2016-06-02 10:51:57', 0, 0, 0),
   (NULL, 3, 'This app is cool!', '$5', 3, '2016-06-02 20:51:57', 0, 0, 0),
   (NULL, 1, 'Also need help with something else bleh', '$60', 3, '2016-06-04 15:51:57', 0, 1, 0)
;

INSERT INTO Messages VALUES
   (NULL, 'Hey how is it goin? Need help with pointers?', '2016-06-03 15:53:29', 1),
   (NULL, 'Yes! Do you want to meet up at the lib?', '2016-06-03 15:54:34', 2),
   (NULL, 'Sure, how does 4:30pm sound?', '2016-06-03 15:56:29', 1),
   (NULL, 'Sounds great see you then!', '2016-06-03 15:56:31', 2)
;

INSERT INTO PostMessages VALUES
   (1, 1),
   (1, 2),
   (1, 3),
   (1, 4)
;
