package kfbslide;

import java.awt.image.BufferedImage;
import java.io.ByteArrayInputStream;
import java.io.IOException;

import javax.imageio.ImageIO;

import com.sun.jna.Pointer;
import com.sun.jna.ptr.DoubleByReference;
import com.sun.jna.ptr.FloatByReference;
import com.sun.jna.ptr.IntByReference;
import com.sun.jna.ptr.PointerByReference;

import kfbslide.KfbLibrary.ImageInfoStruct;


public class KfbSlide {
	private ImageInfoStruct.ByReference sImageInfo = new ImageInfoStruct.ByReference();
	private int width = -1;
	private int height = -1;
	private float capRes = -1;  // the ratio of pixel and actual size
	private float downsample = -1;  // downsample of top level
	
	public KfbSlide OpenSlide(String filename) {
		int status = KfbLibrary.INSTANCE.InitImageFileFunc(this.sImageInfo, filename);
		if (status == 1)
			return this;
		else
			System.err.println("failed to open slide");
			return null;
	}
	
	public void close() {
		int status = KfbLibrary.INSTANCE.UnInitImageFileFunc(this.sImageInfo);
		if (status != 1) {
			System.err.println("failed to close slide");
		}
	}
	
	public int getWidth() {
		if (this.width == -1) {
			this.getHeaderInfo();
		}
		return this.width;
	}
	
	public int getHeight() {
		if (this.height == -1) {
			this.getHeaderInfo();
		}
		return this.height;
	}
	
	public void getHeaderInfo() {
		IntByReference khiImageHeight = new IntByReference(); 
		IntByReference khiImageWidth = new IntByReference();
		IntByReference khiScanScale = new IntByReference();
		FloatByReference khiSpendTime = new FloatByReference();
		DoubleByReference khiScanTime = new DoubleByReference();
		FloatByReference khiImageCapRes = new FloatByReference();
		IntByReference khiImageBlockSize = new IntByReference();
		int status = KfbLibrary.INSTANCE.GetHeaderInfoFunc(this.sImageInfo, khiImageHeight, khiImageWidth, khiScanScale, 
				khiSpendTime, khiScanTime, khiImageCapRes, khiImageBlockSize);
		if (status != 1) {
			System.err.println("failed to get header info");
			return;
		}
		
		this.width = khiImageWidth.getValue();
		this.height = khiImageHeight.getValue();
		this.capRes = khiImageCapRes.getValue();
//		System.out.println(khiImageWidth.getValue());
//		System.out.println(khiImageHeight.getValue());
//		System.out.println(khiScanScale.getValue());
//		System.out.println(khiSpendTime.getValue());
//		System.out.println(khiScanTime.getValue());
//		System.out.println(khiImageCapRes.getValue());
//		System.out.println(khiImageBlockSize.getValue());
	}
	
	public BufferedImage read_region(int[] position, int level, int[] size) {
		if (this.downsample == -1) {
			this.getDownsample();
		}
		float fScale = this.downsample / (level + 1);
		int sp_x = position[0];
		int sp_y = position[1];
		int nWidth = size[0];
		int nHeight = size[1];
		PointerByReference pBuffer = new PointerByReference();
		IntByReference DataLength = new IntByReference();
		boolean flag = true;  // what is this for? don't know.
		int status = KfbLibrary.INSTANCE.GetImageDataRoiFunc(this.sImageInfo, fScale, sp_x, sp_y, nWidth, nHeight, pBuffer, DataLength, flag);
		if (status != 1) {
			System.err.println("failed to read ROI");
			return null;
		}
		
		Pointer p = pBuffer.getValue();
		byte[] imageBuffer = p.getByteArray(0, DataLength.getValue());
		ByteArrayInputStream bis = new ByteArrayInputStream(imageBuffer);
		BufferedImage bImage = null;
		try {
			bImage = ImageIO.read(bis);
		} catch (IOException e) {
			e.printStackTrace();
		}
		return bImage;
	}
	
	private void getDownsample() {
		PointerByReference ImageData = new PointerByReference();
		IntByReference nDataLength = new IntByReference();
		IntByReference nThumbWidth = new IntByReference();
		IntByReference nThumbHeight = new IntByReference();
		int status = KfbLibrary.INSTANCE.GetThumnailImageFunc(this.sImageInfo, ImageData, nDataLength, nThumbWidth, nThumbHeight);
		if (status != 1) {
			System.err.println("failed to get downsample");
			return;
		}
		
		this.downsample = this.getWidth() / nThumbWidth.getValue() * this.capRes;
	}
	
	public BufferedImage get_thumbnail() {
		PointerByReference ImageData = new PointerByReference();
		IntByReference nDataLength = new IntByReference();
		IntByReference nThumbWidth = new IntByReference();
		IntByReference nThumbHeight = new IntByReference();
		int status = KfbLibrary.INSTANCE.GetThumnailImageFunc(this.sImageInfo, ImageData, nDataLength, nThumbWidth, nThumbHeight);
		if (status != 1) {
			System.err.println("failed to get thumbnail image");
			return null;
		}
		
		Pointer p = ImageData.getValue();
		byte[] imageBuffer = p.getByteArray(0, nDataLength.getValue());
		ByteArrayInputStream bis = new ByteArrayInputStream(imageBuffer);
		BufferedImage bImage = null;
		try {
			bImage = ImageIO.read(bis);
		} catch (IOException e) {
			e.printStackTrace();
		}
		return bImage;
	}
	
