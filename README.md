[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Maintainability](https://api.codeclimate.com/v1/badges/97d45867d9f5fb10b538/maintainability)](https://codeclimate.com/github/deadpyxel/digital-image-processing/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/97d45867d9f5fb10b538/test_coverage)](https://codeclimate.com/github/deadpyxel/digital-image-processing/test_coverage)
[![Documentation Status](https://readthedocs.org/projects/simple-imaging/badge/?version=latest)](https://simple-imaging.readthedocs.io/en/latest/?badge=latest)
# simple-imaging

**simple-imaging** is a Python library for simple imaging processing tasks, made as part of the assignment for the Digital Imaging Processing class taken in 2020.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install simple-imaging.

```bash
pip install simple-imaging
```

## Usage

A simple example of the usage can be found below.
```python
from simple_imaging import image

img = image.read_file('sample.ppm')
img.negative()
```

### Developer reference
>WIP

### Running tests
This project has unit tests, and PRs have to pass in all tests to be merged.

>WIP

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
