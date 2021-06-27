from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey

engine = create_engine('sqlite:///:memory:', echo=True)
Base = declarative_base()


class A(Base):
    __tablename__  = "table1"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)


class B(Base):
    __tablename__ = "table2"

    id = Column(Integer, primary_key=True, autoincrement=True)
    aid = Column(Integer, ForeignKey(A.id))

a = A(id = 1, name="A")

b = B(id = 1 , aid=1)
b2 = B(id = 2 , aid=1)


if __name__ == '__main__':
    print(Base.metadata.create_all(engine))
