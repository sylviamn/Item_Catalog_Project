#Create database and tables
###################configuration##################
import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


###########user class###########
class User(Base):

	########table########
	__tablename__ = 'user'

	#####mapper#####
	name = Column(String(250), nullable = False)
	email = Column(String(250), nullable = False)
	picture = Column(String(250))
	id = Column(Integer, primary_key = True)


###########category class###########
class Category(Base):

	########table########
	__tablename__ = 'category'

	#####mapper#####
	name = Column(String(80), nullable = False)
	id = Column(Integer, primary_key = True)
	user_id = Column(Integer, ForeignKey('user.id'))
	user = relationship(User)
	
	@property
	def serialize(self):
		return{
			'name' : self.name,
			'id' : self.id,
		}

###############item class############
class Item(Base):

	########table########
	__tablename__ = 'item'

	#####mapper#####
	name = Column(String(80), nullable = False)
	id = Column(Integer, primary_key = True)
	description = Column(String(250))
	color = Column(String(80), nullable = False)
	price = Column(String(8))
	category_id = Column(Integer, ForeignKey('category.id'))
	category = relationship(Category)
	user_id = Column(Integer, ForeignKey('user.id'))
	user = relationship(User)
	
	@property
	def serialize(self):
		return{
			'name' : self.name,
			'description' : self.description,
			'id' : self.id,
			'price' : self.price,
			'color' : self.color,
		}


###################configuration##################
engine = create_engine('sqlite:///itemCatalog.db')
Base.metadata.create_all(engine)
