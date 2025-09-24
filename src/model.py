import torch  # ✨ ADD THIS LINE
import torch.nn as nn
import torch.nn.functional as F
from torchvision import models

class CustomDenseNet(models.DenseNet):
    """
    A custom DenseNet class that overrides the forward pass to ensure
    the final ReLU operation is "out-of-place". This is crucial for
    making Grad-CAM compatible with this architecture.
    """
    def forward(self, x):
        features = self.features(x)
        # The key change from the original: inplace=False
        out = F.relu(features, inplace=False)
        out = F.adaptive_avg_pool2d(out, (1, 1))
        out = torch.flatten(out, 1)
        out = self.classifier(out)
        return out

def load_model():
    """Initializes the custom DenseNet model and loads pretrained weights."""
    print("🧠 Loading pre-trained DenseNet-121 model...")
    # These are the standard parameters for DenseNet-121
    model = CustomDenseNet(
        growth_rate=32,
        block_config=(6, 12, 24, 16),
        num_init_features=64,
        bn_size=4,
        drop_rate=0
    )
    # Load weights from the standard pre-trained model
    pretrained_state_dict = models.densenet121(weights=models.DenseNet121_Weights.DEFAULT).state_dict()
    model.load_state_dict(pretrained_state_dict)
    model.eval()
    print("✅ Model loaded successfully.")
    return model