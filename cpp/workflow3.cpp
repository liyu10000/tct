// g++ -o workflow1 workflow1.cpp -L/usr/local/lib -lopenslide -I/usr/local/include/openslide
// g++ -o workflow1 workflow1.cpp -L/usr/local/lib -lopenslide -I/usr/local/include/openslide  `pkg-config --cflags --libs glib-2.0`
// g++ -o workflow1 workflow1.cpp -L/usr/local/lib -lopenslide -I/usr/local/include/openslide  `pkg-config --cflags --libs glib-2.0` -I/usr/local/include -I/usr/local/include/opencv -L/usr/local/lib/ -lopencv_core -lopencv_highgui -lopencv_imgproc -lopencv_imgcodecs -lpthread -std=c++11
// g++ -o workflow1 workflow1.cpp -L/usr/local/lib -lopenslide -I/usr/local/include/openslide  `pkg-config --cflags --libs glib-2.0` -I/usr/local/include -I/usr/local/include/opencv -L/usr/local/lib/ -lopencv_core -lopencv_highgui -lopencv_imgproc -lopencv_imgcodecs -lpthread -std=c++11 -lboost_filesystem -lboost_system
// g++ -g -Wall -o workflow3 workflow3.cpp -L/usr/local/lib -lopenslide -I/usr/local/include/openslide  `pkg-config --cflags --libs glib-2.0` -I/usr/local/include -I/usr/local/include/opencv -L/usr/local/lib/ -lopencv_core -lopencv_highgui -lopencv_imgproc -lopencv_imgcodecs -lpthread -std=c++11 -lboost_filesystem -lboost_system libdarknet.so -ldl

#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <dlfcn.h>
#include <vector>
#include <iostream>
#include <math.h>
#include <unistd.h>
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
        if (m_stopFlag)
        {
            return POP_STOP;
        }        
        if (queue<T>::empty())
        {
            m_cond.wait(lock);
        }
        if (m_stopFlag)
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


struct network;
typedef struct network network;

typedef struct{
    int classes;
    char **names;
} metadata;

typedef struct {
    int w;
    int h;
    int c;
    float *data;
} image;

typedef struct{
    float x, y, w, h;
} box;

typedef struct detection{
    box bbox;
    int classes;
    float *prob;
    float *mask;
    float objectness;
    int sort_class;
} detection;


// int network_width(network *net);
int (*network_width)(network *net);

// int network_height(network *net);
int (*network_height)(network *net);

// network *net = load_network(char *cfg, char *weights, int clear);
network* (*load_network)(char *cfg, char *weights, int clear);

// float *predictions = network_predict(network net, float *X);
float* (*network_predict)(network net, float *X);

// metadata get_metadata(char *file);
metadata (*get_metadata)(char *file);

// image load_image(char *filename, int w, int h, int c);
// image load_image_color(char *filename, int w, int h);
image (*load_image_color)(char *filename, int w, int h);

// float *network_predict_image(network *net, image im);
float* (*network_predict_image)(network *net, image im);

// detection *get_network_boxes(network *net, int w, int h, float thresh, float hier_thresh, int *map, int relative, int *num);
detection* (*get_network_boxes)(network *net, int w, int h, float thresh, float hier_thresh, int *map, int relative, int *num);

// void do_nms_obj(detection *dets, int total, int classes, float thresh);
void (*do_nms_obj)(detection *dets, int total, int classes, float thresh);

// void free_image(image im);
void (*free_image)(image im);

// void free_detections(detection *dets, int n);
void (*free_detections)(detection *dets, int n);

// image make_image(int w, int h, int c);
image (*make_image)(int w, int h, int c);

// void cuda_set_device(int n)
void (*cuda_set_device)(int n);


void* handle = nullptr;

void open_lib(char *lib_name) {
  handle = dlopen(lib_name, RTLD_LAZY);
  if (!handle) {
    fprintf(stderr, "%s\n", dlerror());
    exit(1);
  }

  dlerror();  // clear any existing error
}


void close_lib() {
  dlclose(handle);
}


void load_functions() {
  network_width = (int (*)(network*)) dlsym(handle, "network_width");

  network_height = (int (*)(network*)) dlsym(handle, "network_height");

  load_network = (network* (*)(char*, char*, int)) dlsym(handle, "load_network");

  network_predict = (float* (*)(network, float*)) dlsym(handle, "network_predict");

  get_metadata = (metadata (*)(char*)) dlsym(handle, "get_metadata");

  load_image_color = (image (*)(char*, int, int)) dlsym(handle, "load_image_color");

  network_predict_image = (float* (*)(network*, image)) dlsym(handle, "network_predict_image");

  get_network_boxes = (detection* (*)(network*, int, int, float, float, int*, int, int*)) dlsym(handle, "get_network_boxes");

  do_nms_obj = (void (*)(detection*, int, int, float)) dlsym(handle, "do_nms_obj");

  free_image = (void (*)(image)) dlsym(handle, "free_image");

  free_detections = (void (*)(detection*, int)) dlsym(handle, "free_detections");

  make_image = (image (*)(int, int, int)) dlsym(handle, "make_image");

  cuda_set_device = (void (*)(int)) dlsym(handle, "cuda_set_device");
}



