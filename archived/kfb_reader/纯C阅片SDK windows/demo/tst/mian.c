#include <windows.h>
#include "stdio.h"
#include "stdlib.h"
typedef struct IMAGE_INFO_STRUCT
{
	int DataFilePTR;
}ImageInfoStruct;
typedef signed int          KF_INT32;
static HINSTANCE hInstLibrary;
/// \note 2017.03.28 hushiliang 定义类型
typedef  signed  int KF_INT32;

 
/// \note 2017.03.28 hushiliang 定义初始化函数指针
typedef BOOL (__stdcall *DLLInitImageFileFunc)(ImageInfoStruct*,const char*);
DLLInitImageFileFunc InitImageFile;


//typedef  bool (__stdcall *DLLInitImageFileFunc)(ImageInfoStruct&, const char*);
/// \note 2017.03.28 hushiliang 定义获取头信息函数指针
typedef int (_stdcall*DLLGetHeaderInfoFunc)(ImageInfoStruct, KF_INT32*, KF_INT32*, KF_INT32*, float*, double*, float*, KF_INT32*);
DLLGetHeaderInfoFunc GetHeaderInfo;
/// \note 2017.03.28 hushiliang 定义获取图像函数指针
typedef unsigned char* (_stdcall*DLLGetImageStreamFunc)(ImageInfoStruct*, float, KF_INT32, KF_INT32, KF_INT32*, unsigned char**);//Define pointer function type
DLLGetImageStreamFunc GetImageStream;
/// \note 2017.03.28 hushiliang 定义获取RGB块图像函数指针
typedef unsigned char* (_stdcall*DLLGetRGBDataImageStreamFunc)(ImageInfoStruct*, float, KF_INT32, KF_INT32, KF_INT32*,KF_INT32*,KF_INT32*, unsigned char**);//Define pointer function type
DLLGetRGBDataImageStreamFunc GetRGBDataImageStream;//Define function pointer variables
/// \note 2017.03.28 hushiliang 定义删除图像函数指针
typedef BOOL(_stdcall*DLLDeleteImageDataFunc)(LPVOID);//Define pointer function type
DLLDeleteImageDataFunc DeleteImageData;
/// \note 2017.03.28 hushiliang 定义释放资源函数指针
typedef BOOL(_stdcall*DLLUnInitImageFileFunc)(ImageInfoStruct*);//Define pointer function type 
DLLUnInitImageFileFunc UnInitImageFile;
/// \note 2017.03.28 hushiliang 定义缩略图函数指针
typedef BOOL (_stdcall*DLLGetThumnailImageFunc)(ImageInfoStruct, unsigned char**, KF_INT32*, KF_INT32*, KF_INT32*);
DLLGetThumnailImageFunc GetThumnailImage;
int main(void)
    {

	KF_INT32*	khiImageHeight;//定义图片高度
   KF_INT32*	khiImageWidth;//定义图片宽度
   KF_INT32*	khiScanScale;//定义扫描倍率
   float*	khiSpendTime;//定义扫描时长
   double*	khiScanTime;//定义扫描时间
   float*	khiImageCapRes;//定义扫描分辨率
   KF_INT32*	khiImageBlockSize;//定义扫描块大小

   FILE* pf;
   unsigned char** ImageData;//定义数据块
   KF_INT32* nDataLength;//定义数据块长度
	
	float fScale;//定义需要倍率
	KF_INT32 nImagePosX;//定义X坐标
	KF_INT32 nImagePosY;//定义Y坐标


   int ret;
   ImageInfoStruct* sImageInfo;//定义数据信息

	HMODULE mylib;//定义Handle句柄
    mylib = LoadLibrary(".\\ImageOperationLib.dll");//加载动态库

	
    InitImageFile = (DLLInitImageFileFunc)GetProcAddress(mylib, "InitImageFileFunc");//加载初始化函数

	if(InitImageFile==NULL)
		return -1;
	sImageInfo=(ImageInfoStruct*)malloc(sizeof(ImageInfoStruct));//开辟空间
	ret=InitImageFile(sImageInfo,"k:\\2016-11-09 09_56_55.kfb");//使用初始化函数
	if(ret==0)
	{
		return -1;
	}  
	GetHeaderInfo = (DLLGetHeaderInfoFunc)GetProcAddress(mylib, "GetHeaderInfoFunc");//加载头信息获取函数
	if(GetHeaderInfo==NULL)
		return -1;
	khiImageHeight=(KF_INT32*)malloc(sizeof(KF_INT32));//开辟空间
	khiImageWidth=(KF_INT32*)malloc(sizeof(KF_INT32));
	khiScanScale=(KF_INT32*)malloc(sizeof(KF_INT32));
	khiSpendTime=(float*)malloc(sizeof(float));
	khiScanTime=(double*)malloc(sizeof(double));
	khiImageCapRes=(float*)malloc(sizeof(float));
	khiImageBlockSize=(KF_INT32*)malloc(sizeof(KF_INT32));
	GetHeaderInfo(*sImageInfo, khiImageHeight, khiImageWidth, khiScanScale, khiSpendTime, khiScanTime, khiImageCapRes, khiImageBlockSize);//使用头信息获取函数

	printf("%d",*khiImageHeight);//打印图像高度


	 ImageData=(unsigned char**)malloc(sizeof(unsigned char*));
    nDataLength=(KF_INT32*)malloc(sizeof(KF_INT32));

	fScale=20.0f;
	nImagePosX=0;
	nImagePosY=0;
	GetRGBDataImageStream = (DLLGetRGBDataImageStreamFunc)GetProcAddress(mylib, "GetImageRGBDataStreamFunc");//加载块信息获取函数

	GetRGBDataImageStream(sImageInfo, fScale, nImagePosX, nImagePosY, nDataLength,khiImageWidth,khiImageHeight, ImageData);//使用块信息获取函数
    printf("\n%d\n",*nDataLength);      
	pf = fopen( "ImageRGBStreamFunc.raw", "wb" );
           fwrite( *ImageData, sizeof(unsigned char), *nDataLength, pf);
           fclose( pf );

	DeleteImageData= (DLLDeleteImageDataFunc)GetProcAddress(mylib, "DeleteImageDataFunc");//加载数据清理函数
	DeleteImageData(*ImageData);//使用数据清理函数
	UnInitImageFile= (DLLUnInitImageFileFunc)GetProcAddress(mylib, "UnInitImageFileFunc");//加载释放资源函数
	UnInitImageFile(sImageInfo);///使用释放资源函数
	getchar();
	return 0;
}