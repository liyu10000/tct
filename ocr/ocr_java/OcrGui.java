package ocr;

import java.awt.Font;
//import java.awt.Color;
import java.awt.Component;
import java.awt.Container;
import java.awt.GridBagLayout;
import java.awt.GridBagConstraints;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
//import java.awt.event.KeyEvent;
import java.awt.image.BufferedImage;
import java.awt.Image;
import java.awt.Insets;
import java.io.File;
//import java.io.IOException;

//import javax.imageio.ImageIO;
import java.util.ArrayList;

import javax.swing.JFrame;
import javax.swing.JPanel;
import javax.swing.JButton;
import javax.swing.JLabel;
import javax.swing.JTextField;
import javax.swing.filechooser.FileFilter;
import javax.swing.filechooser.FileNameExtensionFilter;
import javax.swing.JFileChooser;
import javax.swing.JOptionPane;
import javax.swing.ImageIcon;

import ocr.TesseractRun;
import ocr.LabelReader;

public class OcrGui {
	private static int w1 = 512;
	private static int w2 = 300;
	private static int h = 512;
	private static JFrame frame;
	private static JLabel image;
	private static JLabel wsi;
	private static JLabel wsiText;
	private static JTextField labelText;
	
	private static int index;
	private static ArrayList<LabelItem> labelItems;
	
	private static TesseractRun tess;

	public OcrGui() {
		guiSetup();
		changeFont(frame, wsi.getFont().deriveFont(wsi.getFont().getSize2D()+4));
		index = -1;
		labelItems = new ArrayList<>();
		tess = new TesseractRun();
	}
	
	private void guiSetup() {
		frame = new JFrame("OCR");
		frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);

		JPanel panel = new JPanel();
		panel.setLayout(new GridBagLayout());
		GridBagConstraints c = new GridBagConstraints();

		// set layout for label image
		image = new JLabel(new ImageIcon(new BufferedImage(w1, h, 5)));
		c.fill = GridBagConstraints.BOTH;
		c.anchor = GridBagConstraints.CENTER;
		c.weightx = 0.5;
		c.gridwidth = 5;
		c.gridheight = 5;
		c.gridx = 0;
		c.gridy = 0;
		panel.add(image, c);

		// set layout for open file button
		JButton open_f = new MyButton("open file");
		c.fill = GridBagConstraints.HORIZONTAL;
		c.anchor = GridBagConstraints.CENTER;
		c.insets = new Insets(15,0,15,0);
		c.ipady = 30;
		c.weightx = 0.5;
		c.gridwidth = 2;
		c.gridheight = 1;
		c.gridx = 5;
		c.gridy = 0;
		panel.add(open_f, c);

		// set layout for open dir button
		JButton open_d = new MyButton("open dir");
		c.fill = GridBagConstraints.HORIZONTAL;
		c.anchor = GridBagConstraints.CENTER;
		c.insets = new Insets(15,0,15,0);
		c.weightx = 0.5;
		c.gridwidth = 2;
		c.gridheight = 1;
		c.gridx = 7;
		c.gridy = 0;
		panel.add(open_d, c);

		// set layout for wsi
		wsi = new JLabel("filename:");
		c.fill = GridBagConstraints.NONE;
		c.anchor = GridBagConstraints.LINE_END;
		c.insets = new Insets(15,0,15,20);
		//c.weightx = 0.5;
		c.gridwidth = 1;
		c.gridheight = 1;
		c.gridx = 6;
		c.gridy = 1;
		panel.add(wsi, c);

		// set layout for wsi text
		wsiText = new JLabel("XXXXXXXX.kfb");
		c.fill = GridBagConstraints.HORIZONTAL;
		c.anchor = GridBagConstraints.CENTER;
		c.insets = new Insets(15,0,15,0);
		c.weightx = 0.5;
		c.gridwidth = 2;
		c.gridheight = 1;
		c.gridx = 7;
		c.gridy = 1;
		panel.add(wsiText, c);

		// set layout for label
		JLabel label = new JLabel("label:");
		c.fill = GridBagConstraints.NONE;
		c.anchor = GridBagConstraints.LINE_END;
		c.insets = new Insets(15,0,15,20);
		//c.weightx = 0.5;
		c.gridwidth = 1;
		c.gridheight = 1;
		c.gridx = 6;
		c.gridy = 2;
		panel.add(label, c);

