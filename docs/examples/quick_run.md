# Quick Setup Run

!!! Info
    After the [Quick Setup](./quick_setup.md) you should be able to test and run the setup.

!!! Warning
    Make sure that you have docker installed in your environment.
    Else follow the instructions on the [Docker website](https://docs.docker.com/get-docker/).

Run the docker-compose file to create docker containers. With this command the `example.env` file is used to set the environment variables and a build is forced.

```bash
docker-compose --env-file example.env up --build
```

## Open the Swagger UI
Visit the [Swagger UI](http://localhost:8000/docs) in your Browser. The following Swagger UI should be automatically be generated providing different basic read-write endpoints for the `BaseMongoModel` which are provided by the FastAPI.

<div class="swagger-container">
  <swagger-ui src="./quick_open_api.yaml"></swagger-ui>
</div>

## Create a new document

=== "Swagger UI"
    !!! Note ""

        Click on the `POST` endpoint and then on the `Try it out` button. Fill in the `body` with the following content and click on the `Execute` button.

        ```json
        {
        "_id": "11111111-2222-3333-4444-555555555555"
        }
        ```

=== "Curl"
    !!! Note ""

        ```bash
        curl -X 'POST' \
        'http://localhost:8000/basemongomodel/' \
        -H 'accept: application/json' \
        -H 'Content-Type: application/json' \
        -d '{
        "_id": "11111111-2222-3333-4444-555555555555"
        }'
        ```

The response should be similar to the following:

```json
{
  "_id": "11111111-2222-3333-4444-555555555555"
}
```

Feel free to test and play with the other endpoints as well.
