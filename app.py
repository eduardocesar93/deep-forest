# -*- coding: utf-8 -*-
import os
from flask import Flask, request, redirect, url_for,\
    render_template, flash, current_app, send_file
from werkzeug.utils import secure_filename
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Classifier, Dataset
import zipfile
import json
import time

UPLOAD_FOLDER = 'images/'
ALLOWED_EXTENSIONS = set(['tif', 'tiff'])

port = int(os.getenv('VCAP_APP_PORT', 8080))
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

engine = create_engine("sqlite:///deep_forest.db", echo=True)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def zipdir(path, ziph):
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))


def current_milli_time():
    return int(round(time.time() * 1000))


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/deletar-classificador")
def delete_classifier():
    id_value = request.args.get('id')
    classifier = session.query(Classifier).filter_by(id=int(id_value)).first()
    password = request.args.get('password')
    try:
        if classifier.password == password:
            session.delete(classifier)
            session.commit()
            return "true"
        else:
            return "false"
    except:
        return "false"


@app.route("/deletar-dataset")
def delete_dataset():
    id_value = request.args.get('id')
    dataset = session.query(Dataset).filter_by(id=int(id_value)).first()
    try:
        image_name = dataset.image_name
        label_name = dataset.label_name
        session.delete(dataset)
        session.commit()
        if image_name != "":
            os.remove(os.path.join(UPLOAD_FOLDER, image_name))
        if label_name != "":
            os.remove(os.path.join(UPLOAD_FOLDER + '/labels', label_name))
        return "true"
    except:
        return "false"


@app.route("/dashboard")
def dashboard():
    classifiers = session.query(Classifier).order_by('order_table').all()
    datasets = session.query(Dataset).all()
    for classifier in classifiers:
        if classifier.password != "":
            classifier.locked = 1
        else:
            classifier.locked = 0
    return render_template('dashboard.html', classifiers=classifiers,
                           datasets=datasets)


@app.route("/visualizacao")
def visualization():
    return render_template('visualizacao.html')


@app.route("/adicionar-classificador", methods=['POST', 'GET'])
def add_classifier():
    if request.method == 'POST':
        try:
            order = session.query(Classifier).count()
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
            session.add(new_classifier)
            session.commit()
            return redirect(url_for('dashboard', success='true'))
        except:
            return redirect(url_for('dashboard', fail='true'))
    else:
        datasets = session.query(Dataset)\
            .filter(Dataset.label_name != "").all()
        return render_template('adicionarclassificador.html',
                               datasets=datasets)


@app.route("/atualizar-classificadores")
def update_classifiers():
    classifiers = request.args.get('classifiers')
    classifiers_dict = json.loads(classifiers)
    classifiers = session.query(Classifier).all()
    for classifier_item in classifiers_dict:
        for classifier in classifiers:
            if classifier.id == int(classifier_item['id']):
                classifier.name = classifier_item['classificador']
                classifier.order_table = int(classifier_item['order'])
                session.add(classifier)
                session.commit()

    datasets = request.args.get('datasets')
    datasets_dict = json.loads(datasets)
    datasets = session.query(Dataset).all()
    for dataset_item in datasets_dict:
        for dataset in datasets:
            if dataset.id == int(dataset_item['id']):
                dataset.name = dataset_item['dataset']
                session.add(dataset)
                session.commit()

    return "true"


@app.route('/adicionar-dataset', methods=['POST', 'GET'])
def add_dataset():
    if request.method == 'POST':
        try:
            if 'image' in request.files:
                image = request.files['image']
                if image.filename == "":
                    raise("No image Exception")
            else:
                raise("No Image Exception")
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
                    raise("No Image Exception")
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
            session.add(new_dataset)
            session.commit()
            return redirect(url_for('dashboard', success='true'))
        except:
            return redirect(url_for('dashboard', fail='true'))
    else:
        return render_template('adicionardados.html')


@app.route('/download-dataset')
def download_dataset():
    id_value = request.args.get('id')
    dataset = session.query(Dataset).filter_by(id=int(id_value)).first()
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
    app.secret_key = 'FGV-EMAP 13410 Selva'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(host='0.0.0.0', port=port, debug=True)
    # app.run(host='192.168.25.177', port=9000, debug=False)
