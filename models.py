# pylint: disable=C0111
# pylint: disable=C0103
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
BASE = declarative_base()


class Classifier(BASE):
    __tablename__ = "classifier"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    dataset_first = Column(Integer, ForeignKey("dataset.id"), nullable=False)
    type_classifier = Column(String, nullable=False)
    optimization_method = Column(Integer, nullable=False)
    state = Column(Integer, nullable=False)
    accuracy = Column(String, nullable=False)
    password = Column(String)
    order_table = Column(Integer, nullable=False)
    locked = 0

    def __repr__(self):
        return "<Classifier(name={0}, dataset={1}, type_classifier={2},\
            optimization_method={3}, state={4})>".format(
                self.name, self.dataset_first,
                self.type_classifier, self.optimization_method,
                self.state)


class Dataset(BASE):
    __tablename__ = "dataset"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    train = Column(Integer, nullable=False)
    image_name = Column(String, nullable=False)
    label_name = Column(String, nullable=True)

    def __repr__(self):
        return "<Dataset(name={0}, train={1})>".format(self.name, self.train)


ENGINE = create_engine("sqlite:///deep_forest.db")
BASE.metadata.create_all(ENGINE)
