package kfbslide;

import java.io.File;
import java.util.Arrays;
import java.util.List;

import com.sun.jna.Library;
import com.sun.jna.Native;
//import com.sun.jna.Platform;  // Platform.isWindows(), Platform.isLinux()
import com.sun.jna.Pointer;
import com.sun.jna.Structure;
import com.sun.jna.ptr.DoubleByReference;
import com.sun.jna.ptr.FloatByReference;
import com.sun.jna.ptr.IntByReference;
import com.sun.jna.ptr.PointerByReference;


public interface KfbLibrary extends Library {
//	File libPath = new File("lib/ImageOperationLib.dll");  // windows
	File libPath = new File("lib/libImageOperationLib.so");  // linux
	KfbLibrary INSTANCE = (KfbLibrary) Native.loadLibrary(libPath.getAbsolutePath(), KfbLibrary.class);
	
	
	// File identification structure
	class ImageInfoStruct extends Structure {
		public int DataFilePTR;

		@Override
		protected List<String> getFieldOrder() {
			return Arrays.asList("DataFilePTR");
		}
		
		public static class ByReference extends ImageInfoStruct implements Structure.ByReference {}
		public static class ByValue extends ImageInfoStruct implements Structure.ByValue {}
	}
	
	
	/* Open file
	 * int InitImageFileFunc(ImageInfoStruct* sImageInfo, constchar* Path)
		Parameter: 
		1.sImageInfo: The pointer of the KFB image
		2.Path: The path of the image(*.kfb) on the hard disk
	 */
	int InitImageFileFunc(ImageInfoStruct.ByReference sImageInfo, String Path);

	
	/* Close file
	 * int UnInitImageFileFunc(ImageInfoStruct* sImageInfo);
		Parameter: 
        1.sImageInfo :  The pointer of the KFB image, Get by InitImageFileFunc.
	 */
	int UnInitImageFileFunc(ImageInfoStruct.ByReference sImageInfo);
	
	
	/* Get image
	 * char * GetImageStreamFunc(ImageInfoStruct* sImageInfo, float fScale, int nImagePosX, int nImagePosY, int* nDataLength, unsignedchar** ImageStream);
    	Parameter:
		1.sImageInfo:The pointer of the KFB image, Get by InitImageFileFunc.
		2.fScale: The scale of the image which you want to get
        3.nImagePosX: The X coordinate(top,left) of the image, the number of the coordinate must be multiple of 256
        4.nImagePosY: The Y coordinate(top,left) of the image, the number of the coordinate must be multiple of 256
		5.nDataLength: Get the length of the returned image stream
		6.ImageStream: The pointer of the returned image. It’s JPEG format image stream. The image size is depend on the size of the block data, indicated with khiImageBlockSize in header information.
	 */
	Pointer GetImageStreamFunc(ImageInfoStruct.ByReference sImageInfo, float fScale, int nImagePosX, int nImagePosY, IntByReference nDataLength, PointerByReference ImageStream);
	
	
	/* Header information
	 * int GetHeaderInfoFunc(ImageInfoStruct sImageInfo, int* khiImageHeight, int* khiImageWidth, int* khiScanScale,float* khiSpendTime, double* khiScanTime,float* khiImageCapRes, int* khiImageBlockSize);
		Parameter:
		1.sImageInfo: The pointer of the KFB image, Get by InitImageFileFunc.
		2.khiImageHeight: Get the height of scanned area
		3.khiImageWidth: Get the width of the scanned area
		4.khiScanScale: Get the scale of the scanning
		5.khiSpendTime: Get the time of the scanning process takes
		6.khiScanTime: Get the start time of the scanning process
		7.khiImageCapRes: Get the ratio of the pixel and the actual size
		8.khiImageBlockSize: Get the size of the block
	 */
	int GetHeaderInfoFunc(ImageInfoStruct.ByReference sImageInfo, IntByReference khiImageHeight, IntByReference khiImageWidth, IntByReference khiScanScale, FloatByReference khiSpendTime, DoubleByReference khiScanTime, FloatByReference khiImageCapRes, IntByReference khiImageBlockSize);

	
	/* Get the image of the specified area
	 * int GetImageDataRoiFunc(ImageInfoStruct sImageInfo, float fScale, int sp_x, int sp_y, int nWidth, int nHeight,BYTE** pBuffer, int* DataLength, bool flag);
		Parameter: 
		1.sImageInfo: The pointer of the KFB image , Get by InitImageFileFunc.
		2.fScale: The scale of the image which you want to get
		3.sp_x: The X coordinates of the top left corner you want to get
		4.sp_y: The Y coordinates of the top left corner you want to get
		5.nWidth: The width of the ROI image block you want to get
		6.nHeight: The height of the ROI image block you want to get
		7.pBuffer: The pointer of the returned image block. Its format is JPEG
		8.DataLength: Get the length of the returned image stream.
		9.flag: The result of the reading.(reserve parameter)
	 */
	int GetImageDataRoiFunc(ImageInfoStruct.ByReference sImageInfo, float fScale, int sp_x, int sp_y, int nWidth, int nHeight, PointerByReference pBuffer, IntByReference DataLength, boolean flag);
	
	
	/* Get thumbnail
	 * int GetThumnailImagePathFunc(constchar* szFilePath, unsignedchar** ImageData, int* nDataLength, int* nThumWidth, int* nThumHeght);
		Parameter: 
		1.szFilePath: The path of the KFB image on the hard disk
		2.ImageData: The pointer of the returned image
		3.nDataLength: The length of the returned image stream, the stream with JPEG format
		4.nThumWidth: The the width of the returned image
		5.nThumHeght : The the height of the returned image
	 */
	int GetThumnailImageFunc(ImageInfoStruct.ByReference sImageInfo, PointerByReference ImageData, IntByReference nDataLength, IntByReference nThumbWidth, IntByReference nThumbHeight);
	int GetThumnailImagePathFunc(String szFilePath, PointerByReference ImageData, IntByReference nDataLength, IntByReference nThumbWidth, IntByReference nThumbHeight);
	
	
	/* Get preview image
	 * int GetPriviewInfoPathFunc(constchar* szFilePath, unsignedchar** ImageData, int* nDataLength, int* nPriviewWidth, int* nPriviewHeight);
		Parameter: 
		1.szFilePath: The path of the KFB image on the hard disk
		2.ImageData: The pointer of the returned image
		3.nDataLength: The size of the returned image stream, the stream with JPEG format
		4.nPriviewWidth: The width of the returned image
		5.nPriviewHeight : The height of the returned image
	 */
	int GetPriviewInfoFunc(ImageInfoStruct.ByReference sImageInfo, PointerByReference ImageData, IntByReference nDataLength, IntByReference nPriviewWidth, IntByReference nPriviewHeight);
	int GetPriviewInfoPathFunc(String szFilePath, PointerByReference ImageData, IntByReference nDataLength, IntByReference nPriviewWidth, IntByReference nPriviewHeight);
	
	
	/* Get label image
	 * int GetLableInfoPathFunc(constchar* szFilePath, unsignedchar** ImageData, int* nDataLength, int* nLabelWidth, int* nLabelHeight);
		Parameter: 
		1.szFilePath: The path of the KFB image on the hard disk
		2.ImageData: The pointer of returned image
		3.nDataLength: The size of the returned image
		4.nLabelWidth: The width of the returned image
		5.nLabelHeight : The height of the returned image
	 */
	int GetLableInfoFunc(ImageInfoStruct.ByReference sImageInfo, PointerByReference ImageData, IntByReference nDataLength, IntByReference nLabelWidth, IntByReference nLabelHeight);
	int GetLableInfoPathFunc(String szFilePath, PointerByReference ImageData, IntByReference nDataLength, IntByReference nLabelWidth, IntByReference nLabelHeight);
}
