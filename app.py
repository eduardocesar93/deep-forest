# pylint: disable=C0111
# pylint: disable=W0702
import os
import zipfile
import json
import time
import _thread
from flask import Flask, request, redirect, url_for,\
    render_template, send_file
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from models import BASE, Classifier, Dataset
import utils

UPLOAD_FOLDER = 'images/'
ALLOWED_EXTENSIONS = set(['tif', 'tiff'])

PORT = int(os.getenv('VCAP_APP_PORT', 8080))
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ENGINE = create_engine("sqlite:///deep_forest.db", echo=True)
BASE.metadata.bind = ENGINE
SESSION = scoped_session(sessionmaker(bind=ENGINE))

def secure_filename(filename):
    return filename # TODO


def create_folders_if_not_exist():
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    if not os.path.exists(UPLOAD_FOLDER + '/labels'):
        os.makedirs(UPLOAD_FOLDER + '/labels')
    if not os.path.exists('temp'):
        os.makedirs('temp')


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def zipdir(path, ziph):
    for root, _, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))


def current_milli_time():
    return int(round(time.time() * 1000))


def train_classifier_thread(percent_train_min, percent_train_max, percent_test_min,\
       percent_test_max, dataset_id, classifier_name, new_classifier):

    # ENGINE_THREAD = create_engine("sqlite:///deep_forest.db", echo=True)
    # BASE.metadata.bind = ENGINE_THREAD
    # SESSION_THREAD = sessionmaker(bind=ENGINE_THREAD)()

    # creates new classifier on database
    SESSION.add(new_classifier)
    SESSION.commit()

    score, model_path = utils.train_classifier(percent_train_min, percent_train_max, percent_test_min,\
       percent_test_max, dataset_id)

    classifier = SESSION.query(Classifier).filter_by(name=classifier_name).first()
    classifier.state = 2
    classifier.accuracy = score[1]
    classifier.model_path = model_path
    SESSION.commit()


@app.teardown_request
def remove_session(ex=None):
    SESSION.remove()


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/deletar-classificador")
def delete_classifier():
    id_value = request.args.get('id')
    classifier = SESSION.query(Classifier).filter_by(id=int(id_value)).first()
    password = request.args.get('password')
    try:
        if classifier.password == password:
            SESSION.delete(classifier)
            SESSION.commit()
            return "true"
        else:
            return "false"
    except:
        return "false"


@app.route("/deletar-dataset")
def delete_dataset():
    id_value = request.args.get('id')
    dataset = SESSION.query(Dataset).filter_by(id=int(id_value)).first()
    try:
        image_name = dataset.image_name
        label_name = dataset.label_name
        SESSION.delete(dataset)
        SESSION.commit()
        if image_name != "":
            os.remove(os.path.join(UPLOAD_FOLDER, image_name))
        if label_name != "":
            os.remove(os.path.join(UPLOAD_FOLDER + '/labels', label_name))
        return "true"
    except:
        return "false"


@app.route("/dashboard")
def dashboard():
    classifiers = SESSION.query(Classifier).order_by('order_table').all()
    datasets = SESSION.query(Dataset).all()
    for classifier in classifiers:
        if len(classifier.accuracy) > 5:
            classifier.accuracy = classifier.accuracy[0:6]
        if classifier.password != "":
            classifier.locked = 1
        else:
            classifier.locked = 0
    return render_template('dashboard.html', classifiers=classifiers,
                           datasets=datasets)


@app.route("/visualizacao")
def visualization():
    classifiers = SESSION.query(Classifier)\
        .filter(Classifier.state == 2)\
        .order_by('order_table').all()

    all_datasets = SESSION.query(Dataset)\
        .order_by('name').all()

    labeled_datasets = SESSION.query(Dataset)\
        .filter(Dataset.train == 1)\
        .all()

    return render_template('visualizacao.html', classifiers=classifiers,
        all_datasets=all_datasets, labeled_datasets=labeled_datasets)


@app.route("/adicionar-classificador", methods=['POST', 'GET'])
def add_classifier():
    if request.method == 'POST':
        try:
            order = SESSION.query(Classifier).count()
            password = ""
            if request.form["password"] == "yes":
                password = request.form["password_value"]
            new_classifier = Classifier(
                name=request.form['name'],
                dataset_first=int(request.form['dataset_first']),
                type_classifier=request.form['type_classifier'],
                optimization_method=int(request.form['optimization_method']),
                password=password,
                state=1,
                accuracy="-",
                order_table=order)

            try:
                dataset_first = int(request.form['dataset_first'])
                name = request.form['name']
                type_classifier = type_classifier=request.form['type_classifier']
                optimization_method=int(request.form['optimization_method'])
                epochs = int(request.form['epochs'])
                batch = int(request.form['batch'])
                activation_function = request.form['activation_function']
                learning_rate = int(request.form['learning_rate'])
                
                _thread.start_new_thread( train_classifier_thread, (0, 48, 50, 98, dataset_first, name , new_classifier, ))

            except:
               print ("Error: unable to start thread")
           # while 1:
           #    pass
            return redirect(url_for('dashboard', success='true'))

        except:
            return redirect(url_for('dashboard', fail='true'))
    else:
        datasets = SESSION.query(Dataset)\
            .filter(Dataset.label_name != "").all()
        return render_template('adicionarclassificador.html',
                               datasets=datasets)


