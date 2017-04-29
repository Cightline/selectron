from sql import *

class User(Base):
    __tablename__ = "users"
    id           = Column(Integer, primary_key=True)
    username       = Column(String(255))
    password       = Column(String(255))

    
