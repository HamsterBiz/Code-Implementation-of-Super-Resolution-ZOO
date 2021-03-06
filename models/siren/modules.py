import torch
import math
from torch import nn
import torch.nn.functional as F


def init_(weight, bias, c=6.0):
    with torch.no_grad():
        dim = weight.size(1)
        std = 1 / math.sqrt(dim)
        w_std = math.sqrt(c) * std
        weight.uniform_(-w_std, w_std)

        # if bias is not None:
        #     bias.uniform_(-std, std)


class Sine(nn.Module):
    def __init__(self, w0=1.):
        super().__init__()
        self.w0 = w0

    def forward(self, x):
        return torch.sin(self.w0 * x)


class Siren(nn.Module):
    def __init__(self, dim_in, dim_out, w0=1.0, c=6.0, w0_initial=30.0, use_bias=True, activation='sine', first_layer=False):
        super().__init__()
        weight = torch.zeros(dim_out, dim_in)
        bias = torch.zeros(dim_out) if use_bias else None
        if activation == 'sine':
            init_(weight, bias, c=c)
            self.do_not_init_again = True
            if first_layer:
                self.activation = Sine(w0_initial)
            else:
                self.activation = Sine(w0)
        elif activation == 'relu':
            self.activation = torch.nn.ReLU(inplace=True)
        elif activation == 'none':
            self.activation = None
        else:
            raise NotImplementedError("not implemented {}".format(activation))

        self.weight = nn.Parameter(weight)
        self.bias = nn.Parameter(bias) if use_bias else None

    def forward(self, x):
        out = F.linear(x, self.weight, self.bias)
        if self.activation is not None:
            out = self.activation(out)
        return out


class SirenNet(nn.Module):
    def __init__(self, dim_in, dim_hidden, dim_out, num_layers, w0=1., use_bias=True, final_activation='none'):
        super().__init__()
        layers = []
        for ind in range(num_layers):
            layer_dim_in = dim_in if ind == 0 else dim_hidden
            first_layer = True if ind == 0 else False

            layers.append(Siren(
                dim_in=layer_dim_in,
                dim_out=dim_hidden,
                w0=w0,
                use_bias=use_bias,
                activation='sine',
                first_layer=first_layer
            ))

        self.net = nn.Sequential(*layers)
        self.last_layer = Siren(dim_in=dim_hidden, dim_out=dim_out, w0=w0, use_bias=use_bias, activation=final_activation, first_layer=False)

    def forward(self, x):
        x = self.net(x)
        return self.last_layer(x)
