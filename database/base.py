from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database

from database.models import Vacancy, Base


class VacancyDB:

    def __init__(self, url):
        self.url = url


    def add_salary(self, db_item):
        self.engine = create_engine(self.url)
        # if not database_exists(self.engine.url):
        #     create_engine(self.engine.url)
        Base.metadata.create_all(self.engine)

        db_session = sessionmaker(bind=self.engine)
        session = db_session()

        session.add(db_item)
        session.commit()
        session.close()