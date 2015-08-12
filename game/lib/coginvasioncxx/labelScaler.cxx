// Filename: labelScaler.cxx
// Created by:  blach (09Aug15)

#include <iostream>
#include <cmath>

#include "asyncTaskManager.h"
#include "genericAsyncTask.h"

#include "labelScaler.h"

TypeHandle LabelScaler::_type_handle;

LabelScaler::
LabelScaler(NodePath& node, const NodePath& camera, const float scaling_factor) :
_scaling_factor(scaling_factor), _node(node), _cam(camera), _task_mgr(AsyncTaskManager::get_global_ptr()) {

}

LabelScaler::
~LabelScaler(){

}

AsyncTask::DoneStatus LabelScaler::
do_resize_task() {
	if (_node.is_empty()) {
		return AsyncTask::DS_done;
	}

	float max_distance = 50.0;
	float min_distance = 1.0;

	float distance = _node.get_distance(_cam);
	if (distance > max_distance) {
		distance = max_distance;
	}
	else if (distance < min_distance) {
		distance = min_distance;
	}

	float scale = sqrt(distance) * _scaling_factor;
	_node.set_scale(scale, scale, scale);

	return AsyncTask::DS_cont;
}

AsyncTask::DoneStatus LabelScaler::
resize_task(GenericAsyncTask* task, void* data) {
	return ((LabelScaler*)data)->do_resize_task();
}

void LabelScaler::
resize() {
	PT(GenericAsyncTask) task = new GenericAsyncTask("LabelScaler_resize_task", &LabelScaler::resize_task, (void*) this);
	_task_mgr->add(task);
}