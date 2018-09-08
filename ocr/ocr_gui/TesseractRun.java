import java.io.File;
import net.sourceforge.tess4j.Tesseract;
import net.sourceforge.tess4j.ITesseract;

public class TesseractRun {
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