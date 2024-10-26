# Development

## Linting

Linting is the process of running a program that will analyze your code for potential errors, stylistic inconsistencies, and coding standard violations.

We use [pylint](https://pylint.readthedocs.io/en/stable/) and our linting configuration is stored in the `.pylintrc` file in the root directory of this project.

Pylint is run:
- during development with `pylint .` (by the developer)
- when pushing or creating a pull request (automatically by GitHub actions)

Currently our configuration requires for the score to be at least 9.5/10.0 to pass the test.
It is not recommened to edit the pylint config or change the fail treshold unless absolutely necessary.
