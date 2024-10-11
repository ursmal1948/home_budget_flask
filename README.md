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
## Tests
Each key component of the application (__models, repositories, services and routes__) is tested to ensure functionality and compliance to the expected behaviour. Testing is carried out with pytest and unittest mostly using object and function mocking. The test coverage is over 80%, ensuring that the application performs reliably under various scenarios. 