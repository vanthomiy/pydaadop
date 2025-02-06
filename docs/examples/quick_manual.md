# Quick Manual Setup

This is the easiest way to get started with `pydaadop`.
We are setting up all files which are needed for a minimalistic pydaadop project.

!!! Info
    If you want to use a ready-to-go project follow the instructions on the [Quick Auto Setup](./quick_auto.md).

## 1. Install
Follow the [installation instructions](../install.md) to install Pydaadop in your environment.
Make sure that you have docker installed in your environment.

## 2. Setup

Create a new project in your favorite IDE like [VS Code](https://code.visualstudio.com/) or [PyCharm](https://www.jetbrains.com/pycharm/).

### 2.1 Environment Variables

Create a `example.env` file in the root of your project and add the following environment variables.
Feel free to adjust the actual values to your needs.

```env  title=".env" linenums="1"
--8<-- "examples/example.env"
```

### 2.2 Requirements

Create a `requirements.txt` file in the root of your project and add `pydaadop`.

```env  title=".env" linenums="1"
--8<-- "examples/requirements.txt"
```

###  2.3 API
Add a new file `api.py` and define the `Fast API` using the [`BaseReadRouter`](../install.md) class.

```python title="api.py" linenums="1"
--8<-- "examples/setups/quick/api.py"
```

###  2.4 Docker
We need to add a `Dockerfile` and a `docker-compose.yml` file to the root of the project.
Does will dockerize the FastAPI and MongoDB for easy setup.

```python title="api.Dockerfile" linenums="1"
--8<-- "examples/api.Dockerfile"
```

```python title="docker-compose.yml" linenums="1"
--8<-- "examples/docker-compose.yml"
```

## 3. Final Project

Our final project should look like this:

```bash
.
├── api.py
├── api.Dockerfile
├── docker-compose.yml
├── example.env
└── requirements.txt
```


### 4. Next

Now you should have a working setup! 🚀

!!! Tip
    On the [Quick Setup Run](./quick_run.md) page you get some tips how to test if everything worked as expected.
