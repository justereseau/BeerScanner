## Development

### With docker and docker compose

#### Make migration

```
docker compose run app python manage.py makemigrations drink_consumption
```

#### Migrate

```
docker compose run app python manage.py migrate
```

#### Generate Admin user

```
docker compose exec app python manage.py createsuperuser
```

#### Data import/export

```
docker compose run app ./manage.py dumpdata drink_consumption --format yaml > app.yaml
docker compose run app ./manage.py loaddata app.yaml
```
