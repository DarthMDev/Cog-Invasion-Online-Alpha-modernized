// Filename: labelScaler.h
// Created by:  blach (09Aug15)

#ifndef LABELSCALER_H
#define LABELSCALER_H

#include "pandabase.h"
#include "nodePath.h"
#include "asyncTaskManager.h"
#include "genericAsyncTask.h"

class LabelScaler : public TypedObject {
private:
	NodePath& _node;
	const NodePath& _cam;
	const float _scaling_factor;
	PT(AsyncTaskManager) _task_mgr;

PUBLISHED:
	LabelScaler(NodePath& node, const NodePath& camera, const float scaling_factor = 0.06);
	~LabelScaler();
	void resize();
	
	AsyncTask::DoneStatus do_resize_task();
	static AsyncTask::DoneStatus resize_task(GenericAsyncTask* task, void* data);

public:
	static TypeHandle get_class_type() {
		return _type_handle;
	}

	static void init_type() {
		TypedObject::init_type();
		register_type(_type_handle, "LabelScaler", TypedObject::get_class_type());
	}

	virtual TypeHandle get_type() const {
		return get_class_type();
	}

	virtual TypeHandle force_init_type() {
		init_type();
		return get_class_type();
	}

private:
	static TypeHandle _type_handle;

};

#endif