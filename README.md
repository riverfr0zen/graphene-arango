This package is in very early development. For now, please see the [tests](graphene_arango/tests) for usage clues.

# Running tests & example app

* Copy/modify `graphene_arango/tests/settings_example.py` to `graphene_arango/tests/settings.py`. You will also have to create a database per the settings.

* Make sure you've installed all dependencies (including dev dependencies) using your python package manager. You can find the dependencies in `pyproject.toml`

To run tests:
```
pytest 
```

To run the example app (from base folder):
```
sh run_example_app.sh
```


# License
Standard MIT License. See LICENSE file
