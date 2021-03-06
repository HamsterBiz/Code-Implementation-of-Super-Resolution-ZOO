"""
apply:
    python apply.py --dataroot  ./datasets/demo/test/A --name vimeo_tanet4_04_21_17_00 --model tanet4 --load_epoch epoch_85

    python3 apply.py --dataroot  /opt/data/private/datasets/demo/test/A --name vimeo_tanet4_04_21_17_00 --model tanet4 --load_epoch epoch_85

    dataset_images2video(datasetpath = "./results/vimeo_tanet4_04_21_17_00/apply-A-epoch_85-block_size_250", fps=25)

python train.py --dataroot ./datasets/Vid4 --name Vid4_tanet4 --model tanet4 --display_freq  40  --print_freq  4 --imgseqlen 7  --num_threads 2

aimax:
    gpu:
    python3 train.py
        --dataroot          /opt/data/private/datasets/vimeo_septuplet
        --name              vimeo_tanet4
        --model             tanet4
        --display_freq      4800
        --print_freq        4800
        --save_epoch_freq   5
        --gpu_ids           0,1,2,3
        --batch_size        4
        --suffix            04_21_17_00
        --crop_size         64
        --imgseqlen         7
        --seed              3
        --continue_train    True
        --load_epoch        epoch_55
        --epoch_count       56


        v5:
        --dataroot          /opt/data/private/datasets/vimeo_septuplet
        --name              vimeo_tanet5
        --model             tanet4
        --display_freq      4800
        --print_freq        4800
        --save_epoch_freq   5
        --batch_size        5
        --suffix            04_21_21_30
        --crop_size         64
        --imgseqlen         7
        --seed              2
        --cl                32
        --cm                32
        --ch                16
        --continue_train    True
        --load_epoch        epoch_75
        --epoch_count       76

        v6:
        --dataroot          /opt/data/private/datasets/vimeo_septuplet
        --name              vimeo_tanet6
        --model             tanet4
        --display_freq      5400
        --print_freq        5400
        --save_epoch_freq   5
        --gpu_ids           0,1,2
        --batch_size        18
        --suffix            05_03_11_40
        --crop_size         64
        --imgseqlen         5
        --seed              1
        --cl                32
        --cm                32
        --ch                16
        --nframes           5
        --lr                0.0002


        v7:
        --dataroot          /opt/data/private/datasets/vimeo_septuplet
        --name              vimeo_tanet7
        --model             tanet4
        --display_freq      4800
        --print_freq        4800
        --save_epoch_freq   5
        --gpu_ids           0,1
        --batch_size        20
        --suffix            05_04_16_15
        --crop_size         64
        --imgseqlen         3
        --seed              1
        --cl                32
        --cm                32
        --ch                16
        --nframes           3
        --lr                0.0002

        v8:
        --dataroot          /opt/data/private/datasets/vimeo_septuplet
        --name              vimeo_tanet8
        --model             tanet4
        --display_freq      4800
        --print_freq        4800
        --save_epoch_freq   5
        --batch_size        16
        --suffix            05_03_11_40
        --crop_size         64
        --imgseqlen         1
        --seed              1
        --cl                32
        --cm                32
        --ch                16
        --nframes           1
        --lr                0.0002
"""
import torch
from .base_model import BaseModel
from . import tanet4_networks
from util import remove_pad_for_tensor


