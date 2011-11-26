from sqlalchemy import ForeignKey
from sqlalchemy import Column, Integer, String, Date, DateTime
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

def initializeBase(engine):
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)

class ObjectsModel(Base):
    __tablename__ = 'objects'
    
    id = Column(Integer, primary_key=True)
    score = Column(Integer(100), default=0)
    voted_users = association_proxy('users_objects', 'user')

    def __init__(self, **fields):
        self.__dict__.update(fields)

    def __repr__(self):
        return "<Objects('%s')>" % (self.id)

class UsersModel(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    voted_objects = association_proxy('users_objects', 'object')

    def __init__(self, **fields):
        self.__dict__.update(fields)

    def __repr__(self):
        return "<Users('%s', '%s', '%s')>" % (self.id)

class UsersObjectsModel(Base):
    __tablename__ = 'users_objects'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    object_id = Column(Integer, ForeignKey('objects.id'))
    vote = Column(Integer(1))
    
    user = relationship(UsersModel,
                        backref="users_objects")
    object = relationship(ObjectsModel,
                          backref="users_objects")

    def __init__(self, **fields):
        self.__dict__.update(fields)

    def __repr__(self):
        return "<UsersComments('%s', '%s', '%s')>" % (self.user_id,
                                                      self.object_id,
                                                      self.vote)    