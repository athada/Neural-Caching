# Benchmarking

The details of the notebooks are as follow:

| Notebook Name | Input | Caching | Batchsizes | Profiling Tool   | Model | Dataset
|---|---|---|---|---|---|---|
|  Noise-Default-Caching |  Noise | Yes  | [1, 2, 4, 8, 16, 32, 64]  |  TF Profiler | NASNet-Imagenet | Noise |
|  Noise-Caching-Blocked |  Noise | No  | [1, 2, 4, 8, 16, 32, 64]  |  TF Profiler | NASNet-Imagenet | Noise |
|  Image-Default-Caching |  Image | Yes  | [1, 2, 4, 8, 16, 32, 64]  |  TF Profiler | NASNet-Imagenet | CIFAR100 Resized|
|  Image-Caching-Blocked |  Image | No  | [1, 2, 4, 8, 16, 32, 64]  |  TF Profiler | NASNet-Imagenet | CIFAR100 Resized |

<br>

tensorboard logs the file in certain specifc directiry strucuture. 
```
./logs
├── Image
│   ├── Cache
│   │   ├── CPU
│   │   │   ├── 1
│   │   │   │   └── plugins
│   │   │   │       └── profile
│   │   │   │           └── 2025_02_05_15_27_37
│   │   │   │               └── C17586.xplane.pb
│   │   │   ├── 100
│   │   │   │   └── plugins
│   │   │   │       └── profile
│   │   │   │           └── 2025_02_05_15_29_24
│   │   │   │               └── C17586.xplane.pb
│   │   │   ├── 128
│   │   │   │   └── plugins
│   │   │   │       └── profile
│   │   │   │           └── 2025_02_05_15_30_37
│   │   │   │               └── C17586.xplane.pb
│   │   │   ├── 16
│   │   │   │   └── plugins
│   │   │   │       └── profile
│   │   │   │           └── 2025_02_05_15_27_51
│   │   │   │               └── C17586.xplane.pb
│   │   │   ├── 32
│   │   │   │   └── plugins
│   │   │   │       └── profile
│   │   │   │           └── 2025_02_05_15_28_05
│   │   │   │               └── C17586.xplane.pb
│   │   │   ├── 4
│   │   │   │   └── plugins
│   │   │   │       └── profile
│   │   │   │           └── 2025_02_05_15_27_41
│   │   │   │               └── C17586.xplane.pb
│   │   │   ├── 64
│   │   │   │   └── plugins
│   │   │   │       └── profile
│   │   │   │           └── 2025_02_05_15_28_35
│   │   │   │               └── C17586.xplane.pb
│   │   │   └── 8
│   │   │       └── plugins
│   │   │           └── profile
│   │   │               └── 2025_02_05_15_27_45
│   │   │                   └── C17586.xplane.pb
```
Before we can get the detaisl of all the  runs in single folder we need to restrucre the logs directory using `restruct.py`. Once restructred, the logs of the profiling tools can be visualized with Tensorboard. After restructing, we'll have this strcutre.
```
./logs
└── 2025020514-4351-4802
    └── plugins
        └── profile
            ├── Image-Cache-CPU-1
            │   └── C17586.xplane.pb
            ├── Image-Cache-CPU-100
            │   └── C17586.xplane.pb
            ├── Image-Cache-CPU-128
            │   └── C17586.xplane.pb
            ├── Image-Cache-CPU-16
            │   └── C17586.xplane.pb
            ├── Image-Cache-CPU-32
            │   └── C17586.xplane.pb
            ├── Image-Cache-CPU-4
            │   └── C17586.xplane.pb
            ├── Image-Cache-CPU-64
            │   └── C17586.xplane.pb
            ├── Image-Cache-CPU-8
            │   └── C17586.xplane.pb
```
Now tensorboard can be initilized in terminal at `./logs/025-02[05144351-05154802]` direcitry using below command:
```
tensorbaord --logsdir ./logs/2025020514-4351-4802
```

**BugFix**: The pathname after directory restructuring should not contain `[` otheriwse after launchign the tensorboard, the profile will show hostname as`default` instead of original hostname somthing like `C17586`. Due to this bug the runs will be listed under Profiler tab but the data will not laod up.
