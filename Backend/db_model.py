from sqlalchemy import MetaData, Column, Integer, String, DateTime, ForeignKey 
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

from datetime import datetime


metadata = MetaData()
Base = declarative_base(metadata = metadata)

# One feature set to have multiple children which represent sepparate features
class QR_codes(Base):
    __tablename__ = 'Feature_set_table'

    ID = Column(Integer, primary_key = True, unique = True, autoincrement = True)
    created = Column(DateTime, default = datetime.now)
    last_updated = Column(DateTime, default = datetime.now, onupdate = datetime.now)
    unique_code = Column(String(30), unique = True)