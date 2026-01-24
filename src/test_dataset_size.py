import os

image_dir = "../dataset/images"

images = os.listdir("../dataset/images")
masks = os.listdir("../dataset/masks")

images_count = 0
masks_count = 0

for image in images:
    images_count = images_count + 1

for mask in masks:
    masks_count = masks_count + 1

for i in range(len(images)):
    if images[i] != masks[i]:
        print(os.path.join(image_dir, images[i]))
        images.remove(images[i])
        os.remove(os.path.join(image_dir, images[i]))
        break


print(f"images count: ", images_count)
print(f"masks_count: ", masks_count)