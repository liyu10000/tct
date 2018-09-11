import org.bytedeco.javacpp.*;
import static org.bytedeco.javacpp.lept.*;
import static org.bytedeco.javacpp.tesseract.*;


public class TesseractRun {
    
    public String detect() throws Exception {
        BytePointer outText;

        TessBaseAPI api = new TessBaseAPI();
        // Initialize tesseract-ocr with English, without specifying tessdata path
        if (api.Init(".", "ENG") != 0) {
            System.err.println("Could not initialize tesseract.");
            System.exit(1);
        }

        // Open input image with leptonica library
        PIX image = pixRead("./res/label.jpg");
        api.SetImage(image);
        // Get OCR result
        outText = api.GetUTF8Text();
        String string = outText.getString();
        System.out.println("OCR output:\n" + string);

        // Destroy used object and release memory
        api.End();
        outText.deallocate();
        pixDestroy(image);
    }
}

/*
import java.io.File;
import net.sourceforge.tess4j.Tesseract;
import net.sourceforge.tess4j.ITesseract;

public class TesseractRun {
	TesseractRun() {}
	ITesseract instance = new Tesseract();

	public String ocr_filename(String filename) throws Exception {
		File image = new File(filename);
		String result = instance.doOCR(image);
		System.out.println(result);
		return result;
	}

	public static void main(String[] args) throws Exception {
		(new TesseractRun()).ocr_filename("./label.jpg");
	}
}
*/