// Filename: config_ccoginvasion.cxx
// Created by:  blach (11Aug15)

#include "labelScaler.h"

#include "pandabase.h"
#include "dconfig.h"

void init_libccoginvasion();

Configure(config_ccoginvasion);

ConfigureFn(config_ccoginvasion) {
	init_libccoginvasion();
}

void init_libccoginvasion() {
	static bool initialized = false;
	if (initialized) {
		return;
	}

	initialized = true;

	LabelScaler::init_type();
}