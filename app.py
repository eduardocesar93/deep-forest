# -*- coding: utf-8 -*-
import os
from flask import Flask, request, redirect, url_for,\
    render_template, flash, current_app, send_from_directory
from werkzeug.utils import secure_filename
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Classifier
import json

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


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/deletar-classificador")
def delete_classifier():
    id_value = request.args.get('id')
    classifier = session.query(Classifier).filter_by(id=int(id_value)).first()
    password = request.args.get('password')
    if classifier.password == password:
        session.delete(classifier)
        session.commit()
        return "true"
    else:
        return "false"


@app.route("/dashboard")
def dashboard():
    classifiers = session.query(Classifier).order_by('order_table').all()
    for classifier in classifiers:
        if classifier.password != "":
            classifier.locked = 1
        else:
            classifier.locked = 0
    return render_template('dashboard.html', classifiers=classifiers)


@app.route("/adicionar-classificador", methods=['POST', 'GET'])
def adicionar_classificador():
    if request.method == 'POST':
        try:
            order = session.query(Classifier).count()
            password = ""
            if request.form["password"] == "yes":
                password = request.form["password_value"]
            new_classifier = Classifier(
                name=request.form['name'],
                dataset=int(request.form['dataset']),
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
        return render_template('adicionarclassificador.html')


@app.route("/atualizar-classificadores")
def atualizar_classificadores():
    classifiers = request.args.get('values')
    classifiers_dict = json.loads(classifiers)
    classifiers = session.query(Classifier).all()
    print(classifiers)
    for classifier_item in classifiers_dict:
        for classifier in classifiers:
            if classifier.id == int(classifier_item['id']):
                classifier.name = classifier_item['classificador']
                classifier.order_table = int(classifier_item['order'])
                session.add(classifier)
                session.commit()
    return "true"


@app.route('/upload', methods=['get'])
def upload():
    state = "danger"
    message = "Um erro ocorreu ao fazer Upload do arquivo"

    if 'file' in request.files:
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            state = "success"
            message = "A questão foi salva com sucesso"
    if 'question' in request.files:
        file = request.files['question']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join('questions/', filename))
            state = "success"
            message = "A questão foi salva com sucesso"
            flash(message, state)
            return redirect(url_for('submeter'))

    flash(message, state)
    return redirect(url_for('submeter'))


@app.route('/delete')
def delete():
    file = request.args.get('file')
    dir = os.path.join(current_app.root_path, 'questions/')
    return send_from_directory(directory=dir, filename=file)


@app.route('/download')
def download():
    file = request.args.get('file')
    dir = os.path.join(current_app.root_path, 'questions/')
    return send_from_directory(directory=dir, filename=file)


if __name__ == "__main__":
    app.secret_key = 'FGV-EMAP 13410 Selva'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(host='0.0.0.0', port=port, debug=True)
