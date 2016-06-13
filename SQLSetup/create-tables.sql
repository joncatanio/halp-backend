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
   deleted BOOLEAN NOT NULL DEFAULT FALSE
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
   unlisted     BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE Users (
   userId          INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
   firstName       VARCHAR(32),
   lastName        VARCHAR(32),
   username        VARCHAR(32) NOT NULL UNIQUE,
   email           VARCHAR(128) NOT NULL UNIQUE,
   phone           VARCHAR(16),
   dateOfBirth     DATE,
   bio             VARCHAR(128),
   gender          ENUM('Decline to State', 'M', 'F', 'Other') DEFAULT 'Decline to State',
   password        CHAR(60) NOT NULL,
   school          INT UNSIGNED REFERENCES Schools(schoolId),
   major           INT UNSIGNED REFERENCES Majors(majorId),
   year            ENUM('1', '2', '3', '4', '5', '6+', 'Post-Graduate', 'Graduate'),
   verifiedTutor   BOOLEAN NOT NULL DEFAULT FALSE,
   joinDate        DATETIME,
   verifiedAccount BOOLEAN NOT NULL DEFAULT FALSE,
   deleted         BOOLEAN NOT NULL DEFAULT FALSE 
);

CREATE TABLE Tutors (
   `user`   INT UNSIGNED REFERENCES Users(userId),
   class    INT UNSIGNED REFERENCES Classes(classId),
   grade    ENUM('W', 'Fail', 'Pass', 'NC', 'CR', 'F', 'D-', 'D', 'D+', 'C-', 'C', 'C+', 'B-', 'B', 'B+', 'A-', 'A', 'A+'), 
   unlisted BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE Posts (
   postId   INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
   `user`   INT UNSIGNED REFERENCES Users(userId),
   content  VARCHAR(128),
   bounty   VARCHAR(8),
   class    INT UNSIGNED REFERENCES Classes(classId),
   postDate DATETIME,
   resolved BOOLEAN NOT NULL DEFAULT FALSE,
   tutor    INT UNSIGNED REFERENCES Users(userId),
   deleted  BOOLEAN NOT NULL DEFAULT FALSE
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
   revoked BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX TokenIndex ON Tokens(token, `user`);
