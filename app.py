import os, random, threading, time
from flask import Flask, flash, send_from_directory, render_template, request, redirect, url_for
from flask_uploads import UploadSet, configure_uploads, patch_request_class, IMAGES, DOCUMENTS
from werkzeug.utils import secure_filename
from tesseract import image2string
##### Database Instantiation ############
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Receipt, Accounts, Store

## instantiate session ########
engine = create_engine('sqlite:///receiptsStoresAccounts.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

##### End Database Instantiation ##########

##### Configure where to store photos & pdfs########

##### if using separate folders for images & pdfs
#app.config['UPLOADED_PHOTOS_DEST'] = 'static/img'
#app.config['UPLOADED_DOCUMENTS_DEST'] = 'static/pdfs'
#specify a maximum size for uploads
####################################################

####//// Using one folder for all uploads to begin with

UPLOAD_FOLDER = '/vagrant/uploads'
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg'])

#######////////////////////////////////////////////


####////   PROGRESS INDICATOR WITH THREADS **********
class ExportingThread(threading.Thread):
    def __init__(self):
        self.progress = 0
        super(ExportingThread, self).__init__()

    def run(self):
        # My exporting stuff should go here ...
        image2string('/vagrant/uploads/test.png')
        for _ in range(10):
            time.sleep(1)
            self.progress += 10

exporting_threads = {}
#######//////////////////////////////////////////////


##########  Flask App configurations ***************
app = Flask(__name__)
app.secret_key ='super secret key'
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
######/////////////////////////////////////////////


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


########  Routing                   ##########################

#####  Service Worker /***********
@app.route('/sw.js', methods=['GET'])
def sw():
    return app.send_static_file('sw.js')
#####/////////////////////////////////////






##### Simple uploader ######################
@app.route('/')
@app.route('/upload')
def upload_file():
    return render_template('index.html')

@app.route('/uploader', methods =['GET','POST'])  
def uploader():
    if request.method == 'POST':
      file = request.files['file']
      filename = secure_filename(file.filename)
      file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
      
      results = image2string(file.filename)
      return render_template('results.html', results = results)
      #return 'file uploaded successfully'

#####////////////////////////////////////////


#####  PROGRESS INDICATOR PAGE /***********
@app.route('/progress')
def index():
    global exporting_threads

    thread_id = random.randint(0,10000)
    exporting_threads[thread_id] = ExportingThread()
    exporting_threads[thread_id].start()

    return redirect(url_for('progress', thread_id = thread_id))

@app.route('/progress/<int:thread_id>')
def progress(thread_id):
    global exporting_threads

    return str(exporting_threads[thread_id].progress)
######////////////////////////////////////





#####  Route to uploader that redirects to opening file on success
#####

@app.route('/betterupload', methods=['GET', 'POST'])
def betterupload():
    if request.method == 'POST':
        # check if the post request has the file part
        #print 'its a post method'
        if 'file' not in request.files:
            #print 'no file in request.files'
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            #print 'its an allowed file'
            filename = secure_filename(file.filename)
            #print 'filename: ', filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            #print 'i think the file saved okay'
            
            return redirect(url_for('uploaded_file',
                                    filename=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''
#######  serves the file that was uploaded
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


#######///////////////////////////////////////////////////////

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)