class TANET4Model(BaseModel):
    """ This class implements the tanet4 model

    The model training requires '--dataset_mode aligned_video' dataset.

    Here we do not use optical flow.

    vimeo90K train dataset size: 55025.
    """
    @staticmethod
    def modify_commandline_options(parser, is_train=True):
        """Add new dataset-specific options, and rewrite default values for existing options.

        Parameters:
            parser          -- original option parser
            is_train (bool) -- whether training phase or test phase. You can use this flag to add training-specific or test-specific options.

        Returns:
            the modified parser.

        """
        parser.set_defaults(dataset_mode='aligned_video')
        parser.set_defaults(batch_size=1)  # 8 in paper  need 4 gpu
        parser.set_defaults(preprocess='crop')
        parser.set_defaults(SR_factor=4)
        parser.set_defaults(crop_size=64)  # 64
        parser.set_defaults(beta1='0.9')
        parser.set_defaults(lr=0.0001)
        parser.set_defaults(init_type='kaiming')
        parser.set_defaults(lr_policy='step')
        parser.set_defaults(lr_decay_iters=20)
        parser.set_defaults(lr_gamma=0.65)
        parser.set_defaults(n_epochs=150)
        parser.set_defaults(multi_base=8)
        parser.add_argument('--cl', type=int, default=128, help='the cl in paper')
        parser.add_argument('--cm', type=int, default=128, help='the cm in paper')
        parser.add_argument('--ch', type=int, default=64, help='the ch in paper')
        parser.add_argument('--nframes', type=int, default=7, help='frames used by model')  # used for assert, imgseqlen should set equal to this when train

        return parser

    def __init__(self, opt):
        """Initialize the RBPN class.

        Parameters:
            opt (Option class)-- stores all the experiment flags; needs to be a subclass of BaseOptions
        """
        BaseModel.__init__(self, opt)
        self.SR_factor = opt.SR_factor

        # specify the training losses you want to print out. The training/test scripts will call <BaseModel.get_current_losses>
        self.loss_names = ['SR']

        # specify the images you want to save/display. The training/test scripts will call <BaseModel.get_current_visuals>
        if self.opt.phase == "apply":
            self.visual_names = ['LR', 'HR_Bicubic', 'HR_G']
        else:
            self.visual_names = ['LR', 'HR_GroundTruth', 'HR_G', 'HR_Bicubic']

        # specify the models you want to save to the disk. The training/test scripts will call <BaseModel.save_networks> and <BaseModel.load_networks>
        if self.isTrain:
            self.model_names = ['G']
        else:
            self.model_names = ['G']

        self.netG = tanet4_networks.define_G(opt)

        if self.isTrain:
            self.criterionL1 = torch.nn.L1Loss()
            self.optimizer_G = torch.optim.Adam(self.netG.parameters(), lr=opt.lr, betas=(opt.beta1, 0.999))
            self.optimizers.append(self.optimizer_G)

    def set_input(self, input):
        """Unpack input data from the dataloader and perform necessary pre-processing steps.

        Parameters:
            input (dict): include the data itself and its metadata information.
        """
        self.A_paths = input['A_paths']

        # input['A']:   e.g. [4, 10, 3, 64, 64] for recurrent training
        # input['B']:   e.g. [4, 10, 3, 256, 256]
        self.LR = input['A'].to(self.device, non_blocking=True)
        assert self.LR.shape[1] == self.opt.nframes, "input image length {} should equal to opt.nframes {}".format(self.LR.shape[1], self.opt.nframes)
        mid = self.opt.nframes // 2

        if self.opt.phase in ('train', 'test'):
            self.B_paths = input['B_paths']
            self.HR_GroundTruth = input['B'][:, mid, ...].to(self.device, non_blocking=True)

        if self.opt.phase == "apply":
            self.HR_GT_h, self.HR_GT_w = input['gt_h_w']

    def forward(self):
        """Run forward pass; called by both functions <optimize_parameters> and <test>.
        """
        self.HR_G = self.netG(self.LR)

    def compute_visuals(self):
        mid = self.opt.nframes//2
        self.LR = self.LR[:, mid, ...]
        if self.opt.phase in ("test", "apply"):
            # remove pad for LR
            if self.opt.phase == "test":
                h, w = self.HR_GroundTruth.shape[-2], self.HR_GroundTruth.shape[-1]
            else:
                h, w = self.HR_GT_h, self.HR_GT_w
            self.LR = remove_pad_for_tensor(tensor=self.LR,
                                            HR_GT_h_w=(h, w),
                                            factor=self.SR_factor, LR_flag=True)
            # remove pad for HR_G
            self.HR_G = remove_pad_for_tensor(tensor=self.HR_G,
                                              HR_GT_h_w=(h, w),
                                              factor=self.SR_factor, LR_flag=False)

        self.HR_Bicubic = torch.nn.functional.interpolate(self.LR, scale_factor=self.SR_factor, mode='bicubic', align_corners=False)

    def backward(self):
        """Calculate loss"""
        mid = self.opt.nframes//2
        self.loss_SR = self.criterionL1(self.HR_G, self.HR_GroundTruth)
        self.loss_SR.backward()

    def optimize_parameters(self):
        self.forward()                   # compute fake images: G(A)
        # update
        self.optimizer_G.zero_grad()
        self.backward()
        self.optimizer_G.step()
