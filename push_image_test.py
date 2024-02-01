import requests
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import GetPosts, NewPost
from wordpress_xmlrpc.methods.users import GetUserInfo

def upload_image(client, image_path):
    # Define your image and its properties
    data = {
        'name': 'filename.jpg',
        'type': 'image/jpeg',  # mimetype
    }

    # Read the binary file and let the XMLRPC library encode it into base64
    with open(image_path, 'rb') as img:
        data['bits'] = img.read()

    response = client.call(UploadFile(data))
    attachment_id = response['id']
    return attachment_id

def push_post(client, title, content, attachment_id):
    post = WordPressPost()
    post.title = title
    post.content = content
    post.post_status = 'publish'
    post.thumbnail = attachment_id

    post_id = client.call(NewPost(post))
    return post_id

def main():
    url = 'http://my_website.blog/xmlrpc.php'
    username = 'MY_username'
    password = 'MY_password'

    client = Client(url, username, password)

    # Define the path to your image
    image_path = 'path_to_your_image.jpg'

    # Upload the image and get the attachment ID
    attachment_id = upload_image(client, image_path)

    # Your article data
    article = {
        'title': "Your Title",
        'content': "Your Content",
        'keyword': "Your Keyword",
        'keyphrase': "Your Keyphrase",
        'metadescription': "Your Meta Description"
    }

    # Send the post with the attachment ID
    post_id = push_post(client, article['title'], article['content'], attachment_id)

    print(f"Post created with ID: {post_id}")

if __name__ == "__main__":
    main()
