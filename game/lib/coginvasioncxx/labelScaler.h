// Filename: labelScaler.h
// Created by:  blach (09Aug15)

#ifndef LABELSCALER_H
#define LABELSCALER_H

#include "nodePath.h"
#include "pandabase.h"

class LabelScaler : public TypedObject {
PUBLISHED:
  LabelScaler(const float scaling_factor = 0.06);
  ~LabelScaler();

  void resize();

private:
  NodePath& m_node;
  const float m_scaling_factor;
  PT(AsyncTaskManager) task_mgr;

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

#include "labelScaler.I"

#endif
