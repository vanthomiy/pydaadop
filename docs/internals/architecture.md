!!! note
    This section is part of the *internals* documentation, and is partly targeted to contributors.

Starting with Pydantic V2, part of the codebase is written in Rust in a separate package called `pydantic-core`.
This was done partly in order to improve validation and serialization performance (with the cost of limited
customization and extendibility of the internal logic).

This architecture documentation will first cover how the two `pydantic` and `pydantic-core` packages interact
together, then will go through the architecture specifics for various patterns (model definition, validation,
serialization, JSON Schema).

Usage of the Pydantic library can be divided into two parts:

- Model definition, done in the `pydantic` package.
- Model validation and serialization, done in the `pydantic-core` package.
