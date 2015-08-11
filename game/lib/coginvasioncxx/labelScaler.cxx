// Filename: labelScaler.cxx
// Created by:  blach (09Aug15)

#include <math.h>

#include "nodePath.h"
#include "asyncTaskManager.h"
#include "genericAsyncTask.h"

#include "labelScaler.h"

LabelScaler::
LabelScaler(const float scaling_factor) :
  _task_mgr(AsyncTaskManager::get_global_ptr()),
  _scaling_factor(scaling_factor),
  _cam(NULL),
  _node(NULL),
  _max_distance(50.0),
  _min_distance(1.0)
{

}

void LabelScaler::
set_node(NodePath& node) {
  _node = node;
}

void LabelScaler::
set_camera(NodePath& camera) {
  _cam = camera;
}

AsyncTask::DoneStatus LabelScaler::
resize_task(GenericAsyncTask* task, void* data) {
  if (_node.is_empty()) {
    return AsyncTask::DS_done;
  }

  float distance = _node.get_distance(_cam);
  if (distance > _max_distance) {
    distance = _max_distance;
  }
  else if (distance < _min_distance) {
    distance = _min_distance;
  }

  float scale = sqrt(distance) * _scaling_factor;
  _node.set_scale(scale);

  return AsyncTask::DS_cont;
}

void LabelScaler::
resize() {
  PT(GenericAsyncTask) task = new GenericAsyncTask("labelScalingAsyncTask", &LabelScaler::resize_task, (void*) NULL);
  _task_mgr->add(task);
}
