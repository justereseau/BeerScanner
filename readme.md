# BeerScanner

## Fonctionnements

### Top Players

Tout les comptes faisant partit du groupe `players` sont affichés dans la liste des plus gros buveurs.

### Websocket

La communication bidirectionnelle est assurée par un websocket. Celui-ci utilise [Channel Layer](https://channels.readthedocs.io/en/latest/topics/channel_layers.html) et Redis.

## Development

### With docker and docker compose

#### Make migration

```
docker compose exec app python manage.py makemigrations drink_consumption
```

#### Migrate

```
docker compose exec app python manage.py migrate
```

#### Generate Admin user

```
docker compose exec app python manage.py createsuperuser
```

#### Data import/export

```
docker compose exec app ./manage.py dumpdata drink_consumption --format yaml > app.yaml
docker compose exec app ./manage.py loaddata app.yaml
```
