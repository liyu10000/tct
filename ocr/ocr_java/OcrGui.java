import java.awt.Font;
import java.awt.Color;
import java.awt.GridBagLayout;
import java.awt.GridBagConstraints;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.KeyEvent;
import java.awt.image.BufferedImage;
import java.awt.Image;
import java.awt.Insets;
import java.io.File;
import javax.imageio.ImageIO;
import javax.swing.JFrame;
import javax.swing.JPanel;
import javax.swing.JButton;
import javax.swing.JLabel;
import javax.swing.JTextField;
import javax.swing.JFileChooser;
import javax.swing.JOptionPane;
import javax.swing.ImageIcon;

public class OcrGui {
	static JFrame frame;
	static JLabel image;
	static JLabel wsi;
	static JLabel wsiText;
	static JTextField labelText;

	public OcrGui() {
		frame = new JFrame("OCR");
		frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);

		JPanel panel = new JPanel();
		panel.setLayout(new GridBagLayout());
		GridBagConstraints c = new GridBagConstraints();

		// set layout for label image
		image = new JLabel(new ImageIcon(loadImage("")));
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

		frame.setSize(1000, 512);
		frame.setResizable(false);
		frame.setVisible(true);
	}

	private BufferedImage loadImage(String src) {
		int width = 512, height = 512;
		BufferedImage jpg_new = new BufferedImage(width, height, 5); // 5 for jpg
		if (src.equals("")) {
			return jpg_new;
		}
		try {
			BufferedImage jpg = ImageIO.read(new File(src));
			jpg_new.getGraphics().drawImage(jpg.getScaledInstance(width, height, Image.SCALE_SMOOTH),
											0, 0, null);
		} catch (Exception e) {
			e.printStackTrace();
		}
		return jpg_new;
	}


	public static void main(String[] args) {
		new OcrGui();
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
					chooser = new JFileChooser(System.getProperty("java.class.path"));
					if (chooser.showOpenDialog(null) == JFileChooser.APPROVE_OPTION) {
						String file_name = chooser.getSelectedFile().getAbsolutePath();
						image.setIcon(new ImageIcon(loadImage(file_name)));
					} else {
						System.out.println("open operation cancelled");
					}
					break;
				case "open dir":
					break;
				case "previous":
					break;
				case "next":
					break;
				case "rename":
					break;
				case "rename and next":
					break;
			}
		}
	}
}