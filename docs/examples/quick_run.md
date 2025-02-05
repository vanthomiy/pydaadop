# Quick Setup Run

!!! Info
    After the [Quick Auto Setup](./quick_auto.md) or setting up the project manually via the [Quick Manual Setup](./quick_manual.md) you should be able to test and run the setup.

!!! Warning
    Make sure that you have docker installed in your environment.
    Else follow the instructions on the [Docker website](https://docs.docker.com/get-docker/).

Run the docker-compose file to create docker containers. With this command the `example.env` file is used to set the environment variables and a build is forced.

```bash
docker-compose --env-file example.env up --build
```

## 1. Swagger UI
Visit the [Swagger UI](http://localhost:8000/docs) in your Browser. The following Swagger UI should be automatically be generated providing different basic read-only endpoints which are provided by the FastAPI.

<swagger-ui src="./quick_open_api.yaml"/>





