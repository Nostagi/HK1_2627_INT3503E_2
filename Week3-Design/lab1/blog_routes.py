from __future__ import annotations

from flask import Flask, jsonify, request, make_response

# import _ as services

app = Flask(__name__)


LOCALHOST: dict = {
    "host": "127.0.0.1",
    "port": 5000,
    "debug": True,
}

# ========================
# USERS
# ========================

@app.get("/users/<int:user_id>")
def get_user(user_id: int):
    """
    Get an user profile by user_id.
    """
    pass

@app.get("/users/<int:user_id>/posts")
def list_user_posts(user_id: int):
    """
    Get an user's posts by user_id.
    """
    pass

@app.get("/users/<int:user_id>/posts/<int:post_id>")
def get_user_post(user_id: int, post_id: int):
    """
    Get a specific post by post_id for a given user.
    """
    pass

# ========================
# FOLLOWING
# ========================

@app.get("/users/<int:user_id>/following")
def list_user_following(user_id: int):
    """
    Get a list of users that the given user is following.
    """
    pass

@app.get("/users/<int:user_id>/followers")
def list_user_followers(user_id: int):
    """
    Get a list of users that are following the given user.
    """
    pass

# ========================
# POSTS
# ========================

@app.get("/posts/<int:post_id>/comments")
def list_post_comments(post_id: int):
    """
    Get a list of comments for a specific post.
    """
    pass

@app.get("/posts/<int:post_id>/tags")
def list_post_tags(post_id: int):
    """
    Get a list of tags for a specific post.
    """
    pass

# ============================================================
# APPLICATION START
# ============================================================

if __name__ == "__main__":
    app.run(**LOCALHOST)