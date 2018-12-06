## caffe model
https://github.com/soeaver/caffe-model/tree/master/cls

## Install caffe on Ubuntu 16.04 with gpu

#### useful links:
https://github.com/BVLC/caffe/wiki/Ubuntu-16.04-or-15.10-Installation-Guide
https://blog.csdn.net/wuzuyu365/article/details/52430657


### Install thirdparty packages
1. install packages
<pre> 
	sudo apt update
	sudo apt upgrade
	sudo apt install -y build-essential cmake git pkg-config
	sudo apt install -y libprotobuf-dev libleveldb-dev libsnappy-dev libhdf5-serial-dev protobuf-compiler
	sudo apt install -y libatlas-base-dev 
	sudo apt install -y --no-install-recommends libboost-all-dev
	sudo apt install -y libgflags-dev libgoogle-glog-dev liblmdb-dev
</pre>

2. install python

3. install cuda (9.0), cudnn (7.0), opencv (3.4.0)


### Adapt caffe config files
1. download caffe: [github link](https://github.com/BVLC/caffe)

2. If download caffe from [github link](https://github.com/BVLC/caffe), the version should be 1.0. Go to caffe folder, edit _/src/caffe/util/blocking_queue.cpp_, after line 89, add new line: _template class BlockingQueue<Datum*>;_

3. Modify Makefile.config
3.1 _cp Makefile.config.example Makefile.config_
3.2 edit Makefile.config, find and modify the following lines:
<pre>
	PYTHON_INCLUDE := /usr/include/python2.7 /usr/local/lib/python2.7/dist-packages/numpy/core/include  
	WITH_PYTHON_LAYER := 1  
	INCLUDE_DIRS := $(PYTHON_INCLUDE) /usr/local/include /usr/include/hdf5/serial  
	LIBRARY_DIRS := $(PYTHON_LIB) /usr/local/lib /usr/lib /usr/lib/x86_64-linux-gnu /usr/lib/x86_64-linux-gnu/hdf5/serial  
</pre>
3.3 since cuda 8.0, compute capability 2.0 and 2.1 are discarded, so delete the following two lines:
<pre>
	-gencode arch=compute_20,code=sm_20
	-gencode arch=compute_20,code=sm_21
</pre>

4. fix libhdf5 links
<pre>
	find . -type f -exec sed -i -e 's^"hdf5.h"^"hdf5/serial/hdf5.h"^g' -e 's^"hdf5_hl.h"^"hdf5/serial/hdf5_hl.h"^g' '{}' \;
	cd /usr/lib/x86_64-linux-gnu
	sudo ln -s libhdf5_serial.so.10.1.0 libhdf5.so
	sudo ln -s libhdf5_serial_hl.so.10.0.2 libhdf5_hl.so
</pre>

5. install python packages
<pre>
	cd python
	for req in $(cat requirements.txt); do sudo -H pip install $req --upgrade; done
</pre>

6. Modify Makefile
replace this line:
<pre>
	NVCCFLAGS += -ccbin=$(CXX) -Xcompiler -fPIC $(COMMON_FLAGS)
</pre>
with the following line:
<pre>
	NVCCFLAGS += -D_FORCE_INLINES -ccbin=$(CXX) -Xcompiler -fPIC $(COMMON_FLAGS)
</pre>

7. Modify CMakeLists.txt
add the following line:
<pre>
	# ---[ Includes
	set(${CMAKE_CXX_FLAGS} "-D_FORCE_INLINES ${CMAKE_CXX_FLAGS}")
</pre>


### Build and Compile caffe
<pre>
	make all -j8
	make test -j8
	sudo make runtest -j8
	sudo make pycaffe -j8 (add "export PYTHONPATH=/home/caffe/python:$PYTHONPATH" to "~/.bashrc")
</pre>


### Debug
1. 
error at make all: 
<pre>
	caffe.cpp:(.text+0x15eb): undefined reference to `caffe::Net<float>::CopyTrainedLayersFrom(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const&)` collect2: error: ld returned 1 exit status
</pre>
solve:
<pre>
	delete libcaffe.so present under /usr/local/lib
</pre>
links:
	https://github.com/rbgirshick/py-faster-rcnn/issues/477
	https://github.com/BVLC/caffe/issues/3396

2.
error:
<pre>
	.build_release/tools/caffe: error while loading shared libraries: libcudart.so.9.0: cannot open shared object file: No such file or directory
</pre>
solve:
<pre>
	in ~/.bashrc, should have the two lines:
		export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH
		export PATH=/usr/local/cuda/bin:$PATH
	sudo ldconfig /usr/local/cuda/lib64
</pre>
links:
	https://github.com/BVLC/caffe/issues/4944

3.
error at make pycaffe:
<pre>
	python/caffe/_caffe.cpp:10:31: fatal error: numpy/arrayobject.h: No such file or directory
</pre>
solve:
<pre>
	sudo apt install python-numpy
</pre>
links:
	https://blog.csdn.net/wuzuyu365/article/details/52430657

4.
error at _import caffe_ in python:
<pre>
	ImportError: No module named skimage.io
</pre>
solve:
<pre>
	pip install scikit-image
	sudo apt-get install python-matplotlib python-numpy python-pil python-scipy
	sudo apt-get install build-essential cython
	sudo apt-get install python-skimage
</pre>
links:
	https://github.com/yahoo/open_nsfw/issues/13
	https://github.com/BVLC/caffe/issues/50

5.
error at _import caffe_ in python:
<pre>
	ImportError: No module named google.protobuf.internal
</pre>
solve:
<pre>
	sudo apt install python-protobuf
</pre>
links:
	https://stackoverflow.com/questions/37666241/importing-caffe-results-in-importerror-no-module-named-google-protobuf-interna
	https://stackoverflow.com/questions/37666241/importing-caffe-results-in-importerror-no-module-named-google-protobuf-interna/37905483
