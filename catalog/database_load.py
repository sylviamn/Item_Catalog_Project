# Load data into itemCatalog.db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User

engine = create_engine('sqlite:///itemCatalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()


########## Dummy User##########
User1 = User(name="John Doe", email="johndoe@dummyuser.com")
session.add(User1)
session.commit()

######## Skate Deck Category########
category1 = Category(name = "Skate Deck", user_id=1)
session.add(category1)
session.commit()

item1 = Item(name = "Skate Deck 1", description = "Bamboo skate deck", color = "Blue", price = "$59.99", category = category1, user_id=1)
session.add(item1)
session.commit()

item2 = Item(name = "Skate Deck 2", description = "Carnival skate deck", color = "Purple", price = "$45.99", category = category1, user_id=1)
session.add(item2)
session.commit()

item3 = Item(name = "Skate Deck 3", description = "Mountain skate deck", color = "Green", price = "$40.99", category = category1, user_id=1)
session.add(item3)
session.commit()

######## Skate Trucks Category########
category2 = Category(name = "Skate Trucks", user_id=1)
session.add(category2)
session.commit()

item4 = Item(name = "Skate Trucks 1", description = "Bamboo skate trucks", color = "Blue", price = "$29.99", category = category2, user_id=1)
session.add(item4)
session.commit()

item5 = Item(name = "Skate Trucks 2", description = "Carnival skate trucks", color = "Purple", price = "$25.99", category = category2, user_id=1)
session.add(item5)
session.commit()

item6 = Item(name = "Skate Trucks 3", description = "Mountain skate trucks", color = "Green", price = "$20.99", category = category2, user_id=1)
session.add(item6)
session.commit()

######## Skate Wheels Category########
category3 = Category(name = "Skate Wheels", user_id=1)
session.add(category3)
session.commit()

item7 = Item(name = "Skate Wheels 1", description = "Bamboo skate wheels", color = "Blue", price = "$25.99", category = category3, user_id=1)
session.add(item7)
session.commit()

item8 = Item(name = "Skate Wheels 2", description = "Carnival skate wheels", color = "Purple", price = "$20.99", category = category3, user_id=1)
session.add(item8)
session.commit()

item9 = Item(name = "Skate Wheels 3", description = "Mountain skate wheels", color = "Green", price = "$15.99", category = category3, user_id=1)
session.add(item9)
session.commit()

######## Skate Hardware Category########
category4 = Category(name = "Skate Hardware", user_id=1)
session.add(category4)
session.commit()

item10 = Item(name = "Silver Skate Bearings", description = "Silver bearings", color = "Silver", price = "$14.99", category = category4, user_id=1)
session.add(item10)
session.commit()

item11 = Item(name = "Black Skate Bearings", description = "Black bearings", color = "Black", price = "$12.99", category = category4, user_id=1)
session.add(item11)
session.commit()

item12 = Item(name = "Skate Toolkit", description = "Basic toolkit for skateboard", color = "Silver", price = "$9.99", category = category4, user_id=1)
session.add(item12)
session.commit()

######## Skate Accessories Category########
category5 = Category(name = "Skate Accessories", user_id=1)
session.add(category5)
session.commit()

item13 = Item(name = "Skate Helmet", description = "Helmet for head protection", color = "Black", price = "$25.99", category = category5, user_id=1)
session.add(item13)
session.commit()

item14 = Item(name = "Skate Knee Pads", description = "Pads for knee protection", color = "Black", price = "$18.99", category = category5, user_id=1)
session.add(item14)
session.commit()

item15 = Item(name = "Skate Elbow Pads", description = "Pads for elbow protection", color = "Black", price = "$15.99", category = category5, user_id=1)
session.add(item15)
session.commit()


print "added items!"
