package ocr;

import java.io.File;
import java.io.IOException;
import java.io.ByteArrayInputStream;
import java.awt.image.BufferedImage;
import javax.imageio.ImageIO;

import com.sun.jna.Library;
import com.sun.jna.Native;
import com.sun.jna.Platform;
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
	public interface WinLibrary extends Library {
		WinLibrary INSTANCE = (WinLibrary) Native.loadLibrary(
				(Platform.isWindows() ? "C:/Users/liyud/eclipse-workspace/ocr/lib/ImageOperationLib.dll"
						              : "/home/tsimage001/eclipse-workspace/ocr/lib/ImageOperationLib.dll"), WinLibrary.class);
		int GetLableInfoPathFunc(String filePath, String[] imageData, int[] length, int[] width, int[] height);
	}
	
	public static void main(String[] args) {
		String filePath = "res/TC17042303.kfb";
		String[] imageData = null;
		int[] length = null;
		int[] width = null;
		int[] height = null;
		WinLibrary.INSTANCE.GetLableInfoPathFunc(filePath, imageData, length, width, height);
	}
	*/
	
	/* C method declaration
	 * int GetLableInfoPathFunc( constchar* szFilePath, unsignedchar** ImageData, int* nDataLength, int* nLabelWidth, int* nLabelHeight );
	 */
	
	public static interface WinLibrary extends Library {
		File dllPath = new File("lib/ImageOperationLib.dll");
		WinLibrary INSTANCE = (WinLibrary) Native.loadLibrary(dllPath.getAbsolutePath(), WinLibrary.class);
		int GetLableInfoPathFunc(String filePath, PointerByReference imageData, IntByReference length, IntByReference width, IntByReference height);
	}
	
	public static interface LinuxLibrary extends Library {
		File soPath = new File("lib/libImageOperationLib.so");
		LinuxLibrary INSTANCE = (LinuxLibrary) Native.loadLibrary(soPath.getAbsolutePath(), LinuxLibrary.class);
		int GetLableInfoPathFunc(String filePath, PointerByReference imageData, IntByReference length, IntByReference width, IntByReference height);
	}
	
	public static BufferedImage readLabelImage(File wsi_name) throws IOException {
		if (wsi_name.getName().endsWith(".jpg")) {
			return ImageIO.read(wsi_name);
		} else {
			String filePath = wsi_name.getAbsolutePath();
			PointerByReference imageDataRef = new PointerByReference();
			IntByReference lengthRef = new IntByReference();
			IntByReference widthRef = new IntByReference();
			IntByReference heightRef = new IntByReference();
			int hasLabel = 0;
			if (Platform.isWindows()) {
				hasLabel = WinLibrary.INSTANCE.GetLableInfoPathFunc(filePath, imageDataRef, lengthRef, widthRef, heightRef);
			} else if (Platform.isLinux()) {
				hasLabel = LinuxLibrary.INSTANCE.GetLableInfoPathFunc(filePath, imageDataRef, lengthRef, widthRef, heightRef);
			}
//			System.out.println(lengthRef.getValue());
//			System.out.println(widthRef.getValue());
//			System.out.println(heightRef.getValue());

			if (hasLabel == 1) {
				Pointer p = imageDataRef.getValue();
				byte[] imageBuffer = p.getByteArray(0, lengthRef.getValue());
				ByteArrayInputStream bis = new ByteArrayInputStream(imageBuffer);
				BufferedImage bImage = ImageIO.read(bis);
				return bImage;
			}
		}
		return null;
	}
	
	public static void main(String[] args) throws IOException {
		BufferedImage labelImage = readLabelImage(new File("res/TC17042832.kfb"));
		if (labelImage != null) {
			ImageIO.write(labelImage, "jpg", new File("res/TC17042832.jpg"));
		}
	}
}