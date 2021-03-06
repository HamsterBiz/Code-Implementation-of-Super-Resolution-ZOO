import numpy as np
import math
from . import rgb2ycbcr


def psnr(HR_G, HR_GroundTruth, only_Luminance=True, crop=0):
    """
    :param HR_G: [h,w,c] for image and [b,h,w,c] for video,  ndarray
    :param HR_GroundTruth:
    :param only_Luminance: Whether to use only Luminance channel.
        use rgb2ycbcr function.  same as matlab rgb2ycbcr.
    :param crop: For SR by factor s, we crop s pixels near image boundary before evaluation
    :return: psnr value (frame average for video)
    """
    assert HR_GroundTruth.shape == HR_G.shape
    assert isinstance(HR_G, np.ndarray) and isinstance(HR_GroundTruth, np.ndarray)
    assert HR_GroundTruth.dtype == HR_G.dtype
    assert HR_G.dtype == np.uint8

    video_flag = False
    if len(HR_G.shape) == 4:
        video_flag = True

    # crop
    h, w = HR_G.shape[-3], HR_G.shape[-2]
    assert h > 2*crop and w > 2*crop, 'crop boundary size too large'
    HR_G = HR_G[..., crop:h-crop, crop:w-crop, :]
    HR_GroundTruth = HR_GroundTruth[..., crop:h-crop, crop:w-crop, :]

    HR_G = HR_G.astype(np.float32)
    HR_GroundTruth = HR_GroundTruth.astype(np.float32)

    # if true, [h,w,c] -> [h,w]  or  [b,h,w,c] -> [b,h,w]
    if only_Luminance:
        HR_G = rgb2ycbcr(HR_G)
        HR_GroundTruth = rgb2ycbcr(HR_GroundTruth)

    def one_frame(f1, f2, fakeval=100):
        mse = np.mean((f1 - f2) ** 2)
        if mse < 1.0e-10:
            return fakeval
        return 10 * math.log10(255.0 ** 2 / mse)

    if video_flag:
        # for [b,h,w,c] or [b,h,w]
        frame_result_list = []
        for i in range(HR_G.shape[0]):
            frame_result_list.append(one_frame(HR_G[i], HR_GroundTruth[i]))
        return sum(frame_result_list)/len(frame_result_list)

    else:
        # for [h,w] or [h,w,c]
        return one_frame(HR_G, HR_GroundTruth)
