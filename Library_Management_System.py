from flask import Flask, request, make_response
from functools import wraps
import json, time
import pyodbc
from dotenv import load_dotenv
import os

# Create a new flask app
app = Flask(__name__)

# Establish a SQL Server connection
myconnection = pyodbc.connect('DRIVER={SQL Server};' 
                      'Server=.\SQLEXPRESS;'
                      'Database=TheLibrary;'
                      'Trusted_Connection=yes')
cur = myconnection.cursor()

# Load the login credentials from your environment variables
load_dotenv()
lib_username = os.getenv(<'Your Username'>)
lib_password = os.getenv(<'Your Password'>)

# Authenticate user login using Basic Authorization
def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if auth and auth.username == lib_username and auth.password == lib_password:
            return f(*args, **kwargs)
        return make_response("Must verify to access The Library!",401, {'WWW-Authenticate': 'Basic realm="Login Required"'})
    return decorated


# Home Page
@app.route('/')
def home_page():
    data_set = {'Page': 'Home', 'Message': 'Welcome to the Library','Timestamp': time.time()}
    json_dump = json.dumps(data_set)
    return json_dump


# Search any book in the Library using a Book ID, Book Name or Author name
@app.route('/search-book/')
def search_page(): 
    try:
        book_query = str(request.args.get('book')) # /search-book/?book=book-id        
        book_queries = [book_query, book_query, book_query]
        books = cur.execute("SELECT * FROM Books \
                    WHERE BookName LIKE ? OR \
                    BookID LIKE ? OR \
                    Authors LIKE ?", book_queries).fetchall()
        
        book_data = {}
        for idx, book in enumerate(books):
            book_data[idx] = {'Book ID': book.BookID, 'Book Name': book.BookName, 
                              'Authors': book.Authors,'Book Alias': book.AuthorAlias, 
                              'Book Edition': book.BookEdition, 'Book Dated': book.AddedtoLibDate, 
                              'Book Status': book.BookStatus }
                 
        cur.commit()              
        return json.dumps(book_data) if book_data else (f"The Library contains no books with the keyword '{book_query.strip('%')}'.")
      
    except:
        return "Enter a Book ID, Name or Author to search for a Book."
    

# Get any student information using their student ID 
@app.route('/get-student/<student_id>')
@auth_required
def get_student(student_id):
    get_student_sql = "SELECT * FROM Students WHERE StudentID = ?"
    student = cur.execute(get_student_sql,student_id).fetchone()
    student_data = {"Student ID": student.StudentID,
                    "Student Name": student.FirstName+' '+student.LastName,
                    "Branch": student.Branch,
                    "Graduation Year": student.GraduationYear,
                    "Number of Books Issued Currently": student.BooksCurrentlyIssued,
                    "Cumulative Number Books Issued": student.TotalBooksIssued,
                    "Is the Student Banned": student.StudentBanned }  
    cur.commit()    
    return json.dumps(student_data), 200
    

# Add a new book to the database    
@app.route('/add-book', methods = ['POST'])
@auth_required
def add_book():
    book_data = request.get_json()
    book_data = list(book_data.values())
    cur.execute("INSERT INTO Books(BookID, BookName, Authors, AuthorAlias, BookEdition) \
            VALUES (?,?,?,?,?)", book_data)
    cur.commit()
    
    return "New book successfully added!"


# Issue or re-issue a book
@app.route('/issue-book', methods = ['POST', 'PATCH'])
@auth_required
def issue_book():
    issue_data = request.get_json()
    student_id , book_id = issue_data['Student ID'], issue_data['Book ID']
    
    if request.method == 'POST':     
        # get student's information
        student = cur.execute("SELECT * FROM Students WHERE StudentID = ?", student_id).fetchone()
        # check if student is banned
        if student.StudentBanned == 'BANNED':
            return("Student Banned! Issue Not Allowed.")
        else:
            # check if issue limit is exceeded
            if student.BooksCurrentlyIssued >= 5:
                return("Issue limit exceeded! Student can only issue 5 books at a time. Issue not allowed.")
                
            else:
                # check book status
                book = cur.execute("SELECT * FROM Books WHERE BookID = ?", book_id).fetchone()
                if book.BookStatus == 'Issued':
                    return("Book issued by another student. Issue a different book.")
                else:
                    # Issue Book
                    cur.execute("INSERT INTO BooksIssued(StudentID, BookID) VALUES (?, ?)", student_id, book_id)
                    cur.execute("UPDATE Books SET BookStatus = 'Issued' WHERE BookID = ?", book_id)
                    cur.execute("UPDATE Students SET BooksCurrentlyIssued = BooksCurrentlyIssued + 1, \
                    TotalBooksIssued = TotalBooksIssued + 1 WHERE StudentID = ?", student_id)
                    issued_book = cur.execute("SELECT * from BooksIssued WHERE StudentID = ? AND BookID = ?", student_id, book_id).fetchone()
                    
                    cur.commit()
                    return(f"Book issued successfully! Return book by {issued_book.ReturnbyIssueDate}")  
            
    # reissue request
    elif request.method == 'PATCH':       
        issued_book = cur.execute("SELECT * from BooksIssued WHERE StudentID = ? AND BookID = ?", student_id, book_id).fetchone()

        if not issued_book:
            return("The student has not issued this book.")
        else:
            if issued_book.ReturnStatus == 'Returned':
                return("Student has returned the book.")
            elif issued_book.ReturnStatus == 'Issued': 
                # reissue book
                cur.execute("UPDATE BooksIssued SET ReissuedOnDate = GETDATE(), ReissueCount = ReissueCount + 1 \
                WHERE StudentID = ? AND BookID = ?", student_id, book_id)
                cur.commit()
                return("Book re-issued")
        
    return ("Invalid request!")
    

# Return a book 
@app.route('/return-book', methods = ['PATCH'])
@auth_required
def return_book():
    return_data =  request.get_json()
    student_id , book_id = return_data['Student ID'], return_data['Book ID']
    
    # Get book details
    issued_book = cur.execute("SELECT * from BooksIssued WHERE StudentID = ? AND BookID = ?", student_id, book_id).fetchone()

    # Check if book exists in the Issued Books data table
    if not issued_book:
        return("The student has not issued this book.") 
    else:
        
        # Check if book has already been returned
        if issued_book.ReturnStatus == 'Returned':
            return("Student has returned the book.")
            
        elif issued_book.ReturnStatus == 'Issued':
            # Return book
            # Update Return Status and Return Date
            cur.execute("UPDATE BooksIssued SET ReturnStatus = 'Returned', ReturnDate = GETDATE() WHERE StudentID = ? AND BookID = ?", student_id, book_id)
            # Update Book Availibility Status
            cur.execute("UPDATE Books SET BookStatus = 'Available' WHERE BookID = ?", book_id)
            # Update 
            cur.execute("UPDATE Students SET BooksCurrentlyIssued = BooksCurrentlyIssued - 1 WHERE StudentID = ?", student_id)
            cur.commit()
            
            return("Book returned!")
        

if __name__ == '__main__':
    app.run(debug = True)
