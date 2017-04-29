from sql import *

class Event(Base):
    __tablename__ = "events"
    id           = Column(Integer, primary_key=True)
    name         = Column(String(255))
    coreid       = Column(String(255))
    data         = Column(String(255))
    published_at = Column(DateTime)

    
