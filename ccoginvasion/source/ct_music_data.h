#ifndef CTMUSICDATA_H
#define CTMUSICDATA_H

#include <iostream>
#include <vector>
#include <cmath>
#include <string>
#include <map>
#include <fstream>

#include "stdafx.h"

#include "asyncTaskManager.h"
#include "threadPriority.h"

using namespace std;

class CTMusicData {
public:

	// song name -> chunk name -> file range (list of numbers)
	typedef map<string, vector<int>> ChunkDataMap;
	typedef map<string, ChunkDataMap> MusicDataMap;
	
	static MusicDataMap data;

PUBLISHED:

	CTMusicData();
	~CTMusicData();

	static bool initialized;
	static void initialize_chunk_data();
};

#endif //CTMUSICDATA_H