@app.route("/atualizar-classificadores")
def update_classifiers():
    classifiers = request.args.get('classifiers')
    classifiers_dict = json.loads(classifiers)
    classifiers = SESSION.query(Classifier).all()
    for classifier_item in classifiers_dict:
        for classifier in classifiers:
            if classifier.id == int(classifier_item['id']):
                classifier.name = classifier_item['classificador']
                classifier.order_table = int(classifier_item['order'])
                SESSION.add(classifier)
                SESSION.commit()

    datasets = request.args.get('datasets')
    datasets_dict = json.loads(datasets)
    datasets = SESSION.query(Dataset).all()
    for dataset_item in datasets_dict:
        for dataset in datasets:
            if dataset.id == int(dataset_item['id']):
                dataset.name = dataset_item['dataset']
                SESSION.add(dataset)
                SESSION.commit()

    return "true"


@app.route('/adicionar-dataset', methods=['POST', 'GET'])
def add_dataset():
    if request.method == 'POST':
        try:
            if 'image' in request.files:
                image = request.files['image']
                if image.filename == "":
                    raise Exception("No image Exception")
            else:
                raise Exception("No Image Exception")
            if request.form['train'] == 'yes':
                train = 1
            else:
                train = 0
            current_time = current_milli_time()
            image_name = secure_filename("{0}-{1}".format(current_time,
                                                          image.filename))
            image.save(os.path.join(UPLOAD_FOLDER, image_name))
            if train == 1:
                label_image = request.files['label']
                label_name = secure_filename("{0}-{1}"
                                             .format(current_time,
                                                     label_image.filename))
                if label_name == "":
                    raise Exception("No Image Exception")
                label_path = os.path.join(UPLOAD_FOLDER + '/labels',
                                              label_name)
                label_image.save(label_path)
            else:
                label_name = ""
            new_dataset = Dataset(
                name=request.form['name'],
                year=int(request.form['year']),
                train=train,
                image_name=image_name,
                label_name=label_name,
                lat_inf=request.form['lat_inf'],
                lat_sup=request.form['lat_sup'],
                lng_inf=request.form['lng_inf'],
                lng_sup=request.form['lng_sup'])
            SESSION.add(new_dataset)
            SESSION.commit()
            if train:
                utils.save_image(label_path, "tree_cover", new_dataset.id)
            utils.save_image(os.path.join(UPLOAD_FOLDER, image_name), "image", new_dataset.id)
            return redirect(url_for('dashboard', success='true'))
        except Exception as err:
            print(err)
            raise(err)
            return redirect(url_for('dashboard', fail='true'))
    else:
        return render_template('adicionardados.html')


@app.route('/download-dataset')
def download_dataset():
    id_value = request.args.get('id')
    dataset = SESSION.query(Dataset).filter_by(id=int(id_value)).first()
    zipf = zipfile.ZipFile('temp/{0}.zip'.format(dataset.name), 'w',
                           zipfile.ZIP_DEFLATED)
    zipf.write(UPLOAD_FOLDER + dataset.image_name)
    if dataset.label_name != "":
        zipf.write(UPLOAD_FOLDER + "labels/" + dataset.label_name)
    zipf.close()
    return send_file("temp/{0}.zip".format(dataset.name),
                     mimetype="zip",
                     attachment_filename="{0}.zip".format(dataset.name),
                     as_attachment=True)

@app.route('/classificar-images')
def classify_images():
    classifier_id = request.args.get('classifier')
    dataset_first_id = request.args.get('first')
    dataset_last_id = request.args.get('last')
    datasert_first = SESSION.query(Dataset).filter_by(id=int(dataset_first_id)).first()
    classifier = SESSION.query(Classifier).filter_by(id=int(classifier_id)).first()
    model_path = classifier.model_path
    return_dict = {
        'lat_lng':  {
            'lat_inf': datasert_first.lat_inf,
            'lat_sup': datasert_first.lat_sup,
            'lng_inf': datasert_first.lng_inf,
            'lng_sup': datasert_first.lng_sup
        },
        'cover': utils.classify_images(model_path, dataset_first_id, dataset_last_id)
    }

    return json.dumps(return_dict)

if __name__ == "__main__":
    create_folders_if_not_exist()
    app.secret_key = 'FGV-EMAP 13410 Selva'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(host='0.0.0.0', port=8080, debug=False)
    # APP.run(host='192.168.25.177', port=9000, debug=False)
