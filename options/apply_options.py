from .base_options import BaseOptions


class ApplyOptions(BaseOptions):
    """This class includes apply options.

    It also includes shared options defined in BaseOptions.
    """

    def initialize(self, parser):
        parser = BaseOptions.initialize(self, parser)  # define shared options
        parser.add_argument('--phase', type=str, default='apply', help='train, val, test, etc')
        parser.add_argument('--results_dir', type=str, default='./results/', help='saves results here.')
        parser.add_argument('--block_size', type=int, default='160', help='for save memory, we make blocks by 120*120, set lower for poor performance machine!')

        # Dropout and Batchnorm has different behavioir during training and test.
        parser.add_argument('--eval', type=bool, default=False, help='use eval mode during test time.')
        parser.add_argument('--num_test', type=int, default=10000, help='how many test images(divided blocks) to run (upper_bound)')

        return parser