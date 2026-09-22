BOOKS:list[dict] = []
_next_id = 1

def get_all_books() -> list:
    return BOOKS

def get_next_id() -> int:
    return _next_id

def find_by_id(bid:int):
    i, book = next(((k, b) for k,b in enumerate(BOOKS) if b["id"]==bid), (None, None))
    return i, book


def create_book(new_book:dict):
    new_book.update({'id': get_next_id()})
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
