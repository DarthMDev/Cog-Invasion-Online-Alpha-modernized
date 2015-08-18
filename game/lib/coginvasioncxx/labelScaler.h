// Filename: labelScaler.h
// Created by:  blach (09Aug15)

#ifndef LABELSCALER_H
#define LABELSCALER_H

#include <iostream>
#include <string>
#include <cmath>

#include "pandabase.h"
#include "nodePath.h"
#include "asyncTaskManager.h"
#include "genericAsyncTask.h"

class EXPCL_PANDASKEL LabelScaler {
private:
	NodePath _node;
	NodePath& _cam;
	const float _scaling_factor;
	PT(AsyncTaskManager) _task_mgr;

	AsyncTask::DoneStatus do_resize_task();
	static AsyncTask::DoneStatus resize_task(GenericAsyncTask* task, void* data);

PUBLISHED:
	LabelScaler(NodePath node, NodePath& camera, const float scaling_factor = 0.06);
	~LabelScaler();
	void resize();

};

#endif
