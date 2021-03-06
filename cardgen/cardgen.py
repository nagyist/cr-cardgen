#!/usr/bin/env python3

import os
import json
import sys
import yaml
from PIL import Image
from PIL import ImageCms

CONFIG = os.path.join("config.yaml")


def load_json(filename):
    """Load json by filename."""
    with open(filename, encoding='utf-8', mode='r') as f:
        data = json.load(f)
    return data


def generate_cards():
    """Generate Clash Royale cards."""
    with open(CONFIG) as f:
        config = yaml.load(f)


    # color managemenet
    color_profile = ImageCms.createProfile('sRGB')
    color_transform = ImageCms.buildTransformFromOpenProfiles

    # with open('./sRGB2014.icc') as f:
    #     sRGB_profile = f.read()



    # generate cards

    cards_data = load_json(config["cards_data"])

    src_path = config["src_dir"]
    spells_path = config["spells_dir"]
    output_png24_dir = config["output_png24_dir"]
    output_png8_dir = config["output_png8_dir"]

    filenames = dict((v, k) for k, v in config["cards"].items())

    card_frame = Image.open(os.path.join(src_path, "frame-card.png"))
    leggie_frame = Image.open(os.path.join(src_path, "frame-legendary.png"))
    card_mask = Image.open(
        os.path.join(src_path, "mask-card.png")).convert("RGBA")
    leggie_mask = Image.open(
        os.path.join(src_path, "mask-legendary.png")).convert("RGBA")
    commons_bg = Image.open(os.path.join(src_path, "bg-commons.png"))
    rare_bg = Image.open(os.path.join(src_path, "bg-rare.png"))
    epic_bg = Image.open(os.path.join(src_path, "bg-epic.png"))
    leggie_bg = Image.open(os.path.join(src_path, "bg-legendary.png"))

    size = card_frame.size

    for card_data in cards_data:
        name = card_data['key']
        rarity = card_data['rarity']
        card_src = os.path.join(spells_path, "{}.png".format(filenames[name]))
        card_dst_png24 = os.path.join(output_png24_dir, "{}.png".format(name))
        card_dst_png8 = os.path.join(output_png8_dir, "{}.png".format(name))
        card_image = Image.open(card_src)

        # scale card to fit frame
        scale = 1
        card_image = card_image.resize(
            [int(dim * scale) for dim in card_image.size])

        # pad card with transparent pixels to be same size as output
        card_size = card_image.size
        card_x = int((size[0] - card_size[0]) / 2)
        card_y = int((size[1] - card_size[1]) / 2)
        card_x1 = card_x + card_size[0]
        card_y1 = card_y + card_size[1]

        im = Image.new("RGBA", size)
        im.paste(
            card_image, (card_x, card_y, card_x1, card_y1))
        card_image = im

        im = Image.new("RGBA", size)

        if rarity == "Legendary":
            im.paste(card_image, mask=leggie_mask)
        else:
            im.paste(card_image, mask=card_mask)

        card_image = im

        im = Image.new("RGBA", size)
        im = Image.alpha_composite(im, card_image)

        # use background image for regular cards
        bg = None
        if rarity == "Commons":
            bg = commons_bg
        elif rarity == "Rare":
            bg = rare_bg
        elif rarity == "Epic":
            bg = epic_bg
        elif rarity == "Legendary":
            bg = leggie_bg
        else:
            bg = Image.new("RGBA", size)

        # add frame
        im = Image.alpha_composite(bg, im)
        if rarity == "Legendary":
            im = Image.alpha_composite(im, leggie_frame)
        else:
            im = Image.alpha_composite(im, card_frame)

        # save and output path to std out

        converted_im = ImageCms.profileToProfile(im, './AdobeRGB1998.icc', 'sRGB.icc')
        converted_im.save(card_dst_png24)
        print(card_dst_png24)

        # # Save optimized PNG (PNG-8)
        #
        # # Optimize PNG
        # alpha = converted_im.split()[-1]
        # opt_im = converted_im.convert('RGB').convert('P', palette=Image.ADAPTIVE, colors=255)
        #
        # # Set all pixel values below 128 to 255,
        # # and the rest to 0
        # mask = Image.eval(alpha, lambda a: 255 if a <= 128 else 0)
        #
        # # Paste the color of index 255 and use alpha as a mask
        # opt_im.paste(255, mask)
        #
        # opt_im.save(card_dst_png8, transparency=255)
        # print(card_dst_png8)




def main(arguments):
    """Main."""
    generate_cards()


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))