#! /usr/bin/env python

import argparse
import json

from PIL import Image, ImageDraw, ImageFont


def main():
    # Read arguments
    parser = argparse.ArgumentParser(description='/r/place Image converter')
    parser.add_argument('input_file', help='Input image file')
    parser.add_argument('output_file', help='Output image file')
    parser.add_argument('--annotate', action='store_true',
                        help='Generate annotations for pixel positions')
    parser.add_argument('--colour_file', type=str, default='colours.json',
                        help='JSON file of possible colours')
    parser.add_argument('--dimensions', type=str, default='orig',
                        help='Dimensions of the output image (e.g. 20x20)')
    parser.add_argument('--dither', action='store_true',
                        help='Enable dithering of output image')
    parser.add_argument('--font', type=str,
                        default='/usr/share/fonts/TTF/DejaVuSansMono.ttf',
                        help='Font for annotations')
    parser.add_argument('--font_size', type=int, default=10,
                        help='Font size for annotations')
    parser.add_argument('--output_scale', type=int, default=1,
                        help='Scale output image after dimension')
    parser.add_argument('--top_left', type=str, default='0x0',
                        help='Offset for annotations')
    args = parser.parse_args()

    # Load possible colours
    colours = None
    with open(args.colour_file, 'r') as colours_file:
        colours_list = [i for k in json.load(colours_file) for i in k]
        colours = Image.new('P', (len(colours_list) // 3, 0))
        colours.putpalette(colours_list)

    # Load image
    with Image.open(args.input_file) as img:
        # Scale image to new size
        if args.dimensions != 'orig':
            dims = [int(i) for i in args.dimensions.split('x')]
            img = img.resize(dims, 0)

        # Quantize to colour palette
        img = img.convert('RGB')
        new_img = img.convert(mode='P', palette=colours, dither=args.dither)

        new_dims = [i * args.output_scale for i in new_img.size]
        new_img = new_img.resize(new_dims, 0)

        # Add location annotations (this part was written while very drunk)
        if args.annotate:
            x, y = [int(i) for i in args.top_left.split('x')]
            fnt = ImageFont.truetype(args.font, args.font_size)
            text_img = Image.new('RGBA', new_img.size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(text_img)
            for i in range(0, new_dims[0], args.annotate):
                for j in range(0, new_dims[1], args.annotate):
                    draw.text((i*args.output_scale, j*args.output_scale),
                              '({}, {})'.format(i + x, j + y),
                              font=fnt,
                              fill=(0, 0, 0, 255))
            new_img = new_img.convert('RGBA')
            new_img = Image.alpha_composite(new_img, text_img)

        # Save output
        new_img.save(args.output_file)


if __name__ == '__main__':
    main()
