CREATE DATABASE TheLibrary

CREATE TABLE Books(
	BookID varchar(50) PRIMARY KEY NOT NULL,
	BookName varchar(100),
	Authors varchar(50) DEFAULT NULL,
	AuthorAlias varchar(50) DEFAULT NULL,
	BookEdition int DEFAULT NULL,
	AddedtoLibDate Date DEFAULT GETDATE(),
	BookStatus varchar(50) DEFAULT 'Available'
);

CREATE TABLE BooksIssued(
	IssueID INT IDENTITY(1,1) PRIMARY KEY,
	StudentID varchar(50) NOT NULL FOREIGN KEY REFERENCES Student(StudentID) ,
	BookID varchar(50) FOREIGN KEY REFERENCES Books(BookID),
	IssueDate Date DEFAULT GETDATE(),
	ReturnbyIssueDate AS DATEADD(day, 15, IssueDate) PERSISTED,
	ReissuedOnDate Date,
	ReturnbyReissueDate AS DATEADD(day, 14, ReissuedOnDate) PERSISTED,
	ReissueCount int DEFAULT 0,
	ReturnStatus varchar(20) DEFAULT 'Issued',
	ReturnDate Date DEFAULT NULL
);

CREATE TABLE Students(
	StudentID varchar(50) NOT NULL PRIMARY KEY,
	FirstName varchar(50),
	LastName varchar(50),
	GraduationYear Date,
	Branch varchar(50),
	BooksCurrentlyIssued int DEFAULT 0,
	TotalBooksIssued int DEFAULT 0,
	FineDue money DEFAULT 0,
	StudentBanned varchar(10) DEFAULT 'NO'
);

INSERT INTO Students(StudentID, FirstName, LastName,	GraduationYear, Branch)
VALUES  ('00012022CSE', 'Adam', 'Dill', '01-05-2022', 'Computer Science Engineering'),
		('00022022CSE', 'Sydney', 'Grace', '01-05-2022', 'Computer Science Engineering'),
		('00032022BT', 'Jimmy', 'Smith', '01-05-2022', 'Biotechnology'),
		('00042022EE', 'Ana', 'John', '01-05-2022', 'Electrical Engineering')

INSERT INTO Books(BookID, BookName, Authors)
VALUES ('ID_0001A', 'Ikigai', 'Hector Garcia, Francesc Miralles'),
	('ID_0001B', 'Thinking Fast and Slow', 'Daniel Kahneman')
