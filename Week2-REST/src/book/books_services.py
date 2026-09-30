BOOKS:list[dict] = []
_next_id = len(BOOKS)

def get_all_books() -> list:
    return BOOKS

def find_by_id(bid:int):
    i, book = next(((k, b) for k,b in enumerate(BOOKS) if b["id"]==bid), (None, None))
    return i, book


def create_book(new_book:dict):
    global _next_id, BOOKS

    new_book.update({'id': _next_id})
    BOOKS.append(new_book)
    _next_id += 1
    return new_book

def update_book(idx:int, new_data, replacement:bool=False):
    if replacement:
        BOOKS[idx] = new_data
    else:
        BOOKS[idx].update(new_data)

    return BOOKS[idx]

def delete_book(idx:int):
    BOOKS.pop(idx)

def get_book(query:dict) -> list:
    # filter: author chính xác, q tìm trong title
    filter = get_all_books()

    if "author" in query.keys():
        filter = [b for b in filter if b["author"].lower()==query['author'].lower()]

    if "q" in query.keys():
        filter = [b for b in filter if query["q"] in b["title"].lower()]

    return filter