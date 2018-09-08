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

public class OCRGui {
	static JFrame frame;
	static JLabel image;
	static JTextField prefixText;
	static JTextField numberText;
	static JButton next;

	public OCRGui() {
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

		// set layout for prefix
		JLabel prefix = new JLabel("prefix:");
		c.fill = GridBagConstraints.NONE;
		c.anchor = GridBagConstraints.LINE_END;
		c.insets = new Insets(15,0,15,20);
		//c.weightx = 0.5;
		c.gridwidth = 1;
		c.gridheight = 1;
		c.gridx = 6;
		c.gridy = 1;
		panel.add(prefix, c);

		// set layout for prefix input area
		prefixText = new JTextField();
		prefixText.setText("wsi prefix");
		c.fill = GridBagConstraints.HORIZONTAL;
		c.anchor = GridBagConstraints.CENTER;
		c.insets = new Insets(15,0,15,0);
		c.weightx = 0.5;
		c.gridwidth = 2;
		c.gridheight = 1;
		c.gridx = 7;
		c.gridy = 1;
		panel.add(prefixText, c);

		// set layout for number
		JLabel number = new JLabel("number:");
		c.fill = GridBagConstraints.NONE;
		c.anchor = GridBagConstraints.LINE_END;
		c.insets = new Insets(15,0,15,20);
		//c.weightx = 0.5;
		c.gridwidth = 1;
		c.gridheight = 1;
		c.gridx = 6;
		c.gridy = 2;
		panel.add(number, c);

		// set layout for number area
		numberText = new JTextField();
		numberText.setText("wsi number");
		c.fill = GridBagConstraints.HORIZONTAL;
		c.anchor = GridBagConstraints.CENTER;
		c.insets = new Insets(15,0,15,0);
		c.weightx = 0.5;
		c.gridwidth = 2;
		c.gridheight = 1;
		c.gridx = 7;
		c.gridy = 2;
		panel.add(numberText, c);

		// set layout for next button
		next = new JButton("next");
		c.fill = GridBagConstraints.HORIZONTAL;
		c.anchor = GridBagConstraints.CENTER;
		c.insets = new Insets(15,0,15,0);
		c.weightx = 0.5;
		c.gridwidth = 2;
		c.gridheight = 1;
		c.gridx = 7;
		c.gridy = 3;
		panel.add(next, c);

		frame.add(panel);

		frame.setSize(1000, 600);
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
		new OCRGui();
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
			}
		}
	}
}