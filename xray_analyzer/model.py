import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import models

class CustomDenseNet(models.DenseNet):
    def forward(self, x):
        features = self.features(x)
        out = F.relu(features, inplace=False)
        out = F.adaptive_avg_pool2d(out, (1, 1))
        out = torch.flatten(out, 1)
        out = self.classifier(out)
        return out

def load_model():
    print("🧠 Loading pre-trained DenseNet-121 model...")
    model = CustomDenseNet(
        growth_rate=32,
        block_config=(6, 12, 24, 16),
        num_init_features=64,
        bn_size=4,
        drop_rate=0
    )
    pretrained_state_dict = models.densenet121(weights=models.DenseNet121_Weights.DEFAULT).state_dict()
    model.load_state_dict(pretrained_state_dict)
    model.eval()
    return model