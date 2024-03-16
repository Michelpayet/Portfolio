# What To Cook
#### Video Demo:  <https://youtu.be/IuiBIEv_Luo>
#### Description:

I built this app because I found it to be fun and it was the best way to practice the knowledge gained from CS50.

#### !-Before you use the app, Please get a free API key from <https://spoonacular.com/food-api>.-!

I went with flask because it is so easy to set up.
I used SQLite so we can add user accounts and allow them to save their favorite recipes.\
I did one db file that contains 2 table, one for user's account/hashed password, and the other for their saved recipes.\
We have the templates folder for all the html files.\
Inside the static folder we have some images like the logo I did using Canva, a background and then a css and js folder.\
The css folder contains the css file for all the html.
The js folder contains a javascript file just for a bit of front end functions.\
We have the main app.py file where most of the backend function lives.\
I also added helpers.py so we can call some functions from it that we will use often such as cheching the name of the active user so we can then display it on the navbar.

* You have to register to be able to use the app.
Once registered, you will be redirected to the login page.
* Once logged in, you can log out when you want and the logout button should be displayed at the upper right of the navbar.
* Once you've logged, you will be rerdirected to your account where your saved recipes will be shown.
* To search for recipes, click on the WTC icon on the upper left of the page where you'll be redirected to the main page.
* We're using a complex search so you can write anything food related and you'll most likely get some results.
* Upon clicking on 'view' button for a recipe, you can see the info about it and you can also save it to your profile.
* To go to your profile, you simply have to click on your username diplayed on the navbar.
* Once on your profile, your username will display a bit larger and if you click on it from there, you will be prompt with deletion of your profile (simply close it if you do not wish to delete it).
* If you view a recipe from your saved ones on your   profile, you can remove it by selecting the bin icon.

Thank you!

Michel Payet