		// set layout for label input area
		labelText = new JTextField();
		labelText.setText("XXXXXXXX");
		c.fill = GridBagConstraints.HORIZONTAL;
		c.anchor = GridBagConstraints.CENTER;
		c.insets = new Insets(15,0,15,0);
		c.weightx = 0.5;
		c.gridwidth = 2;
		c.gridheight = 1;
		c.gridx = 7;
		c.gridy = 2;
		panel.add(labelText, c);

		// set layout for previous button
		JButton prev = new MyButton("previous");
		c.fill = GridBagConstraints.HORIZONTAL;
		c.anchor = GridBagConstraints.CENTER;
		c.insets = new Insets(15,0,15,0);
		c.weightx = 0.5;
		c.gridwidth = 2;
		c.gridheight = 1;
		c.gridx = 5;
		c.gridy = 3;
		panel.add(prev, c);

		// set layout for next button
		JButton next = new MyButton("next");
		c.fill = GridBagConstraints.HORIZONTAL;
		c.anchor = GridBagConstraints.CENTER;
		c.insets = new Insets(15,0,15,0);
		c.weightx = 0.5;
		c.gridwidth = 2;
		c.gridheight = 1;
		c.gridx = 7;
		c.gridy = 3;
		panel.add(next, c);

		// set layout for rename button
		JButton rename = new MyButton("rename");
		c.fill = GridBagConstraints.HORIZONTAL;
		c.anchor = GridBagConstraints.CENTER;
		c.insets = new Insets(15,0,15,0);
		c.weightx = 0.5;
		c.gridwidth = 2;
		c.gridheight = 1;
		c.gridx = 5;
		c.gridy = 4;
		panel.add(rename, c);

		// set layout for rename and next button
		JButton proceed = new MyButton("rename and next");
		c.fill = GridBagConstraints.HORIZONTAL;
		c.anchor = GridBagConstraints.CENTER;
		c.insets = new Insets(15,0,15,0);
		c.weightx = 0.5;
		c.gridwidth = 2;
		c.gridheight = 1;
		c.gridx = 7;
		c.gridy = 4;
		panel.add(proceed, c);

		frame.add(panel);

