// g++ -o oslide oslide.cpp -L/usr/local/lib -lopenslide -I/usr/local/include/openslide
// g++ -o oslide oslide.cpp -L/usr/local/lib -lopenslide -I/usr/local/include/openslide  `pkg-config --cflags --libs glib-2.0`
// g++ -o oslide oslide.cpp -L/usr/local/lib -lopenslide -I/usr/local/include/openslide  `pkg-config --cflags --libs glib-2.0` -I/usr/local/include -I/usr/local/include/opencv -L/usr/local/lib/ -lopencv_core -lopencv_highgui -lopencv_imgproc -lopencv_imgcodecs -lpthread -std=c++11
// g++ -o oslide oslide.cpp -L/usr/local/lib -lopenslide -I/usr/local/include/openslide  `pkg-config --cflags --libs glib-2.0` -I/usr/local/include -I/usr/local/include/opencv -L/usr/local/lib/ -lopencv_core -lopencv_highgui -lopencv_imgproc -lopencv_imgcodecs -lpthread -std=c++11 -lboost_filesystem -lboost_system


#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <vector>
#include <iostream>
#include <math.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <inttypes.h>
#include <assert.h>
#include <glib.h>
#include <sys/time.h>
#include <mutex>
#include <queue>
#include <thread>
#include <condition_variable>

#include <opencv2/opencv.hpp>
#include "openslide.h"
// #include "openslide-common.h"


using namespace cv;
using namespace std;



enum PopResult{ POP_OK, POP_STOP, POP_UNEXPECTED };

template<class T>
class BlockingQueue : public std::queue<T>
{
public:
    std::mutex m_lock;
    std::condition_variable m_cond;
    bool m_stopFlag = false;


    virtual ~BlockingQueue() = default;

    void push(const T& value)
    {
        std::lock_guard<decltype(m_lock)> lock(m_lock);
        std::queue<T>::push(value);
        m_cond.notify_one();
    }

    void push(T&& value)
    {
        std::lock_guard<decltype(m_lock)> lock(m_lock);
        std::queue<T>::push(std::move(value));
        m_cond.notify_one();
    }

    PopResult pop(T& out)
    {
        std::unique_lock<decltype(m_lock)> lock(m_lock);
        if (m_stopFlag) // åœæ­¢
        {
            return POP_STOP;
        }        
        if (queue<T>::empty())
        {
            m_cond.wait(lock);
        }
        if (m_stopFlag) // åœæ­¢
        {    
            return POP_STOP;
        }
        if (queue<T>::empty())
        {
            return POP_UNEXPECTED;
        }

        out = std::move(queue<T>::front());
        std::queue<T>::pop();
        return POP_OK;
    }

    void Stop()
    {
        std::lock_guard<decltype(m_lock)> lock(m_lock);
        m_stopFlag = true;
        m_cond.notify_all();
    }
};


BlockingQueue<map<const char*, vector<int64_t>>> cut_queue;
BlockingQueue<map<const char*, int64_t>> result_queue;
int64_t UNIT_SIZE = 4;


static void read_region_and_half_size(openslide_t* osr, int64_t x, int64_t y, int64_t w, int64_t h, string save_path) {
	// openslide_t* osr = openslide_open(slide_name);

	uint32_t *buf = (uint32_t *) g_slice_alloc(w * h * 4);
	openslide_read_region(osr, buf, x, y, 0, w, h);

	Mat img(h, w, CV_8UC4, buf);
	cvtColor(img, img, CV_RGBA2RGB);
	pyrDown(img, img);
	imwrite(save_path + "/" + to_string(x) + "_" + to_string(y) + ".bmp", img);

	g_slice_free1(w * h * 4, buf);

	// openslide_close(osr);
}


void cut_producer(vector<const char*> slide_names) {
	for (const char* slide_name : slide_names) {
		openslide_t* osr = openslide_open(slide_name);
		int64_t w, h;
		openslide_get_level0_dimensions(osr, &w, &h);
		openslide_close(osr);
		cout << slide_name << " " << w << " / " << h << endl;

		int64_t patch_size = 1216, step_size = 1216;
		// int64_t total = ((int64_t) (ceil(w*0.8/step_size) * ceil(h*0.8/step_size) / 4)) * 4;
		vector<int64_t> coords_all;
		for (int64_t x = (int64_t) w*0.1; x < (int64_t) w*0.9; x += step_size) {
			for (int64_t y = (int64_t) h*0.1; y < (int64_t) h*0.9; y += step_size) {
				coords_all.push_back(x);
				coords_all.push_back(y);
			}
		}

		int64_t count = (int64_t) coords_all.size();
		int64_t total = (int64_t) (floor(count / 2 / UNIT_SIZE) * UNIT_SIZE);
		for (int64_t i = 0; i < count; i += UNIT_SIZE*2) {
			if (count - i < UNIT_SIZE*2) {
				break;
			}
			vector<int64_t> coords;
			for (int64_t j = 0; j < UNIT_SIZE*2; j++) {
				coords.push_back(coords_all[i+j]);
			}
			coords.push_back(patch_size);
			coords.push_back(total);
			map<const char*, vector<int64_t>> osr_coords;
			osr_coords.insert(pair<const char*, vector<int64_t>>(slide_name, coords));
			cut_queue.push(osr_coords);
		}

		// cout << "count " << count << ", total " << total << endl;
	}
}


