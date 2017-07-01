# pylint: disable=C0111
# pylint: disable=W0702
import os
import zipfile
import json
import time
from flask import Flask, request, redirect, url_for,\
    render_template, send_file
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import BASE, Classifier, Dataset

UPLOAD_FOLDER = 'images/'
ALLOWED_EXTENSIONS = set(['tif', 'tiff'])

PORT = int(os.getenv('VCAP_APP_PORT', 8080))
APP = Flask(__name__)
APP.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ENGINE = create_engine("sqlite:///deep_forest.db", echo=True)
BASE.metadata.bind = ENGINE
SESSION = sessionmaker(bind=ENGINE)()

def secure_filename(filename):
    return filename # TODO


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def zipdir(path, ziph):
    for root, _, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))


def current_milli_time():
    return int(round(time.time() * 1000))


@APP.route("/")
def index():
    return render_template('index.html')


@APP.route("/deletar-classificador")
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


@APP.route("/deletar-dataset")
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


@APP.route("/dashboard")
def dashboard():
    classifiers = SESSION.query(Classifier).order_by('order_table').all()
    datasets = SESSION.query(Dataset).all()
    for classifier in classifiers:
        if classifier.password != "":
            classifier.locked = 1
        else:
            classifier.locked = 0
    return render_template('dashboard.html', classifiers=classifiers,
                           datasets=datasets)


@APP.route("/visualizacao")
def visualization():
    return render_template('visualizacao.html')


@APP.route("/adicionar-classificador", methods=['POST', 'GET'])
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
                dataset_last=int(request.form['dataset_last']),
                type_classifier=request.form['type_classifier'],
                optimization_method=int(request.form['optimization_method']),
                password=password,
                state=1,
                accuracy="-",
                order_table=order)
            SESSION.add(new_classifier)
            SESSION.commit()
            return redirect(url_for('dashboard', success='true'))
        except:
            return redirect(url_for('dashboard', fail='true'))
    else:
        datasets = SESSION.query(Dataset)\
            .filter(Dataset.label_name != "").all()
        return render_template('adicionarclassificador.html',
                               datasets=datasets)


@APP.route("/atualizar-classificadores")
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


@APP.route('/adicionar-dataset', methods=['POST', 'GET'])
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
                label_image.save(os.path.join(UPLOAD_FOLDER + '/labels',
                                              label_name))
            else:
                label_name = ""
            new_dataset = Dataset(
                name=request.form['name'],
                year=int(request.form['year']),
                train=train,
                image_name=image_name,
                label_name=label_name)
            SESSION.add(new_dataset)
            SESSION.commit()
            return redirect(url_for('dashboard', success='true'))
        except:
            return redirect(url_for('dashboard', fail='true'))
    else:
        return render_template('adicionardados.html')


@APP.route('/download-dataset')
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


if __name__ == "__main__":
    APP.secret_key = 'FGV-EMAP 13410 Selva'
    APP.config['SESSION_TYPE'] = 'filesystem'
    APP.run(host='0.0.0.0', port=9090, debug=False)
    # APP.run(host='192.168.25.177', port=9000, debug=False)
