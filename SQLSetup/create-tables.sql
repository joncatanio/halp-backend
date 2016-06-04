CREATE TABLE Schools (
   schoolId INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
   name     VARCHAR(128),
   country  VARCHAR(64),
   state    VARCHAR(64),
   city     VARCHAR(64)
);

CREATE TABLE Colleges (
   collegeId INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
   name       VARCHAR(128),
   school    INT UNSIGNED REFERENCES Schools(schoolId)
);

CREATE TABLE Classes (
   classId INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
   school  INT UNSIGNED REFERENCES Schools(schoolId),
   info    VARCHAR(1024),
   deleted BOOLEAN
);

CREATE TABLE Majors (
   majorId      INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
   school       INT UNSIGNED REFERENCES Schools(schoolId),
   name         VARCHAR(64),
   abbreviation VARCHAR(8),
   college      INT UNSIGNED REFERENCES Colleges(collegeId)
);

CREATE TABLE ClassNames (
   class        INT UNSIGNED REFERENCES Classes(classId),
   abbreviation VARCHAR(16),
   major        INT UNSIGNED REFERENCES Majors(majorId),
   name         VARCHAR(128),
   unlisted     BOOLEAN
);

CREATE TABLE Genders (
   genderId    TINYINT UNSIGNED PRIMARY KEY,
   description VARCHAR(32)
);

CREATE TABLE Users (
   userId          INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
   firstName       VARCHAR(32),
   lastName        VARCHAR(32),
   username        VARCHAR(32) UNIQUE,
   email           VARCHAR(128) UNIQUE,
   phone           VARCHAR(16),
   bio             VARCHAR(128),
   gender          TINYINT UNSIGNED REFERENCES Genders(genderId),
   password        CHAR(60),
   school          INT UNSIGNED REFERENCES Schools(schoolId),
   major           INT UNSIGNED REFERENCES Majors(majorId),
   year            ENUM('1', '2', '3', '4', '5', 'Post-Graduate', 'Graduate'),
   verifiedTutor   BOOLEAN,
   joinDate        DATETIME,
   verifiedAccount BOOLEAN,
   deleted         BOOLEAN
);

CREATE TABLE Tutors (
   `user`   INT UNSIGNED REFERENCES Users(userId),
   class    INT UNSIGNED REFERENCES Classes(classId),
   grade    ENUM('W', 'Fail', 'Pass', 'NC', 'CR', 'F', 'D-', 'D', 'D+', 'C-', 'C', 'C+', 'B-', 'B', 'B+', 'A-', 'A', 'A+'), 
   unlisted BOOLEAN
);

CREATE TABLE Posts (
   postId   INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
   `user`   INT UNSIGNED REFERENCES Users(userId),
   content  VARCHAR(128),
   bounty   VARCHAR(8),
   class    INT UNSIGNED REFERENCES Classes(classId),
   postDate DATETIME,
   helped   BOOLEAN,
   helpedBy INT UNSIGNED REFERENCES Users(userId),
   deleted  BOOLEAN
);

CREATE TABLE Messages (
   messageId INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
   content   VARCHAR(256),
   postDate  DATETIME,
   `user`    INT UNSIGNED REFERENCES Users(userId)
);

CREATE TABLE PostMessages (
   post    INT UNSIGNED REFERENCES Posts(postId),
   message INT UNSIGNED REFERENCES Messages(messageId)
);

CREATE TABLE Tokens (
   `user`  INT UNSIGNED REFERENCES Users(userId),
   token   CHAR(64) UNIQUE,
   expire  DATETIME,
   revoked BOOLEAN
);