	public BufferedImage get_thumbnail(String szFilePath) {
		PointerByReference ImageData = new PointerByReference();
		IntByReference nDataLength = new IntByReference();
		IntByReference nThumbWidth = new IntByReference();
		IntByReference nThumbHeight = new IntByReference();
		int status = KfbLibrary.INSTANCE.GetThumnailImagePathFunc(szFilePath, ImageData, nDataLength, nThumbWidth, nThumbHeight);
		if (status != 1) {
			System.err.println("failed to get thumbnail image");
			return null;
		}
		
		Pointer p = ImageData.getValue();
		byte[] imageBuffer = p.getByteArray(0, nDataLength.getValue());
		ByteArrayInputStream bis = new ByteArrayInputStream(imageBuffer);
		BufferedImage bImage = null;
		try {
			bImage = ImageIO.read(bis);
		} catch (IOException e) {
			e.printStackTrace();
		}
		return bImage;
	}
		
	public BufferedImage get_preview() {
		PointerByReference ImageData = new PointerByReference();
		IntByReference nDataLength = new IntByReference();
		IntByReference nPriviewWidth = new IntByReference();
		IntByReference nPriviewHeight = new IntByReference();
		int status = KfbLibrary.INSTANCE.GetPriviewInfoFunc(this.sImageInfo, ImageData, nDataLength, nPriviewWidth, nPriviewHeight);
		if (status != 1) {
			System.err.println("failed to get whole slide preview");
			return null;
		}
		
		Pointer p = ImageData.getValue();
		byte[] imageBuffer = p.getByteArray(0, nDataLength.getValue());
		ByteArrayInputStream bis = new ByteArrayInputStream(imageBuffer);
		BufferedImage bImage = null;
		try {
			bImage = ImageIO.read(bis);
		} catch (IOException e) {
			e.printStackTrace();
		}
		return bImage;
	}
	
	public BufferedImage get_preview(String szFilePath) {
		PointerByReference ImageData = new PointerByReference();
		IntByReference nDataLength = new IntByReference();
		IntByReference nPriviewWidth = new IntByReference();
		IntByReference nPriviewHeight = new IntByReference();
		int status = KfbLibrary.INSTANCE.GetPriviewInfoPathFunc(szFilePath, ImageData, nDataLength, nPriviewWidth, nPriviewHeight);
		if (status != 1) {
			System.err.println("failed to get whole slide preview");
			return null;
		}
		
		Pointer p = ImageData.getValue();
		byte[] imageBuffer = p.getByteArray(0, nDataLength.getValue());
		ByteArrayInputStream bis = new ByteArrayInputStream(imageBuffer);
		BufferedImage bImage = null;
		try {
			bImage = ImageIO.read(bis);
		} catch (IOException e) {
			e.printStackTrace();
		}
		return bImage;
	}
	
	public BufferedImage get_label() {
		PointerByReference ImageData = new PointerByReference();
		IntByReference nDataLength = new IntByReference();
		IntByReference nLabelWidth = new IntByReference();
		IntByReference nLabelHeight = new IntByReference();
		int status = KfbLibrary.INSTANCE.GetLableInfoFunc(this.sImageInfo, ImageData, nDataLength, nLabelWidth, nLabelHeight);
		if (status != 1) {
			System.err.println("failed to get label image");
			return null;
		}
		
		Pointer p = ImageData.getValue();
		byte[] imageBuffer = p.getByteArray(0, nDataLength.getValue());
		ByteArrayInputStream bis = new ByteArrayInputStream(imageBuffer);
		BufferedImage bImage = null;
		try {
			bImage = ImageIO.read(bis);
		} catch (IOException e) {
			e.printStackTrace();
		}
		return bImage;
	}
	
	public BufferedImage get_label(String szFilePath) {
		PointerByReference ImageData = new PointerByReference();
		IntByReference nDataLength = new IntByReference();
		IntByReference nLabelWidth = new IntByReference();
		IntByReference nLabelHeight = new IntByReference();
		int status = KfbLibrary.INSTANCE.GetLableInfoPathFunc(szFilePath, ImageData, nDataLength, nLabelWidth, nLabelHeight);
		if (status != 1) {
			System.err.println("failed to get label image");
			return null;
		}
		
		Pointer p = ImageData.getValue();
		byte[] imageBuffer = p.getByteArray(0, nDataLength.getValue());
		ByteArrayInputStream bis = new ByteArrayInputStream(imageBuffer);
		BufferedImage bImage = null;
		try {
			bImage = ImageIO.read(bis);
		} catch (IOException e) {
			e.printStackTrace();
		}
		return bImage;
	}

	// deprecated
	public BufferedImage getImageStream() {
		float fScale = 1.0f;
		int nImagePosX = 256;
		int nImagePosY = 256;
		IntByReference nDataLength = new IntByReference();
		PointerByReference ImageStream = new PointerByReference();
		Pointer result = KfbLibrary.INSTANCE.GetImageStreamFunc(this.sImageInfo, fScale, nImagePosX, nImagePosY, nDataLength, ImageStream);
		System.out.println(result.getString(0));
		
		Pointer p = ImageStream.getValue();
		byte[] imageBuffer = p.getByteArray(0, nDataLength.getValue());
		ByteArrayInputStream bis = new ByteArrayInputStream(imageBuffer);
		BufferedImage bImage = null;
		try {
			bImage = ImageIO.read(bis);
		} catch (IOException e) {
			e.printStackTrace();
		}
		return bImage;
	}
	
}
