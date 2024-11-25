from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, JSON, ARRAY
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String)
    role = Column(String)  # 'user', 'supplier', 'admin'


class ServiceType(Base):
    __tablename__ = 'service_type'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    user_id = Column(Integer, ForeignKey('user.id'))

    user = relationship("User")
    services = relationship("Service", back_populates="service_type")
    image = Column(String, nullable=False)

    is_with_services = Column(Boolean, nullable=False, default=True)
    suppliers = Column(MutableList.as_mutable(JSON), nullable=False, default=list)


class Service(Base):
    __tablename__ = 'service'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    service_type_id = Column(Integer, ForeignKey('service_type.id'))
    service_type = relationship("ServiceType", back_populates="services")
    suppliers = Column(MutableList.as_mutable(JSON), nullable=False, default=list)


def init_db(engine):
    # Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
