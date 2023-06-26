# CS50 Final Project: SmartFit
## Video Demo:  <https://youtu.be/Wa6rY7OiPxE>
## **Description**
### SmartFit is an online exercise resource built using Python (Flask), Javascript and SQL. Users can create an account, login and start searching for their next exercise. Data provided by the ExerciseDB API gives you access to over 1300 exercises with individual exercise data and detailed animated demonstrations.
---
### **Search**
####
- A search system comprising of filter categories like 'body part', 'equipment' and a search bar has been implemented, allowing users to fine-tune their search preferences.
- Filter tags have been stylised to look like rounded pills, which is generally a good design choice.
- On clicking, these are activated. Choosing more than one tag under a given category will generally display more results, however choosing tags from different categories will filter results, since an exercise can have atmost one tag from each category.
- The category 'targeted muscle' has been left out of search filters since it is a relatively larger set of tags, and body parts are easier to identify.
- Don't worry though, because targeted muscle is still displayed for each exercise in the search results. If no filters are activated, then a list of all exercises is displayed.
---
### **UI/UX**
####
- UI/UX has been given due priority in this web application. A 'pastel' color theme was chosen. Bootstrap is used heavily, along with some custom CSS.
- Exercises are displayed one after another in a 'card' format, each card providing important details about said exercise in an attractive manner. On hover, the selected card expands in size to highlight itself. These cards also include a GIF demonstration of the given exercise. On clicking any of the cards, users can access the unique page of the exercise which provides some additional info and lets users interact with the exercise.
---
### **Interaction**
####
- Regarding interaction, a 'favorites' system has been implemented; users can add exercises to their favorites and view them on the dashboard page by clicking a heart icon next to the name of the exercise.
- Also, a rating/review system based on exercise difficulty has been created to make differentiating between exercises easier. Users can leave a rating and optionally add a review for any exercise. Users may also delete their original rating/review and add a new one. User reviews and ratings can be found on the unique exercise page.
- Details like overall rating, number of favorites, favorited/unfavorited, number of ratings, exercise tags, etc. are found on both the exercise card and page.
---
### **The Code**
####
- The PRG (Post/Redirect/Get) pattern was implemented in Flask to prevent form resubmissions.
- Javascript (mostly JQuery) was used in handling the frontend changes while favoriting/unfavoriting and rating an exercise. It was also used to dynamically colour the badges based on overall difficulty rating.
- SQL database has been used to store user details, user ratings and reviews, user favorited exercises, unique exercise details, etc.
- HTML and Jinja (templating) were used to design the websites.
---
### **Additional**
####
- Functionality to change password has been added. Users are also made aware of empty searches.
- The difficulty rating is from 1 (very easy) to 5 (very hard), and is also color based. Overall rating for unrated exercises has been preset to 0; this will only change upon receiving a rating.
- Login, register, navbar and form validation have been inspired by C$50 Finance.
- **Creating an account tends to take some time, since by default the database needs to set the favorite 'state' of every exercise to unfavorited. Give it about ~1 minute. This extra step reduces search time in the long run.**
---
### **Closing Thoughts**
#### This project was daunting at first, but turned out to be very enjoyable to make! I learnt a lot not only while making the project but throughout this course! Thank you to Professor David J. Malan and all the others who helped make CS50 possible ❤️.

