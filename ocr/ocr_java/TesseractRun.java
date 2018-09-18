package ocr;

import java.io.File;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import net.sourceforge.tess4j.Tesseract;
import net.sourceforge.tess4j.TesseractException;

import java.awt.image.BufferedImage;

//import ocr.LabelReader;

public class TesseractRun {
    Tesseract instance;
    TesseractRun() {
        // System.out.println(System.getProperty("os.name"));
        instance = new Tesseract();
        // set tessdata path, could add to java library path or system path. 
        // note: need to use the same version as tesseract
        if (System.getProperty("os.name").equals("Linux")) {
            instance.setDatapath("/usr/share/tesseract-ocr/");
        } else {
            instance.setDatapath("lib/tessdata");
        }
    }

    public String detect(String filename) throws TesseractException {
        File image = new File(filename);
        String result = instance.doOCR(image);
        return findLabel(result);
    }
    
    public String detect(File image) throws TesseractException {
        String result = instance.doOCR(image);
        return findLabel(result);
    }
    
    public String detect(BufferedImage image) throws TesseractException {
        String result = instance.doOCR(image);
        return findLabel(result);
    }
    
    public String findLabel(String text) {
        Pattern pattern = Pattern.compile("[a-zA-Z]*[0-9]{5,}");
        Matcher matcher = pattern.matcher(text);
        if (matcher.find()) {
            return matcher.group(0);
        } else {
            return "";
        }
    }
    
    public String getLabel(File filename, BufferedImage labelImage) throws TesseractException {
        String label = findLabel(filename.getName());
        if (label.equals("")) {
            label = detect(labelImage);
        }
        return label;
    }

    public static void main(String[] args) throws Exception {
        TesseractRun tess = new TesseractRun();
        String label = tess.detect("res/label.jpg");
//      String label = tess.detect(new File("res/label.jpg"));
//      String label = tess.detect(ImageIO.read(new File("res/label.jpg")));
//      String label = tess.detect(LabelReader.read_label("C:/Users/liyud/eclipse-workspace/ocr/res/TC17042303.jpg"));
        System.out.println(label);

    }
}
