from util.util_dataset import *


# video_dataset_onlyHR2AB("./datasets/youku/B", "./datasets/youku/train")

# video_dataset_HRLR2AB(HRpath="./datasets/youku/B", LRpath="./datasets/youku/A", ABpath="./datasets/youku/train")

# vimeo90K_dataset_onlyHR2AB(dataset_path="/opt/data/private/datasets/vimeo_septuplet/vimeo_septuplet",
#                            ABpath="/opt/data/private/datasets/vimeo_septuplet",
#                            phase="train",
#                            factor=4)

# for path in os.listdir("./A/"):
#     allpath = os.path.join("./A/", path)
#     assert os.path.isdir(allpath)
#     if len(os.listdir(allpath)) != 7:
#         print(allpath)

# from DCN import *

# SPMCS_dataset_HRLR2AB()

# SPMCS_dataset_HRLR2AB(dataset_path="/opt/data/private/datasets/SPMCS/test_set",
#                       ABpath="/opt/data/private/datasets/SPMCS")

# SPMCS_dataset_onlyHR2AB(dataset_path="/opt/data/private/datasets/SPMCS/test_set",
#                         ABpath="/opt/data/private/datasets/SPMCS")


#!/usr/bin/env python

# import VSR

video_dataset_onlyHR2AB("./datasets/demo/HR", "./datasets/demo", phase="test")

video_dataset_onlyHR2AB("/opt/data/private/datasets/demo/HR", "/opt/data/private/datasets/demo", phase="test")

from util.compare import compare


# compare(dataroot="C:/Users/76397/Desktop/compare/different_size1", x=85, y=105)
# compare(dataroot="C:/Users/76397/Desktop/compare/different_size2", x=15, y=85)
# compare(dataroot="C:/Users/76397/Desktop/compare/different_size3", x=35, y=45)
# compare(dataroot="C:/Users/76397/Desktop/compare/different_method_vid4_1", x=42, y=47)
# compare(dataroot="C:/Users/76397/Desktop/compare/different_method_vid4_2", x=63, y=19)
# compare(dataroot="C:/Users/76397/Desktop/compare/different_method_vid4_3", x=94, y=60)
# compare(dataroot="C:/Users/76397/Desktop/compare/different_method_spmc_1", x=110, y=70)
# compare(dataroot="C:/Users/76397/Desktop/compare/different_method_spmc_2", x=110, y=25)
# compare(dataroot="C:/Users/76397/Desktop/compare/different_method_spmc_3", x=135, y=5)