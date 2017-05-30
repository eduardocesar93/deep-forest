from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class Classifier(Base):
    __tablename__ = "classifier"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    dataset = Column(Integer, nullable=False)
    type_classifier = Column(String, nullable=False)
    optimization_method = Column(Integer, nullable=False)
    state = Column(Integer, nullable=False)
    accuracy = Column(String, nullable=False)
    password = Column(String)
    order_table = Column(Integer, nullable=False)
    locked = 0

    def __repr__(self):
        return "<Classifier(name={0}, dataset={1}, type_classifier={2},\
            optimization_method={3}, state={4})".format(
                self.name, self.dataset,
                self.type_classifier, self.optimization_method,
                self.state)

engine = create_engine("sqlite:///deep_forest.db")
Base.metadata.create_all(engine)
