## Week 2 — [Books API](./books_routers.py)

Week 2 implements a REST API for managing books. The tests below are organized by endpoint, then HTTP method, then sub-sample. Each sample includes the expected HTTP status and the relevant response headers or API behavior to verify.

### 1 `GET /books`

#### 1.1 List books — default pagination

```terminal
curl -i http://127.0.0.1:5000/books
# Expected: HTTP 200 OK
# Expected headers: Cache-Control: public, max-age=30
# Expected: pagination defaults to page=1 and size=20; HATEOAS _links are included
```

#### 1.2 List books — explicit page and size

```terminal
curl -i "http://127.0.0.1:5000/books?page=2&size=10"
# Expected: HTTP 200 OK
# Expected headers: Cache-Control: public, max-age=30
# Expected: pagination reports page=2 and size=10; _links.self/_links.first/_links.last are included
```

#### 1.3 List books — size above maximum

```terminal
curl -i "http://127.0.0.1:5000/books?page=1&size=200"
# Expected: HTTP 200 OK
# Expected headers: Cache-Control: public, max-age=30
# Expected: requested size is capped at 100; pagination is included
```

#### 1.4 Filter by author

```terminal
curl -i "http://127.0.0.1:5000/books?author=Orwell"
# Expected: HTTP 200 OK
# Expected headers: Cache-Control: public, max-age=30
# Expected: only books matching the author filter are returned; pagination and HATEOAS links are included
```

#### 1.5 Search by title

```terminal
curl -i "http://127.0.0.1:5000/books?q=clean"
# Expected: HTTP 200 OK
# Expected headers: Cache-Control: public, max-age=30
# Expected: books whose title contains the search term are returned
```

#### 1.6 Combine filter, search, and pagination

```terminal
curl -i "http://127.0.0.1:5000/books?author=Orwell&q=clean&page=1&size=10"
# Expected: HTTP 200 OK
# Expected headers: Cache-Control: public, max-age=30
# Expected: author filter, title search, and pagination are applied together
```

#### 1.7 Invalid pagination type

```terminal
curl -i "http://127.0.0.1:5000/books?page=abc&size=10"
# Expected: HTTP 400 Bad Request
# Expected: JSON error response identifies page/size as requiring integer values
```

#### 1.8 Empty collection

```terminal
curl -i http://127.0.0.1:5000/books
# Expected: HTTP 200 OK
# Expected headers: Cache-Control: public, max-age=30
# Expected: empty data collection is represented with pagination and HATEOAS metadata
```

### 2 `GET /books/<id>`

#### 2.1 Get an existing book

```terminal
curl -i http://127.0.0.1:5000/books/1
# Expected: HTTP 200 OK
# Expected headers: Cache-Control: max-age=60
# Expected: one book resource is returned
```

#### 2.2 Get a non-existing book

```terminal
curl -i http://127.0.0.1:5000/books/999
# Expected: HTTP 404 Not Found
# Expected: JSON error response indicates the book was not found
```

### 3 `POST /books`

#### 3.1 Create a book — valid request

```terminal
curl -i -X POST http://127.0.0.1:5000/books \
  -H "Content-Type: application/json" \
  -d '{"title":"Clean Code","author":"R. Martin"}'
# Expected: HTTP 201 Created
# Expected headers: Location: /books/<new_id>
# Expected: a new book resource is created with a generated ID
```

#### 3.2 Create another book

```terminal
curl -i -X POST http://127.0.0.1:5000/books \
  -H "Content-Type: application/json" \
  -d '{"title":"Clean Architecture","author":"R. Martin"}'
# Expected: HTTP 201 Created
# Expected headers: Location: /books/<new_id>
# Expected: generated ID differs from the previous created book
```

#### 3.3 Missing required field

```terminal
curl -i -X POST http://127.0.0.1:5000/books \
  -H "Content-Type: application/json" \
  -d '{"title":"Clean Code"}'
# Expected: HTTP 422 Unprocessable Entity
# Expected: JSON error response indicates title and author are required
```

#### 3.4 Empty required fields

```terminal
curl -i -X POST http://127.0.0.1:5000/books \
  -H "Content-Type: application/json" \
  -d '{"title":"","author":""}'
# Expected: HTTP 422 Unprocessable Entity
# Expected: JSON error response indicates title and author are required
```

#### 3.5 Missing JSON Content-Type

```terminal
curl -i -X POST http://127.0.0.1:5000/books \
  -d '{"title":"Clean Code","author":"R. Martin"}'
# Expected: HTTP 415 Unsupported Media Type
# Expected: JSON error response indicates JSON content is expected
```

#### 3.6 Invalid JSON

