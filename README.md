# lib-python-astr

[![PyPI version](https://badge.fury.io/py/libastr.svg)](https://badge.fury.io/py/libastr)
[![License: MPL 2.0](https://img.shields.io/badge/License-MPL%202.0-brightgreen.svg)](https://opensource.org/licenses/MPL-2.0)

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.

### Purpose

Libastr is a **Python3** library designed to ease python scripting with 
the API of A.S.T.R. (Archiving System Truly RESTful). 
It includes multiple features like browsing, downloading and uploading archives.

### Installation

1. Git clone the repository.

2. Install the library with pip. It is advised to use 
  [virtualenv](http://virtualenvwrapper.readthedocs.io/en/latest/):
      ```
      pip install lib-python-astr
      ```

### Configuration

To communicate with the ASTR server, three parameters must be given to the
an instance of the class `AstrClient`:
  * base_url: ASTR instance base url (e.g. http://my-astr-server:8000)
  * email: a user email
  * token: a token of this user (to be generated on the website)

```python
from libastr import AstrClient
client = AstrClient(base_url, email, token)
```

Or, to avoid giving all these parameters manually, they can be stored in
environment variables:

```
export LIBASTR_URL='http://my-astr-server:8000'
export LIBASTR_EMAIL='john.doe@my-email.com'
export LIBASTR_TOKEN='b4b71bf6-a3dd-4975-85b8-03de05096fc0'
```

Then, if you make an instance of `AstrClient` without giving arguments, it
will fetch these environment variables by default.

### Basic usage

```python
from libastr import Browser

# If you use environment variables to connect to the server...
browser = Browser()
# Or if yo use custom variables...
from libastr import AstrClient
client = AstrClient(base_url, email, token)
browser = Browser(client)

# Retrieve some archives
my_archives = browser.get_archives_by_args(
                               author="John DOE",
                               category="MY CATEGORY",
                               descriptors={"my_desc": "MY VALUE"})

# download an archive
my_archives[0].download(local_path="/home/john.doe/Documents/")

# Retrieve all categories
cat = browser.get_all_archive_categories()

# Get descriptors of one category
cat[0].get_descriptors()
```
