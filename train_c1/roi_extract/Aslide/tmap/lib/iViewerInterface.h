/**
* @date         2017-10-16
* @filename     iViewerInterface.h
* @purpose      interface for TMAP file
* @version      2.5.1
* @history      initial draft
* @author       Morgan Lei, UNIC, Beijing, China
* @copyright    Morgan.Lei@unic-tech.cn, UNIC Technologies Inc, 2005-2016. All rights reserved.
*/

#ifndef __IVIEWERSDK_C__
#define __IVIEWERSDK_C__

#include <inttypes.h>
enum _TMAP_IMAGE_TYPE
{
	uImageThumbnail = 0, // 小图，用于浏览器显示图标，图像大小 <= 256
	uImageNavigate, // 导航图，用于显示缩略图，图像大小 <= 640
	uImageMacro, // 切片组织部分整体图像
	uImageLabel, // 切片标签图像
	uImageMacroLabel, // 整个切片大体图像
	uImageTile, // 组成切片的小图像块，每个图像块图像大小为256*256
	uImageWhole, // 切片数字图像，指扫描后的图像
	uImageAll
};

typedef void* HANDLE;

extern "C" 
{
    struct ImgSize
	{
	    int64_t imgsize;
	    int width;
		int height;
		int depth;
	};
	//*****************************************************************************************************
	// 功能： 打开Tmap格式的文件，该函数被最先调用，才能进行后续操作，支持多线程打开多个Tmap文件或同一个Tmap文件，通过hFile区分不同的线程
	//        如果对用一个打开的文件再次调用该函数，表示建立一个新连接，获得一个新句柄，请在相关的线程中使用这个句柄。
	// 参数： pFile 要打开的Tmap格式文件，例如"c:\\abc.tmap"
	//        hFile 如果打开成功，则获得该文件的句柄，以后通过该句柄对该文件进行操作
	// 返回： 打开成功，返回True，并获得hFile；打开失败，返回False。
	//*****************************************************************************************************
    HANDLE OpenTmapFile(const char *pcFile, int len);

	//*****************************************************************************************************
	// 功能： 关闭Tmap格式的文件，该函数被最后调用
	// 参数： hFile 要关闭的Tmap格式文件的句柄
	// 返回： 关闭成功，返回True；关闭失败，返回False。
	//*****************************************************************************************************
    bool CloseTmapFile(HANDLE hFile );

	//*****************************************************************************************************
	// 功能： 取得Tmap格式文件的版本号。
	// 参数： hFile 要访问的Tmap格式文件的句柄。
	// 返回： 读取成功，返回文件版本号；读取失败，返回0。
	//*****************************************************************************************************
    int GetTmapVersion(HANDLE hFile);

	//*****************************************************************************************************
	// 功能： 取得Tmap文件扫描时的最大倍率。
	// 参数： hFile 要访问的Tmap格式文件的句柄。
	// 返回： 读取成功，返回倍率；读取失败，返回0。
	//*****************************************************************************************************
    int GetScanScale(HANDLE hFile);

	//*****************************************************************************************************
	// 功能： 取得Tmap文件扫描时的分级数。分级原则是原始图像宽度不断除以2，直到图像宽度小于256为止，除的次数就是分级数。
	// 参数： hFile 要访问的Tmap格式文件的句柄。
	// 返回： 读取成功，返回分级数；读取失败，返回0。
	//*****************************************************************************************************
    int GetLayerNum(HANDLE hFile);

	//*****************************************************************************************************
	// 功能： 取得Tmap文件的对焦层数。对于单层扫描图像，返回1。对于多层扫描，返回扫描层数。
	// 参数： hFile 要访问的Tmap格式文件的句柄。
	// 返回： 读取成功，返回图像扫描层数；读取失败，返回0。
	//*****************************************************************************************************
    int GetFocusNumber(HANDLE hFile);

	//*****************************************************************************************************
	// 功能： 取得Tmap文件的总共图像块数目。每个图像都是由若干图像块组成，每个图像块大小为256*256。
	// 参数： hFile 要访问的Tmap格式文件的句柄。
	// 返回： 读取成功，返回图像块数；读取失败，返回0。
	//*****************************************************************************************************
    int GetTileNumber(HANDLE hFile);

	//*****************************************************************************************************
	// 功能： 设置当前的对焦面。对单层扫描来说，只有一个对焦面。对多层扫描来说，高于最佳对焦面为正，低于最佳对焦面为负
	// 参数： hFile 要访问的Tmap格式文件的句柄。
	// 返回： 设置成功，true；读取失败，返回false。
	//*****************************************************************************************************
    bool SetFocusLayer(HANDLE hFile, const int nFocus = 0);

		//*****************************************************************************************************
	// 功能： 读取当前的对焦面数值。
	// 参数： hFile 要访问的Tmap格式文件的句柄。
	// 返回： 读取成功，返回当前的对焦面数值。
	//*****************************************************************************************************
    int GetFocusLayer(HANDLE hFile);

	//*****************************************************************************************************
	// 功能： 取得Tmap格式文件的像素分辨率，单位是mm，是换算到100倍下的像素分辨率
	// 参数： hFile 要访问的Tmap格式文件的句柄
	// 返回： Tmap格式文件在100x下的像素分辨率，对应40x分辨率需要乘以2.5，对应20x分辨率需要乘以5，以此类推
	//*****************************************************************************************************
    float GetPixelSize(HANDLE hFile);

	//*****************************************************************************************************
	// 功能： 取得Tmap格式文件的整体图片信息
	// 参数： hFile 要访问的Tmap格式文件的句柄
	//        _TMAP_IMAGE_TYPE eType, 获取图像的类型，参见前面说明
	//        nWidth 获取图片的宽度
	//        nHeight 获取图片的高度
	//        nColor 获取图像的像素位数， 彩色是24bits，黑白是8bits
	// 返回： 返回图像占用的字节数
	//*****************************************************************************************************
    int64_t GetImageInfo(HANDLE hFile, const _TMAP_IMAGE_TYPE eType, int &nWidth, int &nHeight, int &nDepth);
    ImgSize GetImageInfoEx(HANDLE hFile, const _TMAP_IMAGE_TYPE eType);
    
	//*****************************************************************************************************
	// 功能： 取得Tmap格式文件的数据
	// 参数： hFile 要访问的Tmap格式文件的句柄
	//        _TMAP_IMAGE_TYPE eType, 获取图像的类型，参见前面说明，需要注意图像不能是uImageTile或者uImageWhole
	//        pucBuffer 调用方分配的图像内存，该内存不能小于GetImageInfo返回的字节数
	//        nBufferLength 分配内存的长度，该长度不能低于GetImageInfo返回的字节长度
	// 返回： 成功返回true，失败返回false
	//*****************************************************************************************************
    bool GetImageData(HANDLE hFile, const _TMAP_IMAGE_TYPE eType, unsigned char *pucBuffer,const int nBufferLength);

	//*****************************************************************************************************
	// 功能： 取得Tmap格式文件的切片数字图像信息
	// 参数： hFile 要访问的Tmap格式文件的句柄
	//        nLeft, nTop, nRight, nBottom, 截取ROI图像的左上右下，单位是像素坐标；
	//		  fScale, 截取图像的倍率，不能超过扫描图像的最大倍率；
	//        nWidth 获取图片的宽度
	//        nHeight 获取图片的高度
	// 返回： 返回图像占用的字节数
	//*****************************************************************************************************
    int64_t GetImageSize(HANDLE hFile, const int nLeft, const int nTop, const int nRight,const int nBottom, const float fScale, int &nWidth, int &nHeight);
    ImgSize GetImageSizeEx(HANDLE hFile, const int nLeft, const int nTop, const int nRight,const int nBottom, const float fScale);

	//*****************************************************************************************************
	// 功能： 取得Tmap格式文件的切片数字图像
	// 参数： hFile 要访问的Tmap格式文件的句柄
	//  	  nIndex, 内存编号，为多线程取图，系统内部有30个内存可用，编号从0-30，以区分不同的内存块
	//        nLeft, nTop, nRight, nBottom, 截取ROI图像的左上右下，单位是像素坐标；
	//		  fScale, 截取图像的倍率，不能超过扫描图像的最大倍率；
	//        pucBuffer 调用方分配的图像内存，该内存不能小于GetImageSize返回的字节数
	//        nBufferLength 分配内存的长度，该长度不能小于GetImageSize返回的字节长度
	// 返回： 返回图像占用的字节数
	//*****************************************************************************************************
    bool GetCropImageData(HANDLE hFile, const int nIndex, const int nLeft, const int nTop,
		const int nRight, const int nBottom, const float fScale,
		unsigned char *pucBuffer, const int nBufferLength);

    unsigned char* GetCropImageDataEx(HANDLE hFile, const int nIndex, const int nLeft, const int nTop,
      const int nRight, const int nBottom, const float fScale, const int nBufferLength);


	//*****************************************************************************************************
	// 功能： 取得Tmap格式文件的切片数字图像
	// 参数： hFile 要访问的Tmap格式文件的句柄
	//  	  nDownsampleScale, 采样图级别，取值为1, 2, 4, 8, 16, 32, 64, ..., 1就是指扫描倍率的图像
	//        nTileRow， 在当前采样图倍率的情况下的图像块行数；
	//		  nTileCol， 在当前采样图倍率的情况下的图像块列数；
	// 返回： 返回采样图像块的指针。图像块大小为256*256*3
	//*****************************************************************************************************
	// get bitmap data of a tile
    const unsigned char *GetTileData(HANDLE hFile, const int nDownsampleScale,
		const int nTileRow, const int nTileCol);
}

#endif // __IVI:EWERSDK_C__
