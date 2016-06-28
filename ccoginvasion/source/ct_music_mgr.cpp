#include "ct_music_mgr.h"

#include <stdlib.h>
#include <time.h>

#include "eventHandler.h"
#include "tools.cpp"

bool CTMusicManager::loaded = false;
CTMusicManager::MusicChunkMap CTMusicManager::tournament_music_chunks;
CTMusicManager::MusicClipMap CTMusicManager::tournament_music_clips;
PT(AudioManager) CTMusicManager::audio_mgr;

CTMusicManager::~CTMusicManager()
{
}

bool CTMusicManager::is_loaded()
{
	return loaded;
}

void CTMusicManager::spawn_load_tournament_music_task(PT(AudioManager) am)
{
	audio_mgr = am;
	PT(GenericAsyncTask) task = new GenericAsyncTask("LTM", &CTMusicManager::load_tournament_music, (void*)NULL);
	task->set_task_chain("TournamentMusicThread");
	AsyncTaskManager::get_global_ptr()->add(task);
}

AsyncTask::DoneStatus CTMusicManager::load_tournament_music(GenericAsyncTask* task, void* data)
{
	if (loaded) {
		cout << "Redundant call to CTMusicManager::load_tournament_music()" << endl;
		return AsyncTask::DS_done;
	}

	cout << "Loading tournament music" << endl;

	srand(time(NULL));

	if (!CTMusicData::initialized) {
		cout << "Chunk data not yet initialized, initializing..." << endl;
		CTMusicData::initialize_chunk_data();
	}

	for (CTMusicData::MusicDataMap::iterator rootMapItr = CTMusicData::data.begin(); rootMapItr != CTMusicData::data.end(); ++rootMapItr)
	{

		string song_name = rootMapItr->first;
		CTMusicData::ChunkDataMap chunkdata = rootMapItr->second;

		cout << song_name << endl;

		for (CTMusicData::ChunkDataMap::iterator chunkMapItr = chunkdata.begin(); chunkMapItr != chunkdata.end(); ++chunkMapItr)
		{

			string chunk_name = chunkMapItr->first;
			vector<int> file_range = chunkMapItr->second;

			for (int indexi = 0; indexi < file_range.size(); indexi++) {

				int clip_index = file_range[indexi];

				string folder = "tournament_music/" + song_name + "/";
				string filename = "MW_Music";
				string extension = ".ogg";

				if (clip_index > 0) {
					filename = filename + "_" + to_string((longlong)clip_index);
				}

				string fullfile = folder + filename + extension;
				PT(AudioSound) song = audio_mgr->get_sound(fullfile);
				song->set_volume(0.5f);
				song->set_loop(false);
				tournament_music_chunks[song_name][chunk_name].push_back(song);
				
			}

		    tournament_music_clips[song_name][chunk_name] = AudioClip(tournament_music_chunks[song_name][chunk_name], chunk_name);
		}
	}

	loaded = true;
	cout << "Finished loading tournament music" << endl;
	return AsyncTask::DS_done;
}

CTMusicManager::CTMusicManager() : _curr_clip(NULL)
{
	_next_clip_request = "NONE";
	_curr_clip_name = "NONE";

	string base_song = "encntr_nfsmw_bg_";
	int index = rand() % 4;
	_song_name = base_song + to_string((longlong)index + 1);
}

void CTMusicManager::set_clip_request(const string& clip)
{
	_next_clip_request = clip;
}

string CTMusicManager::get_clip_request() const
{
	return _next_clip_request;
}

void CTMusicManager::start_music()
{
	if (!loaded) {
		cout << "CTMusicManager: Cannot start the music before loading!" << endl;
		return;
	}

	cout << "Starting music" << endl;

	int index = rand() % 2;
	string base_or_orc;
	if (index == 0)
		base_or_orc = "base";
	else
		base_or_orc = "orchestra";
	play_clip("intro_" + base_or_orc);

	EventHandler* evhandl = EventHandler::get_global_event_handler();
	evhandl->add_hook(AudioClip::get_part_done_event(), &handle_part_done_event, this);
	evhandl->add_hook(AudioClip::get_clip_done_event(), &handle_clip_done, this);
}

void CTMusicManager::play_clip(string& clip_name)
{
	stop_clip();

	_curr_clip_name = clip_name;

	AudioClip* ac = &tournament_music_clips[_song_name][clip_name];
	ac->active = true;
	ac->play_all_parts();
	_curr_clip = ac;
}

void CTMusicManager::stop_clip()
{
	if (_curr_clip != NULL) {
		_curr_clip->active = false;
		_curr_clip->stop();
		_curr_clip = NULL;
	}
	_curr_clip_name = "NONE";
}

void CTMusicManager::handle_clip_done(const Event* e, void* data)
{
	((CTMusicManager*)data)->play_new_clip();
}

void CTMusicManager::play_new_clip()
{
	string new_clip;
	if (_next_clip_request == "NONE") {
		new_clip = _curr_clip_name;
	}
	else {
		new_clip = _next_clip_request;
		_next_clip_request = "NONE";
	}

	play_clip(new_clip);
}

void CTMusicManager::handle_part_done_event(const Event* e, void* data)
{
	((CTMusicManager*)data)->handle_part_done(e->get_parameter(0).get_int_value());
}

void CTMusicManager::handle_part_done(int part_index)
{
	if (_next_clip_request != "NONE" && _curr_clip_name.find(explode("_", _next_clip_request)[0]) == string::npos) {
		play_new_clip();
	}
	else if (_next_clip_request != "NONE" && _curr_clip_name.find(explode("_", _next_clip_request)[0]) != string::npos) {
		// We requested the same clip (but maybe in a different style?). Play from the same index but in the different style.
		stop_clip();
		AudioClip* ac = &tournament_music_clips[_song_name][_next_clip_request];
		ac->active = true;
		ac->play_from_index(part_index + 1);
		_curr_clip_name = _next_clip_request;
		_next_clip_request = "NONE";
		_curr_clip = ac;
	}
}