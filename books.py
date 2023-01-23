from fastapi import FastAPI, HTTPException, Request, status, Form, Header
from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from typing import Optional
import random
from starlette.responses import JSONResponse

app = FastAPI()


class Book(BaseModel):
    id: UUID
    title: str = Field(min_length=3)
    author: str
    description: Optional[str] = Field(title = "Description of the book", min_length = 1, max_length=100)
    rating: int = Field(ge=0, le=100)

    class Config:
        schema_extra = {
            "example": {
                "id": "fd370f21-17ab-4284-87cd-ef28c9de5189",
                "title": "Book 9",
                "author": "Author 1",
                "description": "A dummy book",
                "rating": 69
            }
        }

class BookNoRating(BaseModel):
    id: UUID
    title: str = Field(min_length=3)
    author:str
    description: Optional[str] = Field(title = "Description of the book", min_length = 1, max_length=100)


class NegativeNumberException(Exception):
    def __init__(self, books_to_return):
        self.books_to_return = books_to_return

@app.exception_handler(NegativeNumberException)
async def negative_number_exception_handler(request: Request, exception: NegativeNumberException):
    return JSONResponse(
        status_code=418,
        content = {
            "message": f"Got negative number: {exception.books_to_return}"
        }
    )


BOOKS = []


@app.post("/login")
async def login_handler(username: str = Form(), password: str = Form()):
    return {
        "username": username,
        "password": password
    }

@app.post("/headers")
async def headers_handler(optional_header: Optional[str] = Header(None)):
    return {
        "optional_header": optional_header
    }

@app.get("/book-login")
async def book_login(id: Optional[UUID], username: Optional[str] = Header(None), password: Optional[str] = Header(None)):
    if username == "FastAPIUser" and password == "test1234!":
        return next((book for book in BOOKS if book.id == id), None)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Either username or password is incorrect.")


@app.get("/")
async def get_books(num_books_to_return: Optional[int] = None):
    if num_books_to_return and num_books_to_return < 0:
        raise NegativeNumberException(num_books_to_return)

    # fill dummy data if empty
    if len(BOOKS) < 1:
        for i in range(10):
            dummy_book = Book(id=uuid4(), title=f"Book {i}", author=f"Author {i}", description="A dummy book", rating=random.randint(0, 100))
            BOOKS.append(dummy_book)

    if num_books_to_return is not None and len(BOOKS) >= num_books_to_return >= 0:
        return BOOKS[:num_books_to_return]
    return BOOKS


@app.get("/books/{id}")
async def get_book_by_id(id: UUID):
    return next((book for book in BOOKS if book.id == id), None)

@app.get("/books/no-rating/{id}", response_model= BookNoRating)
async def get_book_by_id_with_no_rating(id: UUID):
    return next((book for book in BOOKS if book.id == id), None)


@app.put("/books/{id}")
async def update_book_by_id(id: UUID, book: Book):
    idx = next((idx for idx in range(len(BOOKS)) if BOOKS[idx].id == id), None)
    if idx is None:
        raise raise_not_found_error()
    BOOKS[idx] = book
    return BOOKS[idx]


@app.delete("/books/{id}")
async def delete_book_by_id(id: UUID):
    idx = next((idx for idx in range(len(BOOKS)) if BOOKS[idx].id == id), None)
    if idx is None:
        raise raise_not_found_error()
    del BOOKS[idx]
    return {
        "message": "Book deleted successfully"
    }

@app.post("/", status_code=status.HTTP_201_CREATED)
async def create_book(book: Book):
    BOOKS.append(book)
    return book


def raise_not_found_error():
    return HTTPException(status_code=404, detail = "Book not found")