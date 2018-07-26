#include <stdio.h>
#include <string.h>
#include <dlfcn.h>
typedef struct IMAGE_INFO_STRUCT
{
    int DataFilePTR;
}ImageInfoStruct;//Create structure

typedef signed int KF_INT32;
typedef void   *LPVOID;

typedef int (*DLLInitImageFileFunc)(ImageInfoStruct*,const char*);//Define pointer function type
DLLInitImageFileFunc InitImageFile;//Define function pointer variables

typedef int (*DLLGetHeaderInfoFunc)(ImageInfoStruct, KF_INT32*, KF_INT32*, KF_INT32*, float*, double*, float*, KF_INT32*);//Define pointer function type
DLLGetHeaderInfoFunc GetHeaderInfo;//Define function pointer variables

typedef unsigned char* (*DLLGetImageStreamFunc)(ImageInfoStruct*, float, KF_INT32, KF_INT32, KF_INT32*, unsigned char**);//Define pointer function type
DLLGetImageStreamFunc GetImageStream;//Define function pointer variables

typedef unsigned char* (*DLLGetRGBDataImageStreamFunc)(ImageInfoStruct*, float, KF_INT32, KF_INT32, KF_INT32*,KF_INT32*,KF_INT32*, unsigned char**);//Define pointer function type
DLLGetRGBDataImageStreamFunc GetRGBDataImageStream;//Define function pointer variables

typedef int (*DLLDeleteImageDataFunc)(LPVOID);//Define pointer function type
DLLDeleteImageDataFunc DeleteImageData;//Define function pointer variables

typedef int (*DLLUnInitImageFileFunc)(ImageInfoStruct*);//Define pointer function type
DLLUnInitImageFileFunc UnInitImageFile;//Define function pointer variables

typedef int (*DLLGetThumnailImageFunc)(ImageInfoStruct, unsigned char**, KF_INT32*, KF_INT32*, KF_INT32*);//Define pointer function type
DLLGetThumnailImageFunc GetThumnailImage;//Define function pointer variables

const char LIB_PATH[50]="./libImageOperationLib.so";


int main(void)
    {
    void *handle = NULL;
    KF_INT32*	khiImageHeight;
    KF_INT32*	khiImageWidth;
    KF_INT32*	khiScanScale;
    float*	khiSpendTime;
    double*	khiScanTime;
    float*	khiImageCapRes;
    KF_INT32*	khiImageBlockSize;
    unsigned char** ImageData;
    KF_INT32* nDataLength;
    float fScale;
    KF_INT32 nImagePosX;
    KF_INT32 nImagePosY;
    KF_INT32 ret;
    FILE* pf;
    ImageInfoStruct* sImageInfo;
    handle = dlopen(LIB_PATH, RTLD_LAZY);//Load dynamic library
    *(void* *)&InitImageFile=dlsym(handle,"InitImageFileFunc");//Get open file function

    if(InitImageFile==NULL)
        return -1;
    sImageInfo=(ImageInfoStruct*)malloc(sizeof(ImageInfoStruct));
    ret=InitImageFile(sImageInfo,"/home/liang/Desktop/2015-04-13 08_40_05.kfb");
    if(ret==0)
    {
        return -1;
    }

    *(void* *)&GetHeaderInfo=dlsym(handle,"GetHeaderInfoFunc");//Get open file function
    if(GetHeaderInfo==NULL)
        return -1;   
    khiImageHeight=(KF_INT32*)malloc(sizeof(KF_INT32));
    khiImageWidth=(KF_INT32*)malloc(sizeof(KF_INT32));
    khiScanScale=(KF_INT32*)malloc(sizeof(KF_INT32));
    khiSpendTime=(float*)malloc(sizeof(float));
    khiScanTime=(double*)malloc(sizeof(double));
    khiImageCapRes=(float*)malloc(sizeof(float));
    khiImageBlockSize=(KF_INT32*)malloc(sizeof(KF_INT32));
    GetHeaderInfo(*sImageInfo, khiImageHeight, khiImageWidth, khiScanScale, khiSpendTime, khiScanTime, khiImageCapRes, khiImageBlockSize);//Get header information


    ImageData=(unsigned char**)malloc(sizeof(unsigned char*));
    nDataLength=(KF_INT32*)malloc(sizeof(KF_INT32));
    fScale=20.0f;
    nImagePosX=10240;
    nImagePosY=10240;

    //*(void* *)&GetImageStream=dlsym(handle,"GetImageStreamFunc");//Get open file function
    //GetImageStream(sImageInfo, fScale, nImagePosX, nImagePosY, nDataLength, ImageData);//Get image stream data

    *(void* *)&GetRGBDataImageStream=dlsym(handle,"GetImageRGBDataStreamFunc");//Get open file function
        GetRGBDataImageStream(sImageInfo, fScale, nImagePosX, nImagePosY, nDataLength,khiImageWidth,khiImageHeight, ImageData);
    pf = fopen( "ImageStreamFunc.jpg", "wb" );
    printf("\n%d\n",*nDataLength);
    fwrite( *ImageData, sizeof(unsigned char), *nDataLength, pf);
    fclose( pf );

    *(void* *)&DeleteImageData=dlsym(handle,"DeleteImageDataFunc");//Get open file function
    DeleteImageData(*ImageData);//Release image stream data

    *(void* *)&UnInitImageFile=dlsym(handle,"UnInitImageFileFunc");//Get open file function
    UnInitImageFile(sImageInfo);//Release memory
    //getchar();
    return 0;
}
