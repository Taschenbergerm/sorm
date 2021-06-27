from sorm_.sorm_ import *

engine = create_engine("sqlite:////home/marvin/sorm.db")
print(Base.metadata.create_all(engine))
Session = sessionmaker(bind=engine)
languages = [Languages(name=name) for name in "Python Go SQL".split(" ")]

labels = [Labels(name=name) for name in "Important Pip".split(" ")]
codesnippet = Snippets(name="First Snippet", code= "import this", language_id=1)

session = Session()
session.add_all(languages + labels)
session.add(codesnippet)
session.commit()
print("Done")

