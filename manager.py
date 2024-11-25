from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

from dotenv import load_dotenv
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

from models import ServiceType, init_db, Service, User


class Manager:
    def __init__(self):
        engine = create_engine(DATABASE_URL)
        session = sessionmaker(bind=engine)
        self.session = session()

        init_db(engine)
        self.add_user(835005258, "danis", "admin")

    def add_service_type(self, title: str, user_id, image: str, with_services):
        self.session.add(ServiceType(title=title, user_id=user_id, image=image, is_with_services=with_services))
        self.session.commit()

    def add_service(self, service_type_id: int, title: str):
        service = Service(title=title, service_type_id=service_type_id)
        self.session.add(service)
        self.session.commit()

    def add_user(self, user_id, name, role="user"):
        first_time = self.get_user(user_id) is None
        if first_time:
            user = User(id=user_id, name=name, role=role)
            self.session.add(user)
            self.session.commit()
        return first_time

    def get_user(self, user_id):
        user = self.session.query(User).filter_by(id=user_id).first()
        return user

    def get_user_service_types(self, user_id):
        return self.session.query(ServiceType).filter_by(user_id=user_id).all()

    def get_service_types(self):
        return self.session.query(ServiceType).all()

    def get_service_type(self, service_type_id):
        return self.session.query(ServiceType).filter_by(id=service_type_id).first()

    def get_service(self, service_id):
        return self.session.query(Service).filter_by(id=service_id).first()

    def get_services(self, service_type_id):
        return self.session.query(Service).filter_by(service_type_id=service_type_id).all()

    def add_supplier(self, service_id, sup):
        service = self.session.query(Service).filter_by(id=service_id).first()
        service.suppliers.append(sup)
        self.session.commit()

    def add_sup(self, service_type_id, sup):
        service = self.session.query(ServiceType).filter_by(id=service_type_id).first()
        service.suppliers.append(sup)
        self.session.commit()
