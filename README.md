# Item_Catalog_Project
This project runs an application that interacts with a database containing categories and items. All users can view categories and items, but only users with the right access can create/update/delete.

##Get application running:
1. Open Git Bash
2. Run ```cd fullstack/vagrant```
3. Run ```vagrant up```
4. Run ```vagrant ssh```
5. Run ```cd /vagrant/catalog```
6. Run ```python database_setup.py```
7. Run ```python database_load.py```
8. Run ```python finalproject.py```
9. Go to localhost:2200/ on web browser

###Authentication/Authorization:
*Must be logged in to your Google account to see/use Create/Update/Delete features.
*You can only create/edit your own categories and items within.

###JSON endpoint tests:
* List of Categories
..* localhost:2200/Category/JSON
* List of Items in a Category
..* localhost:2200/Category/1/JSON
* List of one Item
..* localhost:2200/Category/1/1/JSON
