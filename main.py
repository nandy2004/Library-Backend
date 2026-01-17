from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from supabase import create_client

db_url="https://qauraqrsejejiafbbyyx.supabase.co"
db_key="sb_publishable_jMMpoeK3W8i250giVd4cIA__uetObBh"

db=create_client(db_url,db_key)

app=FastAPI()

# THIS ARE THE CRUD OPERATIONS PERFORMED ON THE "BOOKS" LIST
# To Get the list of all books 
@app.get('/books')
def get_all_books():
    result = db.table('Books').select('*').execute()
    data =result.data
    return data

#To get a book by book_id
@app.get('/books/{book_id}')
def get_book_by_id(book_id):
    result= db.table('Books').select('*').eq('id',book_id).execute()
    data= result.data
    return data

#To Add a new book to library
@app.post('/books/addnewbook')
async def add_new_book(request: Request):
    data = await request.json()
    book_id=data.get('book_id')
    existing=(db.table('Books').select('book_id').eq('book_id',book_id).execute())
    if existing.data:
        return JSONResponse(
            status_code=200,
            content={
                "status": "failed",
                "message": "Book ID already exists. Please change the Book ID."
            }
        )

    result = db.table("Books").insert(data).execute()

    return {
        "status": "success",
        "message": "Book added successfully",
        "data": result.data
    }
        
    result= db.table('Books').insert(data).execute()
    return "Book details added successfully"

#To update a book details
@app.put('/books/updatebookdetails/{book_id}')
async def update_book_details(request: Request,book_id):
    data =await request.json()
    result =db.table('Books').update(data).eq('id',book_id).execute()
    return "Book details are Updated Successfully"

#To delete a book from the library
@app.delete('/books/deleteabook/{book_id}')
def delete_a_book(book_id):
    result = db.table('Books').delete().eq('id',book_id).execute()
    return "Book deleted Successfully"


# THIS ARE THE CRUD OPERATIONS PERFORMED ON THE "USERS" LIST

#To get the list of all the users
@app.get('/users')
def get_all_users():
    result = db.table('Users').select('*').execute()
    data =result.data
    return data

#To get a user details by user_id
@app.get('/users/{user_id}')
def get_user_by_id(user_id):
    result= db.table('Users').select('*').eq('id',user_id).execute()
    data= result.data
    return data

#To Add a user to the library
@app.post('/users/addnewuser')
async def add_new_user(request: Request):
    data = await request.json()
    user_id=data.get('user_id')
    existing=(db.table('Users').select('user_id').eq('user_id',user_id).execute())
    if existing.data:
            content={
                "status":"failed",
                "message":"User ID already exist.please change the user ID"
            }
    result= db.table('Users').insert(data).execute()
    return {
        "status":"success",
        "message":"User added successfully",
        "data":result.data
    }

#To update a user details
@app.put('/users/updateuserdetails/{user_id}')
async def update_user_details(request: Request,user_id):
    data =await request.json()
    result =db.table('Users').update(data).eq('id',user_id).execute()
    return "user details are Updated Successfully"

#To delete a user details
@app.delete('/users/deleteauser/{user_id}')
def delete_a_user(user_id):
    result = db.table('Users').delete().eq('id',user_id).execute()
    return "user deleted Successfully"

# ISSUE A BOOK / User collecting a book from the library

@app.post('/books/selectbooktocollect')
async def Issue_book(request: Request):
    data = await request.json()
    book_id=data.get('book_id')
    user_id=data.get('user_id')
    # checking if book_id present or not
    book=(db.table('Books').select('*').eq('book_id',book_id).execute())
    if not book.data:
        return{
            "status":"failed",
            "message":"Book ID not found"
        }
    #check if book is previously collected or not
    book_status=book.data[0]
    if book_status["issued"] == "YES":
        return{
            "status":"failed",
            "message":"Book already collected by another user.Please Choose another book from the list."
        }
    book_name=book_status["book_name"]
    #checking if user_id is present or not
    user=(db.table('Users').select('*').eq('user_id',user_id).execute())
    if not user.data:
        return{
            "status":"failed",
            "message":"User id is not found.Register your user detailes to collect a book"
        }
    #checking if user have collected any book other or not
    user_status=user.data[0]
    if user_status["book_collected"] == "YES":
        return{
            "status":"failed",
            "message":"Sorry!. You have already collected a book. You can collect only one book"
        }
    #updating user details 
    update_user=(db.table('Users').update({"book_name":book_name,"book_collected":"YES"}).eq('user_id',user_id).execute())
    #Updating Book details 
    update_book=(db.table('Books').update({"issued":"YES"}).eq('book_id',book_id).execute())
    return {
        "status": "success",
        "message": f"'{book_name}' collected successfully"
    }

#COLLECT A BOOK / User returning a book to library

@app.post('/books/returnabook')
async def Return_a_Book(request: Request):
    data = await request.json()
    book_id=data.get('book_id')
    user_id=data.get('user_id')
    # checking if book_id present or not
    book=(db.table('Books').select('*').eq('book_id',book_id).execute())
    if not book.data:
        return{
            "status":"failed",
            "message":"Book ID not found"
        }
    #check if book is already returned
    book_status=book.data[0]
    if book_status["issued"] == "NO":
        return{
            "status":"failed",
            "message":"Book is already returned"
        }
    book_name=book_status["book_name"]
    #checking if user_id is present or not
    user=(db.table('Users').select('*').eq('user_id',user_id).execute())
    if not user.data:
        return{
            "status":"failed",
            "message":"User id is not found.Register your user detailes to collect or return a book"
        }
    #checking if user have already returned the book
    user_status=user.data[0]
    if user_status["book_collected"] == "NO":
        return{
            "status":"failed",
            "message":"You have not collected the book."
        }
    #updating user details 
    update_user=(db.table('Users').update({"book_name":"NA","book_collected":"NO","book_returned":"YES"}).eq('user_id',user_id).execute())
    #Updating Book details 
    update_book=(db.table('Books').update({"issued":"NO"}).eq('book_id',book_id).execute())
    return {
        "status": "success",
        "message": f"'{book_name}' Returned successfully"
    }
        