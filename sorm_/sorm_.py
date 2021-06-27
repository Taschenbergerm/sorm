from typing import Dict, List
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship
import pandas as pd

Base = declarative_base()


class Languages(Base):
    __tablename__ = "Languages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)


class Labels(Base):
    __tablename__ = "Labels"

    id = Column(Integer, primary_key=True,  autoincrement=True)
    name = Column(String, nullable=False)


class Snippets(Base):
    __tablename__ = "Snippets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    language_id = Column(Integer, ForeignKey(Languages.id))
    name = Column(String, nullable=False)
    code = Column(Text)


class LabelMapp(Base):
    __tablename__ = "LabelMapp"

    id = Column(Integer, primary_key=True)
    snippet_id = Column(Integer,ForeignKey(Snippets.id))
    label_id = Column(Integer,ForeignKey(Labels.id))


def get_storage(url):
    engine = create_engine(url)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


class Storage:

    def __init__(self, url):
        self.url = url
        session = get_storage(url)
        session.close()

    def create(self, mode, name, code) -> None:
        session = get_storage(self.url)
        language_id = session.query(Languages.id).filter_by(name=mode).first()[0]
        snippet = Snippets(language_id=language_id, name=name, code=code)
        session.add(snippet)
        session.commit()
        session.close()

    def delete(self, id):
        session = get_storage(self.url)
        session.query(Snippets).filter(Snippets.id==id).delete()
        session.commit()
        session.close()

    def update(self, mode, name, code) -> None:
        session = get_storage(self.url)
        snippet = session.query(Snippets).filter_by(name=name).first()
        snippet.name = name
        snippet.code = code
        session.commit()
        session.close()

    def save(self, name, code) -> None:
        session = get_storage(self.url)
        snippet = Snippets(name=name, code=code)
        session.add(snippet)
        session.commit()
        session.close()

    def query_snippet(self, id) -> List[Snippets]:
        session = get_storage(self.url)
        res = session.query(Snippets.code, Snippets.name, Snippets.id).filter_by(id=id).all()
        session.close()
        return res

    def query_available_snippets_by_id(self, id) -> pd.DataFrame:

        session = get_storage(
            self.url
        )
        df = pd.read_sql(session.query(Snippets).filter(Snippets.language_id == id).statement, session.bind)
        session.close()
        return df

    def query_languages(self) -> Dict[int, str]:
        session = get_storage(self.url)
        res = {id:name for id, name in session.query(Languages.id, Languages.name)}
        session.close()
        return res
