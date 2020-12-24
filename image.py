from PIL import Image
import os

for file in os.listdir('./demo_src'):
	img = Image.open('./demo_src/'+file)
	img.thumbnail((800,450))
	img.save("./demoimg/"+file)