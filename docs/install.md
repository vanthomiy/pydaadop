Installation is as simple as:

=== "pip"

    ```bash
    pip install pydaadop
    ```

=== "uv"

    ```bash
    uv add pydaadop
    ```

Pydantic has a few dependencies:

* [`pydantic-core`](https://pypi.org/project/pydantic-core/): Core validation logic for Pydantic written in Rust.
* [`typing-extensions`](https://pypi.org/project/typing-extensions/): Backport of the standard library [typing][] module.
* [`annotated-types`](https://pypi.org/project/annotated-types/): Reusable constraint types to use with [`typing.Annotated`][].

If you've got Python 3.9+ and `pip` installed, you're good to go.

## Install from repository

And if you prefer to install Pydaadop directly from the repository:


=== "pip"

    ```bash
    pip install 'git+https://github.com/vanthomiy/pydaadop@main'
    ```

=== "uv"

    ```bash
    uv add 'git+https://github.com/vanthomiy/pydaadop@main'
    ```
