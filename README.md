# Google Drive to AWS S3
Create a workfow in which users will upload to Google Drive and then a script will be kicked off to upload these files to AWS S3 without user intervention. 

Run in a containerized fashion.  Always think Docker.

# Prerequisites
Use virtualenv to isolate your python environment. Virtualenv is a tool to create isolated Python environments. The basic problem it addresses is one of dependencies and versions, and indirectly permissions.

For MacOs
```bash
pip3 install virtualenv
virtualenv <your-env>
source <your-env>/bin/activate
```

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install foobar.

```bash
pip install -r requirements.txt or docker build -t sync-photos .
```

## Usage

```python
docker run sync-photos
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)
