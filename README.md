# JADE_usage
[![Build Status](https://travis-ci.com/alan-turing-institute/JADE_usage.svg?branch=master)](https://travis-ci.com/alan-turing-institute/JADE_usage)
[![Build Status](https://travis-ci.com/alan-turing-institute/JADE_usage.svg?branch=dev)](https://travis-ci.com/alan-turing-institute/JADE_usage)

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
