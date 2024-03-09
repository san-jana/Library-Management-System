from flask import *
import json, time
import pyodbc

# Flask app
app = Flask(__name__)

# SQL Server connector
myconnection = pyodbc.connect('DRIVER={SQL Server};' 
                      'Server=.\SQLEXPRESS;'
                      'Database=TheLibrary;'
                      'Trusted_Connection=yes')
cur = myconnection.cursor()

# Basic Authorization


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
                 book_data[idx] = {'Book ID': book.BookID, 'Book Name': book.BookName, 'Authors': book.Authors,'Book Alias': book.AuthorAlias, 'Book Edition': book.BookEdition, 'Book Dated': book.AddedtoLibDate, 'Book Status': book.BookStatus }
                 
        cur.commit()
                        
        return json.dumps(book_data) if book_data else (f"The Library contains no books with the keyword '{book_query.strip('%')}'.")
    
        
    except:
        return "Enter a Book ID, Name or Author to search for a Book."
    

# Get student data using the api endpoint 'http://127.0.0.1:5000/get-student/00062022CHE' where 00062022CHE is a Student ID. 
@app.route('/get-student/<student_id>')
def get_student(student_id):
    get_student_sql = "SELECT * FROM RegisteredStudents WHERE StudentID = ?"
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

# add a new book to the database
'''input must follow the format: 
{
    "id": "book id",
    "name": "book name",
    "authors": "authors separated by commas"(optional),
    "alias": common alias the book is referred by (eg. Wren and Martin)(optional),
    "book edition": edition of the book(optional)} 
    
    optional keys must be set equal to null if not used. Eg. "alias" : null '''
    
@app.route('/add-book', methods = ['POST'])
def add_book():
    book_data = request.get_json()
    book_data = list(book_data.values())
    cur.execute("INSERT INTO Books(BookID, BookName, Authors, AuthorAlias, BookEdition) \
            VALUES (?,?,?,?,?)", book_data)
    cur.commit()
    
    return "New book successfully added!"


# @app.route('/register-student', methods = ['POST']) -- the library does not need to register students
# def register_student():
#     student_data = request.get_json()
#     return student_data, 201


# Issue or re-issue a book
@app.route('/issue-book', methods = ['POST', 'PATCH'])
def issue_book():
    if request.method == 'POST':
        issue_data = request.get_json()
        return issue_data, 201
    
    # elif request.method == 'PUT':
    #     reissue_data = request.get_json()
    #     return reissue_data, 200
    

# Return a book 
@app.route('/return-book', methods = ['PATCH'])
def return_book():
    book_data =  request.get_json()
    return book_data, 200


# Delete a book


if __name__ == '__main__':
    app.run(debug = True)