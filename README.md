# Overview

Some simple scripts I wrote while testing out the AWS ES service. There are two scripts:

* `create_roles.py` - Creates an individual user, role, and role mapping based on the users configured in `users.yaml`. User passwords are written out to `created_users.yaml`. Users are allowed to write to indices in the pattern `$username-*`.
* `populate_indices.py` - Logs in with the users from `created_users.yaml` and populates indicies in the format `$username-$date` with some random sample data.

# Usage

Install requirements:

```
pip install -r requirements.txt
```

Edit `config_example.yaml` and rename to `config.yaml`

Fill out the users you want in `users.yaml`

Run `create_roles.py` and then `populate_indices.py`
