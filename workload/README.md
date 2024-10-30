```
alembic revision --autogenerate -m "Описание миграции"
alembic upgrade head 
```

```
docker run --name workload-db -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password -e POSTGRES_DB=workload -p 5432:5432 --net workload_network -d postgres

docker build -t workload .
docker run -it --name workload  -p 8001:8000 workload

```