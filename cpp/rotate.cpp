//g++ -o rotate rotate.cpp -I/usr/local/include -I/usr/local/include/opencv -L/usr/local/lib/ -lopencv_core -lopencv_highgui -lopencv_imgproc -lopencv_imgcodecs -lpthread -std=c++11

#include <stdio.h>
#include <string.h>
#include <vector>
#include <time.h>
#include <iostream>
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


BlockingQueue<string> g_queue;



void rotate_90_180_270(string inname, string out_dir)
{
    // cout << "---------enter func: " << inname << endl;
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

    // clock_t time1, time2, time3, time4;

    // time1 = clock();
    
    Mat img = imread(f);
    Mat timg, img_90, img_180, img_270;

    // time2 = clock();
    
    // rotate 90
    string name_90 = out_dir + name_pre + "_90" + name_ext;
    transpose(img, timg);
    flip(timg, img_90, 0);
    
    // time3 = clock();
    
    imwrite(name_90, img_90);

    // time4 = clock();
    // cout << "image reading time: " << time2 - time1 << endl;
    // cout << "image process time: " << time3 - time2 << endl;
    // cout << "image saving time: " << time4 - time3 << endl;
    // cout << "total time: " << time4 - time1 << endl;
    
    // rotate 180
    string name_180 = out_dir + name_pre + "_180" + name_ext;
    flip(img, timg, 0);
    flip(timg, img_180, 1);
    imwrite(name_180, img_180);

    // rotate 270
    string name_270 = out_dir + name_pre + "_270" + name_ext;
    transpose(img, timg);
    flip(timg, img_270, 1);
    imwrite(name_270, img_270);

    delete []f;

}


void Produce()
{
    String pattern = "/home/ssd0/Develop/liyu/batch6_1216/train/*.bmp";
    vector<String> cv2_names;
    glob(pattern, cv2_names, false);
    
    cout << "# pics " << cv2_names.size() << endl;
    
    for (int i = 0; i < cv2_names.size(); i++)
    {
        string file_name = cv2_names[i];

        if (file_name.find("_hls09") == string::npos)
        {
            g_queue.push(file_name);
        }     
        
    }
}


void Consume()
{
    string out_dir = "/home/hdd_array0/batch_1216_rotate_c3/";
    // string out_dir = "/home/ssd0/Develop/liyu/batch6_1216/test/result/";

    string data;
    while (true)
    {        
        // å–æ•°æ®
        PopResult res = g_queue.pop(data);
        if (res == POP_STOP) // çº¿ç¨‹åº”è¯¥åœæ­¢
        {    
            // cout << "pop stop" << endl;
            break;
        }
        if (res == POP_UNEXPECTED) // æ„å¤–å”¤é†’
        {
            // cout << "pop POP_UNEXPECTED" << endl;
            continue;
        }

        // // å¤„ç†æ•°æ®
        
        // int q_size = g_queue.size();
        // if (q_size % 1000 == 0)
        //     cout << "queue size " << q_size << endl;
        rotate_90_180_270(data, out_dir);
    }
}





int main(int argc, char** argv)
{

    //string inname = "/home/ssd0/Develop/liyu/batch6_1216/test.bmp";
    //string out_dir = "/home/ssd0/Develop/liyu/batch6_1216/";

    //rotate_90_180_270(inname, out_dir);    

 // // å¯åŠ¨ç”Ÿäº§è€…çº¿ç¨‹å’Œæ¶ˆè´¹è€…çº¿ç¨‹ï¼ˆä¹Ÿå¯ä»¥å¯åŠ¨å¤šä¸ªçº¿ç¨‹ï¼‰
    // thread produceThread(Produce);
    Produce();
    
    Consume();


//  vector<thread> ts;
//     int thread_count = thread::hardware_concurrency();
//     cout << "thread count " << thread_count << endl;
//     if (thread_count == 0)
//         thread_count = 16;
//  for (int i = 0; i < thread_count; i++)
//  {
//         thread consumerThread(Consume);
//         ts.push_back(move(consumerThread));
        
//         // ts.push_back(thread(Consume));
//         // ts.emplace_back(Consume);
//  }


//     produceThread.join();

    

//     for (auto & t : ts)
//     {
//         if (t.joinable())
//             t.join();
//     }


//     g_queue.Stop();


 //    // åœæ­¢çº¿ç¨‹
    
    
    return 0;
}   