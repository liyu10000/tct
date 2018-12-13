//g++ -o rgb2bgr rgb2bgr.cpp -I/usr/local/include -I/usr/local/include/opencv -L/usr/local/lib/ -lopencv_core -lopencv_highgui -lopencv_imgproc -lopencv_imgcodecs -lpthread -std=c++11

#include <stdio.h>
#include <string.h>
#include <vector>
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
        if (m_stopFlag) // 停止
        {
            return POP_STOP;
        }        
        if (queue<T>::empty())
        {
            m_cond.wait(lock);
        }
        if (m_stopFlag) // 停止
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


void cvtRgb2Bgr(string inname, string out_dir)
{
	// cout << "---------enter func: " << inname << endl;
	char* f = new char[inname.length() + 1];
	strcpy(f, inname.c_str());

	char* basename = strrchr(f, '/');
	basename++;
	string outname = out_dir + string(basename);

	Mat image = imread(f);
	// if (image.empty()) {
	// 	cout << "image empty: " << inname << endl;
	// } else {
	// 	cout << image.rows << ", " << image.cols << endl;
	// }
	cvtColor(image, image, COLOR_BGR2RGB);
	imwrite(outname, image);

	delete []f;
	
	cout << outname << endl;
}


void Produce()
{
	String pattern = "/home/data_samba/Code_by_yuli/batch6_hls_1216/train/*.bmp";
	vector<String> cv2_names;
	glob(pattern, cv2_names, false);

	for (int i = 0; i < cv2_names.size(); i++)
	{
		string file_name = cv2_names[i];
		g_queue.push(file_name);
	}
}


void Consume()
{
	string out_dir = "/home/data_samba/Code_by_yuli/batch6_hls_1216/train_right/";

	string data;
    while (true)
    {
        // 取数据
        PopResult res = g_queue.pop(data);
        if (res == POP_STOP) // 线程应该停止
        {    
        	// cout << "pop stop" << endl;
            break;
        }
        if (res == POP_UNEXPECTED) // 意外唤醒
        {
        	// cout << "pop POP_UNEXPECTED" << endl;
            continue;
        }

        // 处理数据
        cvtRgb2Bgr(data, out_dir);
    }
}





int main(int argc, char** argv)
{
	// 启动生产者线程和消费者线程（也可以启动多个线程）
    thread produceThread(Produce);

    thread consumerThread1(Consume);
    thread consumerThread2(Consume);
    thread consumerThread3(Consume);
    thread consumerThread4(Consume);
    thread consumerThread5(Consume);
    thread consumerThread6(Consume);
    thread consumerThread7(Consume);
    thread consumerThread8(Consume);
    thread consumerThread9(Consume);

    // vector<thread> ts;
    // for (int i = 0; i < 10; i++)
    // {
    	
    // 	ts.push_back(consumerThread);
    // }


    produceThread.join();


    // for (int i = 0; i < ts.size(); i++)
    // {
    // 	ts[i].join();
    // }



    consumerThread1.join();
    consumerThread2.join();
    consumerThread3.join();
    consumerThread4.join();
    consumerThread5.join();
    consumerThread6.join();
    consumerThread7.join();
    consumerThread8.join();
    consumerThread9.join();

    // 停止线程
    g_queue.Stop();

    return 0;
}	
