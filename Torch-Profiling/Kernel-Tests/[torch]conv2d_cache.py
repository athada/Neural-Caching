import torch
import torch.nn as nn
import torch.nn.functional as F
from collections import OrderedDict
from time import time
import argparse

class CachedConv2d(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size, stride=1, padding=0, 
                 cache_size=1000, similarity_threshold=0.1):
        super(CachedConv2d, self).__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.kernel_size = kernel_size if isinstance(kernel_size, tuple) else (kernel_size, kernel_size)
        self.stride = stride if isinstance(stride, tuple) else (stride, stride)
        self.padding = padding if isinstance(padding, tuple) else (padding, padding)
        self.cache_size = cache_size
        self.similarity_threshold = similarity_threshold
        
        # Initialize weights and bias
        self.weight = nn.Parameter(
            torch.randn(out_channels, in_channels, self.kernel_size[0], self.kernel_size[1])
        )
        self.bias = nn.Parameter(torch.zeros(out_channels))
        
        # Initialize weights using Kaiming initialization
        nn.init.kaiming_uniform_(self.weight, mode='fan_in', nonlinearity='relu')
        
        # Initialize cache as OrderedDict to maintain size limit
        self.patch_cache = OrderedDict()
        
    def _compute_patch_hash(self, patch):
        # Convert patch to a form suitable for hashing
        return torch.sum(patch).item()
    
    def _find_similar_patch(self, current_patch):
        current_hash = self._compute_patch_hash(current_patch)
        
        # Search through cache for similar patches
        for cached_hash, (cached_patch, cached_result) in self.patch_cache.items():
            l2_diff = torch.norm(current_patch - cached_patch, p=2)
            if l2_diff < self.similarity_threshold:
                return cached_result
        return None
    
    def _update_cache(self, patch, result):
        # Add new result to cache
        patch_hash = self._compute_patch_hash(patch)
        
        # If cache is full, remove oldest entry
        if len(self.patch_cache) >= self.cache_size:
            self.patch_cache.popitem(last=False)
            
        self.patch_cache[patch_hash] = (patch.detach(), result.detach())
    
    def forward(self, x):
        device = x.device
        weight = self.weight.to(device)
        bias = self.bias.to(device)
        
        batch_size, in_channels, height, width = x.shape
        
        # Calculate output dimensions
        out_height = (height + 2 * self.padding[0] - self.kernel_size[0]) // self.stride[0] + 1
        out_width = (width + 2 * self.padding[1] - self.kernel_size[1]) // self.stride[1] + 1
        
        # Apply padding
        if max(self.padding) > 0:
            x = F.pad(x, (self.padding[1], self.padding[1], self.padding[0], self.padding[0]))
        
        output = torch.zeros(batch_size, self.out_channels, out_height, out_width, device=device)
        
        cache_hits = 0
        total_patches = 0
        
        # Perform convolution with caching
        for b in range(batch_size):
            for h in range(out_height):
                for w in range(out_width):
                    h_start = h * self.stride[0]
                    w_start = w * self.stride[1]
                    
                    # Extract current patch
                    current_patch = x[b, :, 
                                    h_start:h_start + self.kernel_size[0], 
                                    w_start:w_start + self.kernel_size[1]]
                    total_patches += 1
                    
                    # Try to find similar patch in cache
                    cached_result = self._find_similar_patch(current_patch)
                    
                    if cached_result is not None:
                        # Cache hit
                        cache_hits += 1
                        output[b, :, h, w] = cached_result
                    else:
                        # Cache miss - compute convolution
                        result = torch.zeros(self.out_channels, device=device)
                        for c_out in range(self.out_channels):
                            result[c_out] = torch.sum(current_patch * weight[c_out]) + bias[c_out]
                        
                        output[b, :, h, w] = result
                        self._update_cache(current_patch, result)
        
        # Print cache statistics
        cache_hit_rate = (cache_hits / total_patches) * 100 if total_patches > 0 else 0
        print(f"\nCache hit rate: {cache_hit_rate:.2f}% ({cache_hits}/{total_patches})")
        
        return output

def parse_args():
    parser = argparse.ArgumentParser(description='Cached Convolution Layer Testing')
    parser.add_argument('--batch_size', type=int, default=4,
                        help='Batch Size for testing (default: 4)')
    parser.add_argument('--cache_size', type=int, default=1000,
                        help='Size of the Cache (default: 1000)')
    parser.add_argument('--similarity_threshold', type=float, default=0.1,
                        help='L2 Norm threshold for patch similarity (default: 0.1)')
    return parser.parse_args()

def test_cached_conv2d(args):
    devices = ['cpu']
    if torch.backends.mps.is_available():
        devices.append('mps')
        
    for device in devices:
        print(f"\nTesting on {device.upper()}...")
        
        # Test different kernel configurations
        configs = [
            {'kernel_size': 3, 'padding': 1},  # 3x3 conv
            {'kernel_size': 5, 'padding': 2},  # 5x5 conv
        ]
        
        for config in configs:
            # Create input tensor with some repeated patterns
            x = torch.randn(args.batch_size, 3, 32, 32).to(device)
            k_h = config['kernel_size'] if isinstance(config['kernel_size'], tuple) else config['kernel_size']
            k_w = config['kernel_size'][-1] if isinstance(config['kernel_size'], tuple) else config['kernel_size']
            
            # Add similar patches to test caching
            mid_h, mid_w = 16, 16
            x[:, :, mid_h:mid_h+k_h, mid_w:mid_w+k_w] = x[:, :, mid_h-k_h:mid_h, mid_w-k_w:mid_w] + torch.randn(1, 3, k_h, k_w).to(device) * 0.05
            
            # Initialize Cached-Conv Layer
            conv_new = CachedConv2d(
                in_channels=3,
                out_channels=64,
                cache_size=args.cache_size,
                similarity_threshold=args.similarity_threshold,
                **config
            ).to(device)

            # Initialize Old layer
            conv = nn.Conv2d(
                in_channels=3,
                out_channels=64,
                **config
            ).to(device)

            # Forward pass for Cached-Conv Layer
            start_1 = time()
            output = conv_new(x)
            end_1 = time()

            # Forward pass for Old Conv Layer
            start_2 = time()
            output = conv(x)
            end_2 = time()
            
            print(f"+ Kernel configuration: {config}")
            print(f"+ Input shape: {x.shape}")
            print(f"+ Output shape: {output.shape}")
            print(f"+ Time Taken by Cached Version: {(end_1 - start_1)/60:.4f} minutes")
            print(f"+ Time Taken by Old Version: {(end_2 - start_2)/60:.4f} minutes")

if __name__ == "__main__":
    args = parse_args()
    test_cached_conv2d(args)
    test_cached_conv2d()
