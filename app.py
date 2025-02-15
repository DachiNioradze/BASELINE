from ext import app

if __name__ == "__main__":
    from routes import index, upload, register, users, edit_users, delete_user, edit_post, delete_post, login, logout, content, view_content, post, like_post, dislike_post, filter, filtered_products, filter_text_posts, filtered_text_posts, delete_comment, edit_comments, upload_text_post, read_content, read_post, like_read_post, dislike_read_post, edit_read_comment, delete_read_comment, delete_read_post, edit_read_post, choose_upload, reviews, upload_review, delete_review, edit_review, timeline, event_detail
    app.run(debug=True)