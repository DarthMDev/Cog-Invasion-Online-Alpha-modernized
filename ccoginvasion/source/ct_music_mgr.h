#ifndef CTMUSICMGR_H
#define CTMUSICMGR_H

#include "stdafx.h"
#include <map>

#include "audioclip.h"
#include "ct_music_data.h"

#include "audioManager.h"

class CTMusicManager {
PUBLISHED:

	CTMusicManager();
	~CTMusicManager();

	static void spawn_load_tournament_music_task(PT(AudioManager) am);
	void set_clip_request(const string& clip);
	string get_clip_request() const;
	void start_music();
	void stop_clip();
	static bool is_loaded();

public:

	typedef map<string, map<string, vector<PT(AudioSound)>>> MusicChunkMap;
	typedef map<string, map<string, AudioClip>> MusicClipMap;

	static MusicChunkMap tournament_music_chunks;
	static MusicClipMap tournament_music_clips;

	static bool loaded;

	static PT(AudioManager) audio_mgr;

private:
	string _next_clip_request;
	string _song_name;
	AudioClip* _curr_clip;
	string _curr_clip_name;

	static AsyncTask::DoneStatus load_tournament_music(GenericAsyncTask* task, void* data);

	static void handle_clip_done(const Event* e, void* data);
	static void handle_part_done_event(const Event* e, void* data);
	void handle_part_done(int part_index);
	void play_new_clip();
	void play_clip(string& clip_name);
};

#endif //CTMUSICMGR_H
