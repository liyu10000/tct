package ocr;

import java.io.File;
import java.io.IOException;
import java.io.ByteArrayInputStream;
import java.awt.image.BufferedImage;
import javax.imageio.ImageIO;

import com.sun.jna.Library;
import com.sun.jna.Native;
//import com.sun.jna.Platform;
import com.sun.jna.Pointer;
//import com.sun.jna.ptr.ByteByReference;
import com.sun.jna.ptr.IntByReference;
import com.sun.jna.ptr.PointerByReference;


public class LabelReader {
	/* use System.load or System.loadLibrary, need to configure 
	static {
		try {
			//String path = System.getProperty("java.library.path");
			//System.out.println(path);
			System.load("C:/Users/liyud/eclipse-workspace/ocr/lib/ImageOperationLib.dll");
		} catch (Exception e) {
			e.printStackTrace();
		}
	}
	
	public native static int GetLableInfoPathFunc(String filePath, String[] imageData, int[] length, int[] width, int[] height);
	
	public static void main(String[] args) {
		new LabelReader();
		String filePath = "res/TC17042303.kfb";
		String[] imageData = null;
		int[] length = null;
		int[] width = null;
		int[] height = null;
		GetLableInfoPathFunc(filePath, imageData, length, width, height);
	}
	*/

	/* use native parameter passing
	public interface MyLibrary extends Library {
		MyLibrary INSTANCE = (MyLibrary) Native.loadLibrary(
				(Platform.isWindows() ? "C:/Users/liyud/eclipse-workspace/ocr/lib/ImageOperationLib.dll"
						              : "/home/tsimage001/eclipse-workspace/ocr/lib/ImageOperationLib.dll"), MyLibrary.class);
		int GetLableInfoPathFunc(String filePath, String[] imageData, int[] length, int[] width, int[] height);
	}
	
	public static void main(String[] args) {
		String filePath = "res/TC17042303.kfb";
		String[] imageData = null;
		int[] length = null;
		int[] width = null;
		int[] height = null;
		MyLibrary.INSTANCE.GetLableInfoPathFunc(filePath, imageData, length, width, height);
	}
	*/
	
	/* C method declaration
	 * int GetLableInfoPathFunc( constchar* szFilePath, unsignedchar** ImageData, int* nDataLength, int* nLabelWidth, int* nLabelHeight );
	 */
	
	public static interface MyLibrary extends Library {
		File dllPath = new File("lib/ImageOperationLib.dll");
		MyLibrary INSTANCE = (MyLibrary) Native.loadLibrary(dllPath.getAbsolutePath(), MyLibrary.class);
		int GetLableInfoPathFunc(String filePath, PointerByReference imageData, IntByReference length, IntByReference width, IntByReference height);
	}
	
	public static BufferedImage readLabelImage(String wsi_name) throws IOException {
		if (wsi_name.endsWith(".jpg")) {
			return ImageIO.read(new File(wsi_name));
		} else {
			String filePath = wsi_name;
			PointerByReference imageDataRef = new PointerByReference();
			IntByReference lengthRef = new IntByReference();
			IntByReference widthRef = new IntByReference();
			IntByReference heightRef = new IntByReference();
			int hasLabel = MyLibrary.INSTANCE.GetLableInfoPathFunc(filePath, imageDataRef, lengthRef, widthRef, heightRef);
//			System.out.println(lengthRef.getValue());
//			System.out.println(widthRef.getValue());
//			System.out.println(heightRef.getValue());
			
			if (hasLabel == 1) {
				Pointer p = imageDataRef.getValue();
				byte[] imageBuffer = p.getByteArray(0, lengthRef.getValue());
				ByteArrayInputStream bis = new ByteArrayInputStream(imageBuffer);
				BufferedImage bImage = ImageIO.read(bis);
	//			ImageIO.write(bImage, "jpg", new File("res/TC17042303.jpg"));
				return bImage;
			} else {
				return null;
			}
		}
	}
	
	public static void main(String[] args) throws IOException {
		readLabelImage("C:/Users/liyud/eclipse-workspace/ocr/res/C43.kfb");
//		File test = new File("lib/ImageOperationLib.dll");
//		System.out.println(test.getAbsolutePath());
	}
}