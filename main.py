from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.utils import secure_filename
import os
import asyncio
import threading
from swibots import BotApp
from bin import *
from pyrogram import Client


api_id = 3702208
api_hash = "3ee1acb7c7622166cf06bb38a19698a9"


tg = Client("Spidy", api_id, api_hash,session_string=USER_SESSION_STRING)


async def progress(current, total):
    print(f"{current * 100 / total:.1f}%")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Change this to a random, secure value
app.config['UPLOAD_FOLDER'] = 'uploads'  # Folder to store uploaded files
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024  # Maximum file size allowed (20MB in this example)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

users = {'tester': {'password': 'yourdick'}, 'Spidy': {'password': 'pass'}}
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MTAyMDUsImlzX2JvdCI6dHJ1ZSwiYWN0aXZlIjp0cnVlLCJpYXQiOjE3MTM2MTQxOTgsImV4cCI6MjM0NDc2NjE5OH0.-SHFOkXWreqsjTjcM5V7GLaTZwfW62DGlzeGoYuQSnY"
bot = BotApp(TOKEN)

async def upload_progress_handler(progress):
    print(f"Upload progress: {format_file_size(progress.readed+progress.current)}")

async def switch_upload(file, caption):
    res = await bot.send_media(
        message=f"Caption: {caption}\nFileName: {os.path.basename(file)}",
        user_id=10204,
        document=file,
        description=caption,
        thumb=file,
        progress= upload_progress_handler)
    return res

def switch_upload_in_thread(username, file_path, caption):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        message = loop.run_until_complete(switch_upload(file_path, caption))
        entry_data = {
            'username': username,
            'file_id': message.id,
            'media_id': message.media_info.id,
            'media_link': message.media_link,
            'uploaded_date': message.sent_date,
            'checksum': message.media_info.checksum,
            'filename': file_path.replace("uploads/", ''),
            'file_size': message.media_info.file_size,
            'caption': caption,
        }
       
        write_to_binary(entry_data)
    finally:
        loop.close()

def format_file_size(file_size):
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    unit_index = 0
    while file_size >= 1024 and unit_index < len(units) - 1:
        file_size /= 1024.0
        unit_index += 1
    formatted_size = f"{file_size:.2f} {units[unit_index]}"
    return formatted_size

@app.route('/')
def home():
    if 'username' in session:
        username = session.get('username')
        return render_template('up.html',
            uploaded_files=[
                {'formatted_file_size': format_file_size(entry['file_size']), **entry}
                for entry in read_from_binary()['entries'] if entry['username'] == username
            ],
            username=username,
            total_storage=format_file_size(sum([entry["file_size"] for entry in read_from_binary()['entries'] if entry['username'] == username]))
        )
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
        if len(remote_url) > 1:
            file_name = os.path.basename(remote_url)
            os.system(f"wget -nc {remote_url} -P uploads/")
        else:
            file = request.files['file']
            file_name = secure_filename(file.filename)
            file.save(os.path.join("uploads", file_name))
        if not os.path.exists(os.path.join("uploads", file_name)):
                time.sleep(2)
        thread = threading.Thread(target=switch_upload_in_thread, args=(session['username'], os.path.join("uploads", file_name), caption))
        thread.start()
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
        return redirect(media_link, code=302, Response=f'<a href="{media_link}"download="{file_name}">Download {file_name}</a>')

def run_flask():
    app.run(host='0.0.0.0',port=80)

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()
    tg.run()
