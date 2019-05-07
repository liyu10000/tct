// g++ -o rotate rotate.cpp -I/usr/local/include -I/usr/local/include/opencv -L/usr/local/lib/ -lopencv_core -lopencv_highgui -lopencv_imgproc -lopencv_imgcodecs -lpthread -std=c++11

#include <stdio.h>
#include <string.h>
#include <vector>
#include <time.h>
#include <iostream>
#include <sys/stat.h>
#include <unistd.h>
#include <string>
#include <fstream>
#include <thread>
#include <opencv2/opencv.hpp>
#include <mutex>
#include <queue>
#include <condition_variable>


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


BlockingQueue<string> cut_queue;
BlockingQueue<int> res_queue;


inline bool exists(string &name) {
    struct stat buffer;
    return (stat (name.c_str(), &buffer) == 0);
}

void rotate_90_180_270(string inname, string out_dir)
{
    char* f = new char[inname.length() + 1];
    strcpy(f, inname.c_str());

    // get file basename, with extension
    char* basename = strrchr(f, '/');
    basename++;
    string name = string(basename);

    // split file basename
    size_t dot = name.find_last_of(".");
    string name_pre = name.substr(0, dot);
    string name_ext = name.substr(dot, name.size()-dot);
    
    Mat img = imread(f);
    Mat timg, img_90, img_180, img_270;
    
    // rotate 90
    string name_90 = out_dir + name_pre + "_90" + name_ext;
    if (! exists(name_90)) {
    	transpose(img, timg);
    	flip(timg, img_90, 0);
    
    	imwrite(name_90, img_90);
    }

    // rotate 180
    string name_180 = out_dir + name_pre + "_180" + name_ext;
    if (! exists(name_180)) {
    	flip(img, timg, 0);
    	flip(timg, img_180, 1);
    	imwrite(name_180, img_180);
    }

    // rotate 270
    string name_270 = out_dir + name_pre + "_270" + name_ext;
    if (! exists(name_270)) {
    	transpose(img, timg);
    	flip(timg, img_270, 1);
    	imwrite(name_270, img_270);
    }

    delete []f;

}


void Produce()
{
    String pattern = "/home/ssd_array0/Data/batch6.5_1216/original/*.bmp";
    vector<String> cv2_names;
    glob(pattern, cv2_names, false);
    
    cout << "# pics " << cv2_names.size() << endl;
    
    for (int i = 0; i < cv2_names.size(); i++)
    {
        string file_name = cv2_names[i];

        // cout << file_name << endl;

        // if (file_name.find("_hls09") == string::npos)
        // {
        //     cut_queue.push(file_name);
        // }     

        cut_queue.push(file_name);
    }
}


void Consume()
{
    string out_dir = "/home/ssd_array0/Data/batch6.5_1216/rotate/";

    string data;
    while (true)
    {        
        PopResult res = cut_queue.pop(data);
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

        
        // int q_size = cut_queue.size();
        // if (q_size % 1000 == 0)
        //     cout << "queue size " << q_size << endl;
        rotate_90_180_270(data, out_dir);

        res_queue.push(1);
    }
}


void Collect() {
    int data;
    int count = 0;

    while (true)
    {        
        PopResult res = res_queue.pop(data);
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

        
        count++;

        if (count % 1000 == 0)
            cout << "finished " << count << endl;
    }
}



int main(int argc, char** argv)
{

    //string inname = "/home/ssd0/Develop/liyu/batch6_1216/test.bmp";
    //string out_dir = "/home/ssd0/Develop/liyu/batch6_1216/";

    //rotate_90_180_270(inname, out_dir);    

    // Produce();
    // Consume();
    // Collect();


    thread produceThread(Produce);


    vector<thread> ts;
    int thread_count = thread::hardware_concurrency();
    if (thread_count > 8)
        thread_count = 8;
    cout << "thread count " << thread_count << endl;
    for (int i = 0; i < thread_count; i++)
    {
        thread consumerThread(Consume);
        ts.push_back(move(consumerThread));
        
        // ts.push_back(thread(Consume));
        // ts.emplace_back(Consume);
    }

    thread collectThread(Collect);


    produceThread.join();

    for (auto & t : ts)
    {
        if (t.joinable())
            t.join();
    }

    collectThread.join();


    cut_queue.Stop();
    res_queue.Stop();

    
    return 0;
}   
