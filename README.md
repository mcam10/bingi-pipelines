# Google Drive to AWS S3

This is in lieu of project chocolate and needing of a way to create a workfow in which users will upload to Google Drive and then a script will be kicked off to upload these files to AWS S3 without user intervention. 

This script should be ran once a week. 

This script should also try to clean the data, no duplicate image data should be allowed.

Ultimately need images with comments ( food eaten -- this will also be a feature in classification service) to AWS S3 metadata. The structure of the data in S3 will ultimately be a ranking ( project chocolate ranking system )  as directory i.e 1/ 2/ 3/${date-of-pic} -- metadata=chicken --metadata=solid

Features should be accepted. 
Date of image.
Ranking directory structure
Food eaten prior
Description of image contents

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
