# Quick Setup

You can either choose the ready-to-go project or setup the project manually to get to know the basics components of a `pydaadop` project.
    
=== "Read-to-go Setup"
    !!! Note ""
        We are using a pre-defined release which is ready to go.

        ### 1. Download

        [![Branch](https://img.shields.io/badge/Visit-Branch-blue)](https://github.com/vanthomiy/pydaadop/tree/quick-setup)
        [![Direct Download](https://img.shields.io/badge/Download-Branch-green)](https://github.com/vanthomiy/pydaadop/archive/refs/heads/quick-setup.zip)

        To get all files either visit and clone the [Branch](https://github.com/vanthomiy/pydaadop/tree/quick-setup) or just download the [Archive](https://github.com/vanthomiy/pydaadop/archive/refs/heads/quick-setup.zip).
        Extract the files to your desired location.

        ### 2. Open
        Open the extracted folder in your favorite IDE like [VS Code](https://code.visualstudio.com/) or [PyCharm](https://www.jetbrains.com/pycharm/). You can also just use the terminal in the root of the project.

=== "Manual Setup"
    !!! Note ""

        We are setting up all files which are needed for a minimalistic pydaadop project.

        ### 1. Install
        Follow the [installation instructions](../../install.md) to install Pydaadop in your environment.
        Make sure that you have docker installed in your environment.

        ### 2. Setup

        Create a new project in your favorite IDE like [VS Code](https://code.visualstudio.com/) or [PyCharm](https://www.jetbrains.com/pycharm/).

        #### 2.1 Environment Variables

        !!! Warning
            Naming the file `.env` is a common practice and it's not recommended to change it and even worse to commit it to the repository.
            We use the `example.env` file to be able to commit it to the repository using no actual sensitive data.

        Create a `example.env` file in the root of your project and add the following environment variables.
        Feel free to adjust the actual values to your needs.

        ```env  title=".env" linenums="1"
        --8<-- "examples/setups/quick/example.env"
        ```

        #### 2.2 Requirements

        Create a `requirements.txt` file in the root of your project and add `pydaadop`.

        ```env  title="requirements.txt" linenums="1"
        --8<-- "examples/requirements.txt"
        ```

        ####  2.3 API
        Add a new file `api.py` and define the `Fast API` using the [`BaseReadRouter`]() class.

        ```python title="api.py"
        --8<-- "examples/setups/quick/api.py"
        ```

        ####  2.4 Docker
        We need to add a `Dockerfile` and a `docker-compose.yml` file to the root of the project.
        These will dockerize the FastAPI and MongoDB for easy setup.

        ```python title="api.Dockerfile" linenums="1"
        --8<-- "examples/setups/quick/api.Dockerfile"
        ```

        ```python title="docker-compose.yml" linenums="1"
        --8<-- "examples/setups/quick/docker-compose.yml"
        ```

        ### 3. Final Project

        Our final project should look like this:

        ```bash
        .
        ├── api.py
        ├── api.Dockerfile
        ├── docker-compose.yml
        ├── example.env
        └── requirements.txt
        ```

## Next test and run your setup

Now you should have a working setup! 🚀

!!! Tip
    On the [Quick Setup Run](./quick_run.md) page you get some tips how to test if everything worked as expected.
