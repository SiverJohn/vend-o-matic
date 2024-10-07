# How To Run
Running should be fairly simple if docker is installed on your system. Just use the
following command from the root directory.

`docker compose up -d`

Building the app docker container will take a minute as it installs all of the python
dependencies while ideally I would just share an already built image, for simplicity and
hopefully just works:tm: this is an okay method. The app on first run will initialize the
database tables and fill the tables with default values as requested on the assignment.

The app can then be interacted with by using the `test_curl.sh` file provided or by any
similar means. The app docker image is available to be interacted with at:

`http://localhost:3000`

Now I do have unit tests and if those want to be tested the `docker-compose.yaml` file
will need to be edited and the commented out parts of the app yaml will have to be added
back in and the current active command will need to be commented out. Then run the
following command:

`docker compose up -d && docker attach marigold-app-1`

At which point you will be dropped into the docker image and can then run:

`pytest`

The unit tests will then run on their own self contained database which will be created
and deleted for each test, which adds to the time taken. This guarantees isolation between
tests and is almost certainly overkill. It also preserves the standing database so no
quarters lost while running tests.

## Justification For Decisions Made
I chose Flask because it was mentioned as part of the tech stack used at the company and
because I am familiar with it, having used it in other projects.

I chose psycopg3 because I am familiar with two database frameworks and one of them is
postgres and the other is firebird 2.X and I was never going to write this in firebird
(also postgres is free and I believe also used in the tech stack). While if you look
through my commit history, I initially used SQLAlchemy, it was a bit messy to read and
realistically incredible overkill for an app like this. Also using psycopg3 allowed me to
show I know how to use SQL and that's probably not a bad thing.

I also chose to hit the entire code base with black and flake8 at the end. Black mainly
because I have had enough struggles with slightly different code environments and subtle
changes to automatic white spaces to know it's nice to have something manage that for you.
Flake8 while probably a bit overkill for this does provide some nice sanity checks even if
I don't agree with all of it's defaults.

## Organization of Code:
`vendOmatic.py`

I like keeping my top level files relatively simplistic, it just creates the flask app,
registers the blueprints and executes the flask app if called.

`blueprints.py`

Used to compartmentalize handling requests from clients and containing the endpoints. Does
a little bit of logic handling in checking sufficient inventory, and coins for inventory
otherwise offloads most compute to:

`datafuncs.py`

Contains the meat of the program including some helper functions for me to set up the
databases, but also the important functions that interact with the database in order to
check inventory stock, quarter in the machine, etc.

In general if possible I tend to try and break up code into subunits of does one thing and
this outline felt the best. If I were to break if further, I'd put the helper functions in
their own file, but because I used them in both the vendOmatic file and testing; I left it
together (also requires less searching through pages for whomever has to read this).

## Database Schema Choice
Honestly I recognize my database layout is overkill. I could easily have gotten away with
one table giving coins some unique id. I didn't need to name the drinks or anything of
that nature, but it felt sad not to and it adds a bit of personal touch so I hope I can be
indulged for a little bit of extravagance. I also like thinking about how things might be
used in the future and recording how many coins are in the vending machine for purchases
and adding in a column to later add in how many of each item has been sold is in line with
that philosophy. A little bit of "future proofing" if it were.
