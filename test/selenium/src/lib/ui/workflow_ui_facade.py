# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Workflow UI facade."""
from lib import url
from lib.entities import ui_dict_convert
from lib.page import dashboard
from lib.page.widget import workflow_tabs, task_group_info_panel
from lib.ui import internal_ui_operations
from lib.utils import selenium_utils


def create_workflow(workflow):
  """Creates a workflow `workflow`."""
  selenium_utils.open_url(url.dashboard())
  dashboard.Dashboard().start_workflow()
  internal_ui_operations.submit_obj(workflow)


def open_create_task_group_task_popup(task_group):
  """Opens task group task popup."""
  # pylint: disable=invalid-name
  setup_tab = workflow_tabs.SetupTab()
  setup_tab.open_via_url(task_group.workflow)
  setup_tab.open_create_task_group_task_modal(task_group)


def create_task_group_task(task_group_task):
  """Creates a task group task."""
  setup_tab = workflow_tabs.SetupTab()
  setup_tab.open_via_url(task_group_task.task_group.workflow)
  setup_tab.create_task_group_task(task_group_task)


def task_group_objs(workflow):
  """Returns task group titles of `workflow`."""
  setup_tab = workflow_tabs.SetupTab()
  setup_tab.open_via_url(workflow)
  return [ui_dict_convert.task_group_ui_to_app(task_group_row.obj_dict())
          for task_group_row in setup_tab.task_group_rows()]


def get_task_group_tasks_objs():
  """Returns task group tasks."""
  return [ui_dict_convert.task_group_task_ui_to_app(task_row.obj_dict())
          for task_row
          in task_group_info_panel.TaskGroupInfoPanel().task_rows()]
