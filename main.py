from flask import Flask, render_template, request, redirect, url_for, session, send_file
import os
import requests
import asyncio, random,os
from werkzeug.utils import secure_filename
from bin import *
from swibots import BotApp
from typing import Callable

class UploadProgress:
    def __init__(self, percent_complete: float):
        self.percent_complete = percent_complete

async def upload_progress_handler(progress: UploadProgress) -> None:
    print(f"Upload progress: {format_file_size(progress.current)}")

def upload_file(callback: Callable[[UploadProgress], 'Coroutine[Any, Any, None]']):
    for i in range(101):
        callback(UploadProgress(i))

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MTAyMDUsImlzX2JvdCI6dHJ1ZSwiYWN0aXZlIjp0cnVlLCJpYXQiOjE3MTM2MTQxOTgsImV4cCI6MjM0NDc2NjE5OH0.-SHFOkXWreqsjTjcM5V7GLaTZwfW62DGlzeGoYuQSnY"


bot = BotApp(TOKEN)
bot_loop = bot._loop
bot_name = bot.user.user_name


async def switch_upload(file,caption):
  res = await bot.send_media(
                       message=f"""Caption: {caption}\nFileName: {file.replace("uploads/",'')}""",
                       user_id=10204,
                       document=file,
                       description=caption,
                       thumb=file,
                       progress=upload_progress_handler)
  return res








def format_file_size(file_size):
    # Define units and corresponding labels
    units = ['B', 'KB', 'MB', 'GB', 'TB']

    # Determine the appropriate unit
    unit_index = 0
    while file_size >= 1024 and unit_index < len(units) - 1:
        file_size /= 1024.0
        unit_index += 1
    # Format the file size with two decimal places
    formatted_size = f"{file_size:.2f} {units[unit_index]}"
    return formatted_size



app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Change this to a random, secure value
app.config['UPLOAD_FOLDER'] = 'uploads'  # Folder to store uploaded files
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024  # Maximum file size allowed (20MB in this example)






os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

users = {'tester': {'password': 'yourdick'},
         'Spidy': {'password': 'pass'}}





@app.route('/')
def home():
    if 'username' in session:
        username = session.get('username')
        return render_template('up.html', 
uploaded_files = [{'formatted_file_size': format_file_size(entry['file_size']), **entry} for entry in read_from_binary()['entries'] if entry['username'] == username],
username=username,
total_storage= format_file_size(sum([entry["file_size"] for entry in read_from_binary()['entries'] if entry['username'] == username])))
    return render_template('login.html')





@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users and users[username]['password'] == password:
            session['username'] = username
            return redirect(url_for('home'))

        return 'Login failed. Check your username and password.'

    return render_template('login.html')








@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))


@app.route('/upload', methods=['POST'])
def upload_file():
    try:
            remote_url = request.form.get('remote_url', '')
            caption = request.form.get('caption', '')
            if len(remote_url) > 1 :
                file_name = os.path.basename(remote_url)

                os.system(f"wget -nc {remote_url} -P uploads/")
            else:
                file = request.files['file']
                file_name = secure_filename(file.filename)
                file.save(os.path.join("uploads", file_name))


            return redirect(url_for('home'))
            message = asyncio.run(switch_upload(os.path.join("uploads", file_name),caption))
            entry_data = {
                            'username': session['username'],  
                            'file_id': message.id,
                            'media_id':message.media_info.id,
                            'media_link': message.media_link,
                            'uploaded_date':message.sent_date.split()[0],
                            'checksum':message.media_info.checksum,
                            'filename': file_name,
                            'file_size': message.media_info.file_size,
                            'caption': caption,
                        }

            write_to_binary(entry_data)
            return redirect(url_for('home'))
    except Exception as e: 
                return f"Error: {str(e)}"





@app.route('/delete/<id>')
def delete_file(id):
   pass


@app.route('/download/<id>')
def download_file(id):
    entry = [entry for entry in read_from_binary()['entries'] if entry.get('id') == int(id)][0]
    if entry:
        file_name = f'''{entry["filename"]}'''
        media_link = f'{entry["media_link"]}' 
        return redirect(media_link, code=302, Response = f'<a href="{media_link}"download="{file_name}">Download {file_name}</a>')


if __name__ == '__main__':
    app.run(debug=True)