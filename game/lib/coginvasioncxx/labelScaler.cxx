// Filename: labelScaler.cxx
// Created by:  blach (09Aug15)

#include "labelScaler.h"
#include "nodePath.h"
#include "asyncTaskManager.h"

taskMgr = AsyncTaskManager::get_global_ptr();

LabelScaler::
LabelScaler(const float scaling_factor = 0.06) {
  task_mgr = AsyncTaskManager::get_global_ptr();
  m_scaling_factor = scaling_factor;
}

LabelScaler
