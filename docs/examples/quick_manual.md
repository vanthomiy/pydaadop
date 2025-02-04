# Quick Manual Setup

This is the easiest way to get started with `pydaadop`.
We are setting up all files which are needed for a minimalistic pydaadop project.

!!! Info
    If you want to use a ready-to-go project follow the instructions on the [Quick Auto Setup](./quick_auto.md).

## 1. Install
Follow the [installation instructions](../install.md) to install Pydaadop in your environment.
Make sure that you have docker installed in your environment.

## 2. Setup

We need to setup a few things here.

### 2.1 Environment Variables

Create a `.env` file in the root of your project and add the following environment variables.
Feel free to adjust the actual values to your needs.

```env  title=".env" linenums="1"
--8<-- "examples/example.env"
```

###  2.2 API
Create a Fast API and define a read-only route using the [`BaseReadRouter`](../install.md) class.

```python title="api.py" linenums="1"
--8<-- "examples/setups/quick/api.py"
```





