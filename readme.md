# Tech Challenge - Phase 2

Aníbal - Leonardo

##### Pre-requisites
* Docker
* docker-compose
* python3.10

## Run locally

### Step 1 - configure database
You'll need to run the docker-compose.yml in order to have postgres running in your machine:

```shell
docker-compose up -d
```

After that command, you'll have postgres running and responding on port 5432.
Now we just need to run the migrations in order to create the database.

```shell
alembic upgrade head
```

### Step 2 - running the application
Before running the application we need to ensure we have all python dependencies.

```shell
pip install -r requirements.txt
```

Now we just need to run our API on uvicorn

```shell
uvicorn app.app:app --reload 
```

With that our application we'll be up and responding on port 8000