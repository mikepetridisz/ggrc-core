# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Module with common helper functions."""

from contextlib import contextmanager

import ddt

import flask


def tuplify(data):
  """Convert dictionary to a list of tuples."""
  for key, value in data.items():
    if isinstance(value, dict):
      for keykey in tuplify(value):
        yield (key,) + keykey
    else:
      yield (key, value)


def unwrap(data):
  """Decorator that unwrap data dictionary into list of tuples.

  Structure like {"A": {"B": "C", "D": "E"} will be changed to
  [("A", "B", "C"), ("A", "D", "E")]. It will be fed to wrapped function
  through the ddt.unpack.

  Args:
      data: Dictionary with test parameters.

  Returns:
      A batch of test functions.
  """
  def wrapper(func):
    return ddt.data(*tuplify(data))(ddt.unpack(func))
  return wrapper


@contextmanager
def logged_user(user):
  """Context manager to log in provided user."""
  global_user = getattr(flask.g, "_current_user", None)
  setattr(flask.g, "_current_user", user)
  yield
  setattr(flask.g, "_current_user", global_user)