void cut_consumer(string save_path) {
	map<const char*, vector<int64_t>> osr_coords;
	const char* slide_name = nullptr;
	openslide_t* osr = nullptr;

    while (true)
    {
        PopResult res = cut_queue.pop(osr_coords);
        if (res == POP_STOP)
        {    
            // cout << "pop stop" << endl;
            break;
        }
        if (res == POP_UNEXPECTED)
        {
            // cout << "pop POP_UNEXPECTED" << endl;
            continue;
        }

        map<const char*, vector<int64_t>>::iterator itr = osr_coords.begin();
       	// const char* slide_name = itr->first;
       	vector<int64_t> coords = itr->second;

       	if (slide_name != itr->first) {
       		if (osr != nullptr) {
       			openslide_close(osr);
       		}
       		slide_name = itr->first;
       		osr = openslide_open(slide_name);
       		// cout << "switched slide " << slide_name << endl;
       	}

       	int64_t patch_size = coords[UNIT_SIZE*2];
       	for (int i = 0; i < UNIT_SIZE; i++) {
       		read_region_and_half_size(osr, coords[i*2], coords[i*2+1], patch_size, patch_size, save_path);
       	}

       	int64_t total = coords[UNIT_SIZE*2+1];
       	map<const char*, int64_t> unit_cut;
       	unit_cut.insert(pair<const char*, int64_t>(slide_name, total));
       	result_queue.push(unit_cut);
    }
}


void result_collector() {
	map<const char*, int64_t> cut_count;
	map<const char*, int64_t> unit_cut;

    while (true)
    {        
        PopResult res = result_queue.pop(unit_cut);
        if (res == POP_STOP)
        {    
            // cout << "pop stop" << endl;
            break;
        }
        if (res == POP_UNEXPECTED)
        {
            // cout << "pop POP_UNEXPECTED" << endl;
            continue;
        }

        map<const char*, int64_t>::iterator itr = unit_cut.begin();

       	const char* slide_name = itr->first;
       	if (cut_count.find(slide_name) == cut_count.end()) {
       		cut_count.insert(pair<const char*, int64_t>(slide_name, UNIT_SIZE));
       	} else {
       		cut_count[slide_name] += UNIT_SIZE;
       	}

       	int64_t total = itr->second;
       	int64_t count = cut_count[slide_name];
       	if (count % 200 == 0) {
       		cout << slide_name << " " << count << " / " << total << endl;
       	}
       	if (count == total) {
       		cout << slide_name << " finished cutting" << endl;
       	}

    }	
}


static void print_downsamples(openslide_t *osr) {
	for (int32_t level = 0; level < openslide_get_level_count(osr); level++) {
		printf("level %d: downsample: %g\n",
			   level,
			   openslide_get_level_downsample(osr, level));
	}
}



int main(int argc, char** argv) {
	vector<const char*> slide_names;
	slide_names.push_back("/home/hdd0/Develop/xxx/workflow/1.tif");
	slide_names.push_back("/home/hdd0/Develop/xxx/workflow/2.tif");
	slide_names.push_back("/home/hdd0/Develop/xxx/workflow/3.tif");

	string save_path = "/home/hdd0/Develop/tct/cpp";

	// cut_producer(slide_names);


	thread cut_producer_thread(cut_producer, slide_names);

	vector<thread> cut_consumer_threads;
    int thread_count = thread::hardware_concurrency();
    cout << "thread count " << thread_count << endl;
    if (thread_count == 0) {
        thread_count = 16;
    }
	for (int i = 0; i < thread_count; i++)
	{
	    thread cut_consumer_thread(cut_consumer, save_path);
	    cut_consumer_threads.push_back(move(cut_consumer_thread));
	    
	    // cut_consumer_threads.push_back(thread(cut_consumer));
	    // cut_consumer_threads.emplace_back(cut_consumer);
	}

	thread result_collect_thread(result_collector);


	cut_producer_thread.join();

    for (auto & t : cut_consumer_threads)
    {
        if (t.joinable())
            t.join();
    }

    result_collect_thread.join();


	cut_queue.Stop();
	result_queue.Stop();

	
	return 0;
}