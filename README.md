# 💵 HOME BUDGET APPLICATION  💵

## API DOCUMENTATION - POSTMAN 
[POSTMAN DOCUMENTATION](https://documenter.getpostman.com/view/36229565/2sAXxPBZBW)

## Project Description
### This project is a Home Budget Application developed using Flask framework for web functionality and SQLAlchemy for database integration. It allows user to:
- Add,read, update and delete income and expenses.
- Monitor and control their budget.
- Set percentage for specific category they want to spend money on and compare it with actual spendings.
- Set and manage recurring transactions based on intervals defined by user. 

### Using this application, users can easily manage their personal finances and track recurring transactions to ensure they are in control of their budget.

## Registration, activation and security

### Registration process with both functionalities for creation and activation. Once user has created his account, an email is sent to him with activation token (of certain expiration time), which is required for successful activation of his account. 
### 
### Security is done with flask-preatorian to ensure that only authorized individuals can access certain functionalities.
### JWT authentication and authorization - users receive a token when logging, which is required for accessing protected endpoints. Token expiration and refresh mechanisms are implemented to maintain security over time. 


## Docker & Containerization
This project uses Docker for containerization, making it easy to set up and run application in isolated environments. The system includes several services:
- Flask: runs the core web application with Gunicorn
- MySQL: provides database storage for application data
- Nginx: for handling http requests and routing them to Flask app

Useful commands to execute:

For building and running project
```
docker-compose up -d --build
```
It will build and run the project in detached mode, allowing developer to use terminal.

To see the logs of containers
```
docker-compose logs -f
```
To stop and remove all the containers
```
docker-compose down
```

## Migrations
I have used flask-migrate in order to simplify creation of tables and separate its logic from the logic of managing and manipulating data in database. 
### 
Command for applying migration in container of my flask app (in app package):
```
flask --app main.py db upgrade
```
It creates all the tables, making the database functional and ready for programmer to work with the app.

## Tests
Each key component of the application (__models, repositories, services and routes__) is tested to ensure functionality and compliance to the expected behaviour. Testing is carried out with pytest and unittest mostly using object and function mocking. The test coverage is over 80%, ensuring that the application performs reliably under various scenarios.


<div align="center">
    <img src="coverage.svg" alt="coverage">
</div>