```terminal
curl -i -X POST http://127.0.0.1:5000/books \
  -H "Content-Type: application/json" \
  -d '{"title":"Clean Code","author":}'
# Expected: HTTP 422 Unprocessable Entity
# Expected: JSON error response indicates title and author are required
```

### 4 `PUT /books/<id>`

#### 1 Replace an existing book

```terminal
curl -i -X PUT http://127.0.0.1:5000/books/1 \
  -H "Content-Type: application/json" \
  -d '{"title":"New Title","author":"New Author"}'
# Expected: HTTP 200 OK
# Expected: existing book is replaced with the supplied representation
```

#### 2 Replace with optional fields

```terminal
curl -i -X PUT http://127.0.0.1:5000/books/1 \
  -H "Content-Type: application/json" \
  -d '{"title":"New Title","author":"New Author","isbn":"123456","price":19.99}'
# Expected: HTTP 200 OK
# Expected: title and author are replaced; isbn and price are accepted
```

#### 3 Missing required field

```terminal
curl -i -X PUT http://127.0.0.1:5000/books/1 \
  -H "Content-Type: application/json" \
  -d '{"title":"Only Title"}'
# Expected: HTTP 422 Unprocessable Entity
# Expected: JSON error response indicates title and author are required
```

#### 4 Replace a non-existing book

```terminal
curl -i -X PUT http://127.0.0.1:5000/books/999 \
  -H "Content-Type: application/json" \
  -d '{"title":"New Title","author":"New Author"}'
# Expected: HTTP 404 Not Found
# Expected: JSON error response indicates the book was not found
```

### 5 `PATCH /books/<id>`

#### 5.1 Update an existing book

```terminal
curl -i -X PATCH http://127.0.0.1:5000/books/1 \
  -H "Content-Type: application/json" \
  -d '{"title":"Updated Title","author":"Updated Author"}'
# Expected: HTTP 200 OK
# Expected: supplied fields are updated without replacing the entire stored object
```

#### 5.2 Update with price

```terminal
curl -i -X PATCH http://127.0.0.1:5000/books/1 \
  -H "Content-Type: application/json" \
  -d '{"title":"Updated Title","author":"Updated Author","price":19.99}'
# Expected: HTTP 200 OK
# Expected: title, author, and price are updated
```

#### 5.3 Negative price

```terminal
curl -i -X PATCH http://127.0.0.1:5000/books/1 \
  -H "Content-Type: application/json" \
  -d '{"title":"Updated Title","author":"Updated Author","price":-1}'
# Expected: HTTP 422 Unprocessable Entity
# Expected: JSON error response indicates price must be positive
```

#### 5.4 Missing title or author

```terminal
curl -i -X PATCH http://127.0.0.1:5000/books/1 \
  -H "Content-Type: application/json" \
  -d '{"price":19.99}'
# Expected: HTTP 422 Unprocessable Entity
# Expected: JSON error response indicates title and author are required
```

#### 5.5 Update a non-existing book

```terminal
curl -i -X PATCH http://127.0.0.1:5000/books/999 \
  -H "Content-Type: application/json" \
  -d '{"title":"Updated Title","author":"Updated Author"}'
# Expected: HTTP 404 Not Found
# Expected: JSON error response indicates the book was not found
```

### 6 `DELETE /books/<id>`

#### 6.1 Delete an existing book

```terminal
curl -i -X DELETE http://127.0.0.1:5000/books/1
# Expected: HTTP 204 No Content
# Expected: response body is empty
```

#### 6.2 Verify the deleted book

```terminal
curl -i http://127.0.0.1:5000/books/1
# Expected: HTTP 404 Not Found
# Expected: JSON error response indicates the book was not found
```

#### 6.3 Delete a non-existing book

```terminal
curl -i -X DELETE http://127.0.0.1:5000/books/999
# Expected: HTTP 404 Not Found
# Expected: JSON error response indicates the book was not found
```

### 7 Cache and HATEOAS verification

#### 7.1 Collection cache header

```terminal
curl -i "http://127.0.0.1:5000/books?page=1&size=10"
# Expected: HTTP 200 OK
# Expected headers: Cache-Control: public, max-age=30
```

#### 7.2 Individual resource cache header

```terminal
curl -i http://127.0.0.1:5000/books/1
# Expected: HTTP 200 OK when book 1 exists
# Expected headers: Cache-Control: max-age=60
```

#### 7.3 HATEOAS links on collection

```terminal
curl -i "http://127.0.0.1:5000/books?page=1&size=2"
# Expected: HTTP 200 OK
# Expected: _links.self, _links.first, and _links.last are present
# Expected: _links.next is present when another page exists
```

#### 7.4 HATEOAS previous-page link

```terminal
curl -i "http://127.0.0.1:5000/books?page=2&size=2"
# Expected: HTTP 200 OK when page 2 exists
# Expected: _links.prev is present for page > 1
```