image mat_to_image(cv::Mat img_src)
{
    int h = img_src.rows;
    int w = img_src.cols;
    int c = img_src.channels();
    int step = img_src.step;
    image out = make_image(h, w, c);

    unsigned char *data = (unsigned char *)img_src.data;

    int i, j, k, count = 0;
    for(k= 0; k < c; ++k){
        for(i = 0; i < h; ++i){
            for(j = 0; j < w; ++j){
                out.data[count++] = data[i*step + j*c + k] / 255.; // Normalize
            }
        }
    }

    return out;
}


void detect_on_img(network *net, metadata meta, image im, float thresh, float hier_thresh, float nms) {
  int num;
  network_predict_image(net, im);
  detection *dets = get_network_boxes(net, im.w, im.h, thresh, hier_thresh, nullptr, 0, &num);
  do_nms_obj(dets, num, meta.classes, nms);

  // print detections
  for (int j = 0; j < num; j++) {
    for (int i = 0; i < meta.classes; i++) {
      if (dets[j].prob[i] > .0) {
        printf("%s, probability %f, objectness %f ", meta.names[i], dets[j].prob[i], dets[j].objectness);
        printf("(%f, %f, %f, %f)\n", dets[j].bbox.x, dets[j].bbox.y, dets[j].bbox.w, dets[j].bbox.h);
      }
    }
  }

  // free_image(im);
  free_detections(dets, num);
}



typedef struct {
    const char* slide_name;
    int64_t *xys;
    int64_t number;
    int64_t patch_size;
    int64_t total;
} cut_unit;

typedef struct {
    const char* slide_name;
    image img;
    int64_t total;
} yolo_unit;


BlockingQueue<map<const char*, vector<int64_t>>> cut_queue;
BlockingQueue<yolo_unit> yolo_queue;
BlockingQueue<map<const char*, int64_t>> result_queue;
int64_t CUT_UNIT_SIZE = 4;


image read_region_and_half_size(openslide_t* osr, int64_t x, int64_t y, int64_t w, int64_t h) {

  uint32_t *buf = (uint32_t *) g_slice_alloc(w * h * 4);
  openslide_read_region(osr, buf, x, y, 0, w, h);

  Mat mat(h, w, CV_8UC4, buf);
  pyrDown(mat, mat);
  cvtColor(mat, mat, CV_RGBA2BGR);

  g_slice_free1(w * h * 4, buf);

  image img = mat_to_image(mat);

  return img;
}