		frame.setSize(w1+w2, h);
		frame.setResizable(false);
		frame.setVisible(true);
	}

	private void changeFont(Component component, Font font) {
		component.setFont(font);
		if (component instanceof Container) {
			for (Component child : ((Container) component).getComponents()) {
				changeFont(child, font);
			}
		}
	}
		
	private void loadImage(int i) throws Exception {
		if (i > labelItems.size()-1 || i < 0) {
			JOptionPane.showMessageDialog(frame, "already the end", "warning", JOptionPane.WARNING_MESSAGE);
			return;
		}
		BufferedImage labelImage;
		if (labelItems.get(i).getLabelImage() != null) {
			labelImage = labelItems.get(i).getLabelImage();
		} else {
			BufferedImage labelImageOrig = LabelReader.readLabelImage(labelItems.get(i).getOldName().getAbsolutePath());
			labelImage = new BufferedImage(w1, h, 5); // 5 for jpg
			if (labelImageOrig != null) { 
				String label = tess.getLabel(labelItems.get(i).getOldName(), labelImageOrig);
				labelItems.get(i).setLabelText(label);
				labelImage.getGraphics().drawImage(labelImageOrig.getScaledInstance(w1, h, Image.SCALE_SMOOTH), 0, 0, null);
				labelItems.get(i).setLabelImage(labelImage);
			} else {
				labelItems.get(i).setLabelImage(labelImage);
				System.out.println(labelItems.get(i).getOldName().getAbsolutePath() + " cannot be opened");
			}
		}
		image.setIcon(new ImageIcon(labelImage));
		index = i;
	}
	
	private void renameLabel() {
		labelItems.get(index).setLabelText(labelText.getText());
		String dir = labelItems.get(index).getOldName().getParent();
		String basename = labelItems.get(index).getLabelText() + ".kfb";
		File newName = new File(dir + File.separatorChar + basename);
		labelItems.get(index).getOldName().renameTo(newName);
		System.out.println("renamed " + labelItems.get(index).getOldName().getAbsolutePath() + "\n"
						 + "     to " + newName.getAbsolutePath());
		labelItems.get(index).setOldName(newName);
	}
	
	private void showLabel() {
		wsi.setText(String.valueOf(index+1) + " / " + String.valueOf(labelItems.size()) + ":");
		wsiText.setText(labelItems.get(index).getOldName().getName());
		labelText.setText(labelItems.get(index).getLabelText());
	}
	
	private void updateGui(int step, boolean rename) {
		if (index == -1) {
			JOptionPane.showMessageDialog(frame, "there is no kfb file loaded", "error", JOptionPane.ERROR_MESSAGE);
			return;
		}
		if (rename) {
			renameLabel();
		}
		try {
			if (step == -1) {
				loadImage(index - 1);
			} else if (step == 0) {
				loadImage(index);
			} else if (step == 1) {
				loadImage(index + 1);
			}
		} catch (Exception e) {
			e.printStackTrace();
		}
		showLabel();
	}

	public static void main(String[] args) {
		new OcrGui();
	}
	
	private class LabelItem {
		private File oldName;
		private String labelText;
		private BufferedImage labelImage;
		LabelItem(File oldName, String labelText, BufferedImage labelImage) {
			this.setOldName(oldName);
			this.setLabelText(labelText);
			this.labelImage = labelImage;
		}
		public File getOldName() {
			return oldName;
		}
		public void setOldName(File oldName) {
			this.oldName = oldName;
		}
		public String getLabelText() {
			return labelText;
		}
		public void setLabelText(String labelText) {
			this.labelText = labelText;
		}
		public BufferedImage getLabelImage() {
			return labelImage;
		}
		public void setLabelImage(BufferedImage labelImage) {
			this.labelImage = labelImage;
		}
	}

	private class MyButton extends JButton implements ActionListener {
		public MyButton(String name) {
			super(name);
			addActionListener(this);
		}
		public void actionPerformed(ActionEvent e) {
			String s = e.getActionCommand();
			JFileChooser chooser;
			switch (s) {
				case "open file":
					chooser = new JFileChooser(System.getProperty("user.dir"));
					FileFilter fileFilter = new FileNameExtensionFilter("wsi files (*.kfb)", "kfb");
					chooser.setFileFilter(fileFilter);
					if (chooser.showOpenDialog(null) == JFileChooser.APPROVE_OPTION) {
						File file_name = chooser.getSelectedFile();
						index = 0;
						labelItems.clear();
						labelItems.add(new LabelItem(file_name, "", null));
						updateGui(0, false);
					} else {
						JOptionPane.showMessageDialog(frame, "no file choosed", "warning", JOptionPane.WARNING_MESSAGE);
					}
					break;
				case "open dir":
					chooser = new JFileChooser();
					chooser.setCurrentDirectory(new File(System.getProperty("user.dir")));
					chooser.setFileSelectionMode(JFileChooser.DIRECTORIES_ONLY);
					//chooser.setAcceptAllFileFilterUsed(false);
					if (chooser.showOpenDialog(null) == JFileChooser.APPROVE_OPTION) {
						index = -1;
						labelItems.clear();
						File dir = chooser.getSelectedFile();
						for (File file : dir.listFiles()) {
							if (file.getAbsolutePath().endsWith(".kfb")) {
								labelItems.add(new LabelItem(file, "", null));
							}
						}
						if (labelItems.isEmpty()) {
							JOptionPane.showMessageDialog(frame, "no kfb file exists", "warning", JOptionPane.WARNING_MESSAGE);
						} else {
							index = 0;
							updateGui(0, false);
						}
					} else {
						JOptionPane.showMessageDialog(frame, "no directory choosed", "warning", JOptionPane.WARNING_MESSAGE);
					}
					break;
				case "previous":
					updateGui(-1, false);
					break;
				case "next":
					updateGui(1, false);
					break;
				case "rename":
					updateGui(0, true);
					break;
				case "rename and next":
					updateGui(1, true);
					break;
			}
		}
	}
	
}