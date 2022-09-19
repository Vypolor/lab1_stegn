import cv2
import numpy as np

# 0 - blue
# 1 - green
# 2 - red

RED_COEF = 77 / 256
GREEN_COEF = 150 / 256
BLUE_COEF = 29 / 256

RED = 'red'
GREEN = 'green'
BLUE = 'blue'

RED_BIT_PLACE_NUMBER = 2
BLUE_BIT_PLACE_NUMBER = 3

DELTA = 4 + 4 * 17 % 3


def get_bit_place(channel, place_num):
    return channel & (2 ** (place_num - 1))


def get_channel(image, channel):
    b, g, r = cv2.split(image)
    if channel == BLUE:
        return b
    if channel == GREEN:
        return g
    if channel == RED:
        return r


def merge_channels(channel, color_channel_string):
    r = get_channel(baboon, RED)
    g = get_channel(baboon, GREEN)
    b = get_channel(baboon, BLUE)

    if color_channel_string == BLUE:
        return cv2.merge([channel, g, r])
    if color_channel_string == RED:
        return cv2.merge([b, g, channel])
    if color_channel_string == GREEN:
        return cv2.merge([b, channel, r])


def svi1_encode(original_image, water_mark_image, color_channel_string, bit_plate_number,
                second_channel_string, second_bit_plate_number):

    clear_bit_place = 255 - (2 ** (bit_plate_number - 1))
    prepared_watermark_colored = ((water_mark_image / 255) * (2 ** (bit_plate_number - 1))).astype(np.uint8)
    binary_watermark = get_channel(prepared_watermark_colored, color_channel_string)
    # if clear_bit_place == 251: 251 = 11111011, зануляем 3-ю битовую плоскость
    channel_with_empty_bit_place = get_channel(original_image, color_channel_string) & clear_bit_place
    channel_with_watermark = channel_with_empty_bit_place | binary_watermark

    second_channel = get_channel(baboon, second_channel_string)
    second_bit_place = get_bit_place(second_channel, second_bit_plate_number)
    channel_result = channel_with_watermark ^ second_bit_place

    return merge_channels(channel_result, color_channel_string)


def svi1_decode(encode_image, first_bit_place_number, second_bit_place_number
                , first_color_channel_string, second_color_channel_string):
    second_channel = get_channel(baboon, second_color_channel_string)
    second_bit_place = get_bit_place(second_channel, second_bit_place_number)

    first_channel = get_channel(encode_image, first_color_channel_string)
    first_bit_place = get_bit_place(first_channel, first_bit_place_number)

    return first_bit_place ^ second_bit_place


def svi4_encode(original_image, watermark, color_channel_string, delta):
    height, width, channels = original_image.shape
    rounded_white_noise = (np.round(np.random.uniform(0.0, delta - 1, (height, width)))).astype("uint8")

    cv2.imshow("Noise", rounded_white_noise)

    extracted_channel = get_channel(original_image, color_channel_string)
    binary_watermark = get_channel(watermark, color_channel_string)
    changed_channel = (extracted_channel // (2 * delta) * (2 * delta)) + binary_watermark * delta + rounded_white_noise

    return rounded_white_noise, merge_channels(changed_channel, color_channel_string)


def svi4_decode(encode_image, original_image, noise, color_channel, delta):
    encoded_image_channel = get_channel(encode_image, color_channel)
    original_image_channel = get_channel(original_image, color_channel)
    return (encoded_image_channel - noise - (original_image_channel // (2 * delta) * 2 * delta)) / delta


if __name__ == '__main__':
    baboon = cv2.imread('baboon.tif')
    watermark_image = cv2.imread('ornament.tif')
    svi1_result = None
    svi1_decode_result = None
    if RED_BIT_PLACE_NUMBER * RED_COEF > BLUE_BIT_PLACE_NUMBER * BLUE_COEF:
        svi1_result = svi1_encode(baboon, watermark_image, BLUE, BLUE_BIT_PLACE_NUMBER, RED, RED_BIT_PLACE_NUMBER)
        svi1_decode_result = svi1_decode(svi1_result, BLUE_BIT_PLACE_NUMBER, RED_BIT_PLACE_NUMBER, BLUE, RED)
    else:
        svi1_result = svi1_encode(baboon, watermark_image, BLUE, BLUE_BIT_PLACE_NUMBER, RED, RED_BIT_PLACE_NUMBER)
        svi1_decode_result = svi1_decode(svi1_result, RED_BIT_PLACE_NUMBER, BLUE_BIT_PLACE_NUMBER, RED, BLUE)
    cv2.imshow("Source Image", baboon)
    cv2.imshow("SVI-1 Encoded", svi1_result)
    cv2.imshow("SVI-1 Decoded", svi1_decode_result)

    cv2.waitKey(0)

    # СВИ-4
    result_noise, svi4_encode_result = svi4_encode(baboon, watermark_image, RED, DELTA)
    svi4_decode_result = svi4_decode(svi4_encode_result, baboon, result_noise, RED, DELTA)

    cv2.imshow("Source Image", baboon)
    cv2.imshow("SVI-4 Encoded", svi4_encode_result)
    cv2.imshow("SVI-4 Decoded", svi4_decode_result)

    cv2.waitKey(0)
