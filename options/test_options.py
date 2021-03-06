from .base_options import BaseOptions
from . import str2bool

class TestOptions(BaseOptions):
    """This class includes test options.

    It also includes shared options defined in BaseOptions.
    """

    def initialize(self, parser):
        parser = BaseOptions.initialize(self, parser)  # define shared options
        parser.add_argument('--phase', type=str, default='test', help='train, val, test, etc')
        parser.add_argument('--results_dir', type=str, default='./results/', help='saves results here.')
        # Dropout and Batchnorm has different behavioir during training and test.
        parser.add_argument('--eval', type=str2bool, default=True, help='use eval mode during test time.')
        parser.add_argument('--num_test', type=int, default=1000000, help='how many test images to run')
        # Image Quality Assessment
        parser.add_argument('--iqa_list', type=str, default='psnr,ssim', help='do the method in the iqa_list')
        parser.add_argument('--ensemble', type=str2bool, default=True, help='whether to use ensemble strategy')

        # video
        parser.add_argument('--imgseqlen', type=int, default=0, help='how long sub-string of video frames to test, default 0 means all of them, normally not change')
        parser.add_argument('--save_flag', type=str2bool, default=False, help='whether to save the result, used for video')
        return parser
