# Quick Setup

This is the easiest way to get started with `pydaadop`.

## 1. Install
Follow the [installation instructions](../install.md) to install Pydaadop in your environment.
Make sure that you have docker installed in your environment.

## 2. Setup

We need to setup a few things here.

###  2.1 API
Create a Fast API and define a read-only route using the [`BaseReadRouter`](../install.md) class.

```python title="api.py" linenums="1"
--8<-- "examples/setups/quick/api.py"
```

## 3. Run
Run the Fast API server and visit the [Swagger UI](http://localhost:8000/docs) if not specified. The following Swagger UI should be automatically be generated providing different basic read-only endpoints.

<swagger-ui src="./quick_open_api.yaml"/>





