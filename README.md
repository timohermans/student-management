# Student management in Flask

So I build this management app to test how quickly I could set something up with Flask.
Somewhere along the line I was satisfied with my Python skills and decided to abandon this whole project and build everything in my existing [C# student management project](https://github.com/timohermans/StudentProgress).

This app can connect to the Canvas API, so it has some pretty valuable code to reuse.

## Installation

Installation is pretty straightforward.

### Prerequisites

We need mainly these things:

- Python 3 (was writting in 3.10, but 3.11 works as well)
- [Poetry](https://python-poetry.org) (`pip install poetry`)

When you have these things, setting up the project takes little time

### Install dependencies

Installing dependencies can be done with poetry.

```shell
poetry install
```

### Create a .env file

To create the .env file, copy and paste the `.env.example` file and call it `.env`.
Fill in missing values, especially `SECRET_KEY`.
The app won't run without it.

### Setup the database

The database runs on sqlite, so no need to pull out any connectionstring skills. Do the following in a terminal.

- Run `poetry shell` in the root directory. The virtual environment will be loaded for the project (yay, poetry)
- Run `flask shell` in the root directory. This will open a Python shell with Flask loaded as if it was run with `flask dev` (yay, flask)
- Import the init_db function by first executing `from student.database import init_db` and then execute init_db by executing `init_db()`

There, now we're done.

## Running the application

To run the application, first make sure you loaded the virtual environment by running `poetry shell` and then `flask run`.

Alternatively, you can run `poetry run flask run`.
