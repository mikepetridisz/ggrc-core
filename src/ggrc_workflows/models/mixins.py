# Copyright (C) 2020 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Mixins for ggrc_workflow app."""

from datetime import date

from sqlalchemy.ext import declarative

from ggrc import builder
from ggrc import db
from ggrc.models import deferred
from ggrc.models import comment
from ggrc.models import mixins
from ggrc.models import reflection


class StatusValidatedMixin(mixins.Stateful):
  """Mixin setup statuses for Cycle and CycleTaskGroup."""

  ASSIGNED = u"Assigned"
  IN_PROGRESS = u"In Progress"
  FINISHED = u"Finished"
  VERIFIED = u"Verified"
  DEPRECATED = u"Deprecated"

  NO_VALIDATION_STATES = [ASSIGNED, IN_PROGRESS, FINISHED, DEPRECATED]
  VALID_STATES = NO_VALIDATION_STATES + [VERIFIED]

  _api_attrs = reflection.ApiAttributes(
      reflection.Attribute("is_verification_needed",
                           create=False,
                           update=False),
  )

  def is_verification_needed(self):
    raise NotImplementedError()

  @classmethod
  def default_status(cls):
    return cls.ASSIGNED

  def valid_statuses(self):
    """Return valid status for self instance."""
    if self.is_verification_needed:
      return self.VALID_STATES
    return self.NO_VALIDATION_STATES

  @property
  def active_states(self):
    return [i for i in self.valid_statuses() if i != self.done_status]

  @property
  def done_status(self):
    return self.VERIFIED if self.is_verification_needed else self.FINISHED

  @property
  def is_done(self):
    return self.done_status == self.status


class CycleStatusValidatedMixin(StatusValidatedMixin):
  """Mixin setup is_verification needed field for Cycle."""

  _aliases = {
      "status": {
          "display_name": "State",
          "mandatory": False,
          "description": "Options are: \n{} ".format(
              '\n'.join(StatusValidatedMixin.VALID_STATES)
          ),
      },
  }

  @declarative.declared_attr
  def is_verification_needed(cls):  # pylint: disable=no-self-argument
    return deferred.deferred(
        db.Column(db.Boolean, default=True, nullable=False),
        cls.__name__,
    )


class CycleTaskGroupRelatedStatusValidatedMixin(StatusValidatedMixin):
  """Mixin setup is_verification needed property."""

  @builder.simple_property
  def is_verification_needed(self):
    return self.cycle is None or self.cycle.is_verification_needed


class CycleTaskStatusValidatedMixin(CycleTaskGroupRelatedStatusValidatedMixin):
  """Mixin setup state for CycleTaskGroupObjectTask."""

  DECLINED = u"Declined"

  VALID_STATES = CycleTaskGroupRelatedStatusValidatedMixin.VALID_STATES + [
      DECLINED,
  ]

  @property
  def is_overdue(self):
    """Return True if task is overdue."""
    today = date.today()
    task_end_date = self.end_date or today
    return not self.is_done and task_end_date < today

  _aliases = {
      "status": {
          "display_name": "State",
          "mandatory": False,
          "description": (
              u"Options are: \n"
              u"{states} \n".format(states='\n'.join(VALID_STATES))
          ),
      },
  }


class WorkflowCommentable(comment.Commentable):
  """Mixin for commentable workflow objects."""
  VALID_RECIPIENTS = frozenset([
      "Task Assignees",
      "Task Secondary Assignees"
  ])
  recipients = db.Column(
      db.String,
      nullable=True,
      default=u"Task Assignees,Task Secondary Assignees")


class WFCustomRestrictions(object):
  """
    Mixin for custom restriction on objects
    Depends on method of request, and fields to updates
  """
  _method_fields_restrictions = {}

  @property
  def method_fields_restrictions(self):
    return self._method_fields_restrictions

  @method_fields_restrictions.setter
  def method_fields_restrictions(self, obj):
    self._method_fields_restrictions = obj

  def is_method_fields_restricted(self, method, obj, upd_obj):
    """Check the input object with actual object for restricted fields
      If the returned list of fields for restriction is empty, then whole
      method is restricted
    """
    method_fields_restriction = self._method_fields_restrictions.get(method)
    if method_fields_restriction is not None:
      if not method_fields_restriction:
        return True
      for field in method_fields_restriction:
        upd_field = upd_obj.get(field)
        if upd_field is not None and upd_field != obj.get(field):
          return True
    return False
