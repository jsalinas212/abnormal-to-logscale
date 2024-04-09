# abnormal-to-logscale

## Description
Python script to fetch data from Abnormal Security and feed it to LogScale's ingest API.

The script currently fetches from the following endpoints:
```python
endpoints = {
    "cases",
    "vendor-cases",
    "abusecampaigns"
}
```

## Requirements

### Python Version
* Python3.10+

### Dependencies
* python-dotenv

## Usage

Install the `python-dotenv` package with pip.
```
pip install python-dotenv
```

Add a `.env` file in the same directory as the script.
```
SRCTOKEN={Abnormal Security API Token}
DSTTOKEN={LogScale Repository Ingest Token}
ORGTENANT={LogScale Org Tenant}
```

Adjust how far back you would like to fetch results by adusting the time delta function.
```python
datetime.timedelta(minutes=15)
```

You can also set the time delta to use `hours` or `days` instead of minutes.
```python
datetime.timedelta(hours=2)
```

Or...
```python
datetime.timedelta(days=5)
```

Specify the number of events you want to fetch by adjusting the `pageSize` value in the `params` list.
```python
params = {
        "filter": paramOpts + " gte " + sTime,
        "pageSize": 5
    }
```

## Author
* JA Salinas

## Known Issues
I had issues with getting the date in UTC using Python 3.10.

Issue:
```python
datetime.datetime.now(datetime.UTC)
```

Solution:
```python
datetime.datetime.utcnow()
```

The solution still works in Python version 3.13, but it complains about `utcnow()` being deprecated.

## License

[GPL-3.0 license](./LICENSE.md)