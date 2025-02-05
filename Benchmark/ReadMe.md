# Benchmarking

The details of the notebooks are as follow:

| Notebook Name | Input | Caching | Batchsizes | Profiling Tool   | Model | Dataset
|---|---|---|---|---|---|---|
|  Noise-Default-Caching |  Noise | Yes  | [1, 2, 4, 8, 16, 32, 64]  |  TF Profiler | NASNet-Imagenet | Noise |
|  Noise-Caching-Blocked |  Noise | No  | [1, 2, 4, 8, 16, 32, 64]  |  TF Profiler | NASNet-Imagenet | Noise |
|  Image-Default-Caching |  Image | Yes  | [1, 2, 4, 8, 16, 32, 64]  |  TF Profiler | NASNet-Imagenet | CIFAR100 Resized|
|  Image-Caching-Blocked |  Image | No  | [1, 2, 4, 8, 16, 32, 64]  |  TF Profiler | NASNet-Imagenet | CIFAR100 Resized |

The logs of the profiling tools can be visualized with Tensorboard. The profiling tool logs should follow this directory structure.
```
logs
├── profile
```
