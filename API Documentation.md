# THE TRIVIA API
This project is a Trivia application, that stores questions and generates quizzes. The API serves its client different representations of questions, can create and delete them and choose unasked questions, as to make quizzing not repetitive. This is the second project of the Fullstack Nanodegree at Udacity, with its focus on flask, TDD and endpointing.

All backend code follows PEP8 style guidelines.

### Pre-requisites and Local Development

Developers using this project should already have Python3, pip and node installed on their local machines.

### Backend

From the backend folder run `pip install requirements.txt`. All required packages are included in the requirements file.

To run the application run the following commands:

```
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```

These commands put the application in development and directs our application to use the `__init__.py` file in our flaskr folder. Working in development mode shows an interactive debugger in the console and restarts the server whenever changes are made. If running locally on Windows, look for the commands in the [Flask documentation](http://flask.pocoo.org/docs/1.0/tutorial/factory/).

The application is run on `http://127.0.0.1:5000/` by default and is a proxy in the frontend configuration.

#### Frontend

From the frontend folder, run the following commands to start the client:

```
npm install // only once to install dependencies
npm start 
```

By default, the frontend will run on localhost:3000.

### Tests

In order to run tests navigate to the backend folder and run the following commands:

```
createdb bookshelf_test
psql bookshelf_test < books.psql
python test_flaskr.py
```

All tests are kept in that file and should be maintained as updates are made to app functionality.

## API reference

### Getting Started

-   Base URL: At this stage the application is hosted only locally. The backend app is hosted at the default, `http://127.0.0.1:5000/`, which is set as a proxy in the frontend configuration.
-   Authentication: None.

### Error Handling

Errors are returned as JSON, like this:

>{  
'error': 404,
'message' 'resource not found'
}	

You can expect:
-	*400 bad request* if there is no JSON in the request body, when required
-	*404 resource not found*
-	*422 unprocessable entity* if JSON was recognized, but the keys were faulty

### Endpoints
**GET /categories** 
-	Returns a dictionary, where the key-value pairs represent individual categories as {'id': 'type'}

-	Example:

	`curl http://localhost:5000/categories`
>{
  "1": "Science", 
  "2": "Art", 
  "3": "Geography", 
  "4": "History", 
  "5": "Entertainment", 
  "6": "Sports"
}

**GET /questions?page=int** 
-	Returns a dictionary, with keys:
		-	**categories** dict, same as result from GET /categories
		-	**current_category** empty dict, not implemented
		-	**questions** list of dicts, every dict represents a question as described in POST /questions
		-	**total_questions** int
-	Questions are paginated with 10 per page, query accepts page=int, default 1

-	Example (shortened from 10 questions):

	`curl http://localhost:5000/questions?page=2`
> {
>   "categories": {
>     "1": "Science", 
>     "2": "Art", 
>     "3": "Geography", 
>     "4": "History", 
>     "5": "Entertainment", 
>     "6": "Sports"
>   }, 
>   "current_category": {}, 
>   "questions": [
>     {
>       "answer": "Agra", 
>       "category": 3, 
>       "difficulty": 2, 
>       "id": 15, 
>       "question": "The Taj Mahal is located in which Indian city?"
>     }, 
>     {
>       "answer": "Escher", 
>       "category": 2, 
>       "difficulty": 1, 
>       "id": 16, 
>       "question": "Which Dutch graphic artist\u2013initials M C was a creator of optical illusions?"
>     },  
>     {...}
>   ], 
>   "total_questions": 20
> } 

**GET /categories/<int: category_id>/questions** 

-	Takes the id of a category and returns a list of its question objects and the total amount of questions.
-	Example:

	`curl http://localhost:5000/categories/3/questions`
> {
>   "current_category": {}, 
>   "questions": [
>     {
>       "answer": "Lake Victoria", 
>       "category": 3, 
>       "difficulty": 2, 
>       "id": 13, 
>       "question": "What is the largest lake in Africa?"
>     }, 
>     {
>       "answer": "The Palace of Versailles", 
>       "category": 3, 
>       "difficulty": 3, 
>       "id": 14, 
>       "question": "In which royal palace would you find the Hall of Mirrors?"
>     }, 
>     {
>       "answer": "Agra", 
>       "category": 3, 
>       "difficulty": 2, 
>       "id": 15, 
>       "question": "The Taj Mahal is located in which Indian city?"
>     }
>   ], 
>   "total_questions": 20
> }


**POST /questions/search** 
-	Searches through the 'question' of each question object and returns a list of case-insensitive matches or empty if none found.
-	Accepts JSON:
> {
> 	'searchTerm': str
> }

-	Example:

	`curl -X POST -H 'Content-Type: application/json' http://localhost:5000/questions/search -d '{"searchTerm": "which dung beetle"}'`
> {
>   "current_category": {}, 
>   "questions": [
>     {
>       "answer": "Scarab", 
>       "category": 4, 
>       "difficulty": 4, 
>       "id": 23, 
>       "question": "Which dung beetle was worshipped by the ancient Egyptians?"
>     }
>   ], 
>   "total_questions": 20
> }

**POST /questions** 
-	Adds a new question to the database, with required keys as follows.
-	Accepts JSON:
> {
> 	'question': str,
> 	'answer': str,
> 	'category': int,
> 	'difficulty': int
> }

-	Example:

	`curl -X POST -H 'Content-Type: application/json' http://localhost:5000/questions -d '{"question": "What does the fox say?", "answer": "ring-ding-ding", "category": 1, "difficulty": 5}'`
> {
>   "success": true
> }

**POST /quizzes** 
-	Takes a list of previous question ids as well as a dict of quiz_category type and id, then returns a random unasked question object.
-	Accepts JSON:
> {
> 	'previous_questions': list of ints,
> 	'quiz_category': {'type': str, 'id': int}
> }

-	Example:

	`curl -X POST -H 'Content-Type: application/json' http://localhost:5000/quizzes -d '{"previous_questions": [23, 22], "quiz_category": {"type": "Science", "id": 1}}'`
> {
>   "question": {
>     "answer": "The Liver", 
>     "category": 1, 
>     "difficulty": 4, 
>     "id": 20, 
>     "question": "What is the heaviest organ in the human body?"
>   }
> }


**DELETE /questions/<int: question_id>** 
-	Deletes a question from the database by its id.
-	Returns 404 if no id found.

-	Example:

	`curl -X DELETE -H 'Content-Type: application/json' http://localhost:5000/questions/23`
> {
>   "success": true
> }
	
### Authors
Felix Weidenholzer

### Acknowledgments
The frontend as well as the setup come from the team at udacity, the documentation is excessively inspired by Coach Caryn and google search is great.