import cv2
import numpy as np

# 0 - blue
# 1 - green
# 2 - red

red_coef = 77 / 256
green_coef = 150 / 256
blue_coef = 29 / 256

red_bit_place_number = 2
blue_bit_place_number = 3


def get_bit_place(image, place_num):
    return image & (2 ** (place_num - 1))


def svi1_decode(encode_image, first_bit_place_number, second_bit_place_number
                , first_color_channel_string, second_color_channel_string):
    second_channel = get_channel(baboon, second_color_channel_string)
    second_bit_place = get_bit_place(second_channel, second_bit_place_number)

    first_channel = get_channel(encode_image, first_color_channel_string)
    first_bit_place = get_bit_place(first_channel, first_bit_place_number)

    return first_bit_place ^ second_bit_place


def svi1_encode(original_image, water_mark_image, color_channel_string, bit_plate_number,
                second_channel_string, second_bit_plate_number):

    clear_bit_place = 255 - (2 ** (bit_plate_number - 1))

    prepared_watermark_colored = ((water_mark_image / 255) * (2 ** (bit_plate_number - 1))).astype(np.uint8)
    binary_watermark = get_channel(prepared_watermark_colored, color_channel_string)
    channel_with_empty_bit_place = get_channel(original_image, color_channel_string) & clear_bit_place
    channel_with_watermark = channel_with_empty_bit_place | binary_watermark

    second_channel = get_channel(baboon, second_channel_string)
    second_bit_place = get_bit_place(second_channel, second_bit_plate_number)
    channel_result = channel_with_watermark ^ second_bit_place

    r = get_channel(baboon, 'red')
    g = get_channel(baboon, 'green')
    b = get_channel(baboon, 'blue')

    if color_channel_string == 'blue':
        return cv2.merge([channel_result, g, r])
    if color_channel_string == 'red':
        return cv2.merge([b, g, channel_result])
    if color_channel_string == 'green':
        return cv2.merge([b, channel_result, r])
    
    
def get_channel(image, channel):
    b, g, r = cv2.split(image)
    if channel == 'blue':
        return b
    if channel == 'green':
        return g
    if channel == 'red':
        return r


if __name__ == '__main__':
    baboon = cv2.imread('baboon.tif')
    watermark_image = cv2.imread('ornament.tif')
    svi1_result = None
    if red_bit_place_number * red_coef > blue_bit_place_number * blue_coef:
        svi1_result = svi1_encode(baboon, watermark_image, 'blue', blue_bit_place_number, 'red', red_bit_place_number)
    else:
        svi1_result = svi1_encode(baboon, watermark_image, 'blue', blue_bit_place_number, 'red', red_bit_place_number)
    svi1_decode_result = None
    if red_bit_place_number * red_coef > blue_bit_place_number * blue_coef:
        svi1_decode_result = svi1_decode(svi1_result, blue_bit_place_number, red_bit_place_number, 'blue', 'red')
    else:
        svi1_decode_result = svi1_decode(svi1_result, red_bit_place_number, blue_bit_place_number, 'red', 'blue')
    cv2.imshow("Source Image", baboon)
    cv2.imshow("SVI-1 Encoded", svi1_result)
    cv2.imshow("SVI-1 Decoded", svi1_decode_result)

    cv2.waitKey(0)
