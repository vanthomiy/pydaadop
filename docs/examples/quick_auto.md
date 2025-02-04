# Quick Auto Setup

This is the easiest way to get started with `pydaadop`.
We are using a pre-defined release which is ready to go.

!!! Info
    If you want to implement the setup yourself follow the instructions on the [Quick Manual Setup](./quick_manual.md).

## 1. Download
To get all files either clone the repository or preferably download the [Quick Auto Setup]() release.
Extract the files to your desired location.

## 2. Open
Open the extracted folder in your favorite IDE like [VS Code](https://code.visualstudio.com/) or [PyCharm](https://www.jetbrains.com/pycharm/).

## 3. Requirements

1. Run the following command to install the required packages.
```bash
pip install -r requirements.txt
```

This will install the required packages for the project like `fastapi`, `uvicorn`, `pydaadop`.

2. Make sure that you have docker installed in your environment.
Else follow the instructions on the [Docker website](https://docs.docker.com/get-docker/).

Now you should be ready to go! 🚀

## 4. Run
Run the docker-compose file to create docker containers for:

- FastAPI
- MongoDB
- Init (which initializes the database)

```bash
docker-compose up --build
```

!!! Tip
    On the [Quick Setup Results](./quick_results.md) page you get some tips how to test if everything worked as expected.





