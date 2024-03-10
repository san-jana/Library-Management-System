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

SELECT * FROM Students

SELECT * FROM Books
WHERE BookName LIKE 'ikigai' OR
BookID LIKE 'ikigai' OR
Authors LIKE 'ikigai'


-------------------------------------------- Issuing Books
--Eg.: StudentID = 00012022CSE; BookID = ID_0001A

--1. Check Student in Registered Students
SELECT * FROM Students
WHERE StudentID = '00012022CSE'

-- if Student Exists (Check if query returns a result)
-- check if Student Banned == 'NO' and Books Currently Issued < 5
-- if True,

--Check Books Status to avoid errors

--2. Insert into IssuedBooks (StudentID, BookID) <as per the StudentID and BookID provided> 

INSERT INTO BooksIssued(StudentID, BookID)
VALUES ('00012022CSE', 'ID_0001A')

SELECT * FROM BooksIssued

--3. Update Books Table, Set BookStatus to 'Issued', Where BookID == BookID
UPDATE Books
SET BookStatus = 'Issued'
WHERE BookID = 'ID_0001A'

SELECT * FROM Books

--4. Update Registered Students Table, Set BooksCurrentlyIssued = BooksCurrentlyIssued+1 
--                                     and Set TotalBooksIssued +=1, Where StudentID == StudentID

UPDATE Students
SET BooksCurrentlyIssued = BooksCurrentlyIssued + 1,
TotalBooksIssued = TotalBooksIssued + 1
WHERE StudentID = '00012022CSE'



------------Returning Books
SELECT * from BooksIssued WHERE StudentID = '00012022CSE' AND BookID = 'ID_0001A'

UPDATE BooksIssued
SET ReturnStatus = 'Returned',
ReturnDate = GETDATE()
WHERE StudentID = '00012022CSE' AND BookID = 'ID_0001A'

UPDATE Books
SET BookStatus = 'Available'
WHERE BookID = 'ID_0001A'

UPDATE Students
SET BooksCurrentlyIssued = BooksCurrentlyIssued - 1
WHERE StudentID = '00012022CSE'

----------------------------------------------- resetting Primary Key in BooksIssued

ALTER TABLE BooksIssued
DROP CONSTRAINT PK__BooksIss__32C52A7995B92F09;

ALTER TABLE BooksIssued
ADD FOREIGN KEY (StudentID) REFERENCES 
Student(StudentID);
