# JADE_usage
[![CI](https://github.com/alan-turing-institute/JADE_usage/actions/workflows/ci.yaml/badge.svg)](https://github.com/alan-turing-institute/JADE_usage/actions/workflows/ci.yaml)

A command line utility for exporting and analysing usage on [JADE](jade.ac.uk).

## Installation

To install clone this repository then install using pip. For example

```
$ git clone https://github.com/alan-turing-institute/JADE_usage.git
$ cd JADE_usage
$ pip install .
```

A summary of commands can then be seen by executing

```
$ jade-usage -h
```

## Note

You will need valid login credentials for JADE to use this program. Job data is
collected using SSH.
