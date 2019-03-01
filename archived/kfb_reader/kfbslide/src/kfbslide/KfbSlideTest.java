package kfbslide;

import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;

import javax.imageio.ImageIO;

import kfbslide.KfbSlide;


public class KfbSlideTest {
	
	public static void main(String[] args) {
		String filename = "res/TC17042597.kfb";
		KfbSlide slide = new KfbSlide();
		slide = slide.OpenSlide(filename);
		
		System.out.println(String.valueOf(slide.getWidth()) + ", " + String.valueOf(slide.getHeight()));
		BufferedImage bImage = slide.read_region(new int[] {10000,10000}, 1, new int[] {800,800});
//		BufferedImage bImage = slide.get_thumbnail();
		System.out.println(String.valueOf(bImage.getWidth()) + ", " + String.valueOf(bImage.getHeight()));
		File output = new File("res/test.jpg");
		try {
			ImageIO.write(bImage, "jpg", output);
		} catch (IOException e) {
			e.printStackTrace();
		}
		
		slide.close();
		System.out.println("finished");
	}
}
