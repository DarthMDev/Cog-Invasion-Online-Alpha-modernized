// Filename: labelScaler.cxx
// Created by:  blach (09Aug15)

#include "labelScaler.h"

LabelScaler::
LabelScaler(NodePath node, NodePath& camera, const float scaling_factor) :
_scaling_factor(scaling_factor), _node(node), _cam(camera), _task_mgr(AsyncTaskManager::get_global_ptr()) {

}

LabelScaler::
~LabelScaler(){

}

AsyncTask::DoneStatus LabelScaler::
do_resize_task() {

	if (_node == NULL) {
		std::cout << "It's NULL?!!?!?" << std::endl;
	}

	if (_cam == NULL) {
		std::cout << "CAM IS NULL?!?!?" << std::endl;
	}

	if (_node.is_empty()) {
		return AsyncTask::DS_done;
	}

	const float max_distance = 50.0;
	const float min_distance = 1.0;

	double distance = _node.get_pos(_cam).length();
	if (distance > max_distance) {
		distance = max_distance;
	}
	else if (distance < min_distance) {
		distance = min_distance;
	}

	_node.set_scale(sqrt(distance) * _scaling_factor);

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
