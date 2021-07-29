## Development

### With docker and docker-compose

#### Make migration

```
docker-compose run web python manage.py makemigrations drink_consumption
```

#### Migrate

```
docker-compose run web python manage.py migrate
```

#### Generate Admin user

```
docker-compose run web python manage.py createsuperuser
```

#### Data import/export

```
docker-compose run web ./manage.py dumpdata drink_consumption --format yaml > app.yaml
docker-compose run web ./manage.py loaddata app.yaml
```