void cut_producer(vector<const char*> slide_names) {
  for (const char* slide_name : slide_names) {
    openslide_t* osr = openslide_open(slide_name);
    int64_t w, h;
    openslide_get_level0_dimensions(osr, &w, &h);
    openslide_close(osr);
    cout << slide_name << " " << w << " x " << h << endl;

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
    int64_t total = (int64_t) (floor(count / 2 / CUT_UNIT_SIZE) * CUT_UNIT_SIZE);
    for (int64_t i = 0; i < count; i += CUT_UNIT_SIZE*2) {
      if (count - i < CUT_UNIT_SIZE*2) {
        break;
      }
      vector<int64_t> coords;
      for (int64_t j = 0; j < CUT_UNIT_SIZE*2; j++) {
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


void cut_consumer() {
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

        int64_t patch_size = coords[CUT_UNIT_SIZE*2];
        int64_t total = coords[CUT_UNIT_SIZE*2+1];
        for (int i = 0; i < CUT_UNIT_SIZE; i++) {
          image img = read_region_and_half_size(osr, coords[i*2], coords[i*2+1], patch_size, patch_size);
          yolo_unit yunit;
          yunit.slide_name = slide_name;
          yunit.img = img;
          yunit.total = total;
          yolo_queue.push(yunit);
        }
    }
}


void yolo_predictor(char *cfgfile, char *weightfile, char *metafile, int gpu, char* image_name) {
    // specify which gpu to use
    cuda_set_device(gpu);

    // initialize model
    network *net = load_network(cfgfile, weightfile, 0);
    metadata meta = get_metadata(metafile);

    float thresh = 0.5;
    float hier_thresh = 0.5;
    float nms = 0.45;

    // yolo_unit yunit;

    // while (true)
    // {        
    //     PopResult res = yolo_queue.pop(yunit);
    //     if (res == POP_STOP)
    //     {    
    //         // cout << "pop stop" << endl;
    //         break;
    //     }
    //     if (res == POP_UNEXPECTED)
    //     {
    //         // cout << "pop POP_UNEXPECTED" << endl;
    //         continue;
    //     }

    //     detect_on_img(net, meta, yunit.img, thresh, hier_thresh, nms);

    //     map<const char*, int64_t> runit;
    //     runit.insert(pair<const char*, int64_t>(yunit.slide_name, yunit.total));
    //     result_queue.push(runit);
    // } 

    // char* image_name = (char*) "/home/hdd0/Develop/xxx/gen608/2017-09-07-09_24_10_x18891_y23547_r0.bmp";
    image im = load_image_color(image_name, 0, 0);

    for (int i = 0; i < 100; i++) {
        detect_on_img(net, meta, im, thresh, hier_thresh, nms);

        // map<const char*, int64_t> runit;
        // runit.insert(pair<const char*, int64_t>(yunit.slide_name, yunit.total));
        // result_queue.push(runit);
    }

    printf("finished %s\n", image_name);
}


void result_collector() {
  map<const char*, int64_t> cut_count;
  map<const char*, int64_t> runit;

    while (true)
    {        
        PopResult res = result_queue.pop(runit);
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

        map<const char*, int64_t>::iterator itr = runit.begin();

        const char* slide_name = itr->first;
        if (cut_count.find(slide_name) == cut_count.end()) {
          cut_count.insert(pair<const char*, int64_t>(slide_name, 0));
        }
        cut_count[slide_name] += 1;
        

        int64_t total = itr->second;
        int64_t count = cut_count[slide_name];
        if (count % 200 == 0) {
          cout << slide_name << " " << count << " / " << total << endl;
        }
        if (count == total) {
          cout << slide_name << " finished ==================" << endl;
        }

    } 
}


int main(int argc, char** argv) {

    char * lib_name = (char *)"libdarknet.so";
    open_lib(lib_name);
    load_functions();


    char *cfgfile = (char *)"/home/hdd0/Develop/xxx/hdf5_h5/yolo_train3_release/train3.cfg";
    char *weightfile = (char *)"/home/hdd0/Develop/xxx/hdf5_h5/yolo_train3_release/train3.backup";
    char *metafile = (char *)"/home/hdd0/Develop/xxx/hdf5_h5/yolo_train3_release/train3.data";


    vector<const char*> slide_names;
    slide_names.push_back("/home/hdd0/Develop/xxx/workflow/1.tif");
    slide_names.push_back("/home/hdd0/Develop/xxx/workflow/2.tif");
    slide_names.push_back("/home/hdd0/Develop/xxx/workflow/3.tif");


    thread cut_producer_thread(cut_producer, slide_names);

    vector<thread> cut_consumer_threads;
    int thread_count = thread::hardware_concurrency();
    cout << "thread count " << thread_count << endl;
    if (thread_count == 0) {
        thread_count = 16;
    }
    for (int i = 0; i < thread_count; i++)
    {
      thread cut_consumer_thread(cut_consumer);
      cut_consumer_threads.push_back(move(cut_consumer_thread));
      
      // cut_consumer_threads.push_back(thread(cut_consumer));
      // cut_consumer_threads.emplace_back(cut_consumer);
    }

    // vector<thread> yolo_predictor_threads;
    // int gpus = 2;
    // for (int i = 0; i < gpus; i++) {
    //     thread yolo_predictor_thread(yolo_predictor, cfgfile, weightfile, metafile, i);
    //     yolo_predictor_threads.push_back(move(yolo_predictor_thread));
    // }


    pid_t pid1 = fork();
    if (pid1 == (pid_t) 0) {  // child process1
        yolo_predictor(cfgfile, weightfile, metafile, 0, "/home/hdd0/Develop/xxx/gen608/2017-09-07-09_24_10_x18891_y23547_r0.bmp");
    } else {  // parent process

    }

    pid_t pid2 = fork();
    if (pid2 == (pid_t) 0) {  // child process2
        yolo_predictor(cfgfile, weightfile, metafile, 1, "/home/hdd0/Develop/xxx/gen608/2017-09-07-09_24_10_x18891_y23547_r90.bmp");
    } else {  // parent process

    }


    thread result_collect_thread(result_collector);


    cut_producer_thread.join();

    for (auto & t : cut_consumer_threads)
    {
        if (t.joinable())
            t.join();
    }

    // for (auto & t : yolo_predictor_threads)
    // {
    //     if (t.joinable())
    //         t.join();
    // }    

    result_collect_thread.join();


    cut_queue.Stop();
    yolo_queue.Stop();
    result_queue.Stop();

    close_lib();

    return 0;
}