import cv2
import numpy as np

# 0 - blue
# 1 - green
# 2 - red

RED_COEF = 77 / 256
GREEN_COEF = 150 / 256
BLUE_COEF = 29 / 256

RED_BIT_PLACE_NUMBER = 2
BLUE_BIT_PLACE_NUMBER = 3

DELTA = 4 + 4 * 17 % 3


def get_bit_place(channel, place_num):
    return channel & (2 ** (place_num - 1))


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
    # if clear_bit_place == 251: 251 = 11111011, зануляем 3-ю битовую плоскость
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


def svi4_encode(original_image, watermark, color_channel, delta):
    height, width, channels = original_image.shape
    noise = np.empty((height, width), dtype="uint8")
    noise = (np.round(np.random.uniform(0.0, delta - 1, (height, width)))).astype("uint8")

    cv2.imshow("Noise", noise)

    extracted_channel = get_channel(original_image, color_channel)
    binary_watermark = get_channel(watermark, color_channel)
    changed_channel = (extracted_channel // (2 * delta) * (2 * delta)) + binary_watermark * delta + noise

    r = get_channel(original_image, 'red')
    g = get_channel(original_image, 'green')
    b = get_channel(original_image, 'blue')

    if color_channel == 'blue':
        return noise, cv2.merge([changed_channel, g, r])
    if color_channel == 'red':
        return noise, cv2.merge([b, g, changed_channel])
    if color_channel == 'green':
        return noise, cv2.merge([b, changed_channel, r])


def svi4_decode(encode_image, original_image, noise, color_channel, delta):
    encoded_image_channel = get_channel(encode_image, color_channel)
    original_image_channel = get_channel(original_image, color_channel)
    return (encoded_image_channel - noise - (original_image_channel // (2 * delta) * 2 * delta)) / delta
    
    
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
    if RED_BIT_PLACE_NUMBER * RED_COEF > BLUE_BIT_PLACE_NUMBER * BLUE_COEF:
        svi1_result = svi1_encode(baboon, watermark_image, 'blue', BLUE_BIT_PLACE_NUMBER, 'red', RED_BIT_PLACE_NUMBER)
    else:
        svi1_result = svi1_encode(baboon, watermark_image, 'blue', BLUE_BIT_PLACE_NUMBER, 'red', RED_BIT_PLACE_NUMBER)
    svi1_decode_result = None
    if RED_BIT_PLACE_NUMBER * RED_COEF > BLUE_BIT_PLACE_NUMBER * BLUE_COEF:
        svi1_decode_result = svi1_decode(svi1_result, BLUE_BIT_PLACE_NUMBER, RED_BIT_PLACE_NUMBER, 'blue', 'red')
    else:
        svi1_decode_result = svi1_decode(svi1_result, RED_BIT_PLACE_NUMBER, BLUE_BIT_PLACE_NUMBER, 'red', 'blue')
    cv2.imshow("Source Image", baboon)
    cv2.imshow("SVI-1 Encoded", svi1_result)
    cv2.imshow("SVI-1 Decoded", svi1_decode_result)

    cv2.waitKey(0)

    # СВИ-4
    result_noise, svi4_encode_result = svi4_encode(baboon, watermark_image, 'green', DELTA)
    svi4_decode_result = svi4_decode(svi4_encode_result, baboon, result_noise, 'green', DELTA)

    cv2.imshow("Source Image", baboon)
    cv2.imshow("SVI-4 Encoded", svi4_encode_result)
    cv2.imshow("SVI-4 Decoded", svi4_decode_result)

    cv2.waitKey(0)
