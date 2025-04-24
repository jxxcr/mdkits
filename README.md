# MD 轨迹分析脚本
`mdkits` 提供了多种工具, 安装脚本:
```bash
pip install mdkits --upgrade
```

### 密度分布
`density`用于分析体系中的某种元素沿z轴的密度分布, 如分析体系中的`O`元素沿z轴的密度分布, `--element`选项指定元素使用`MDAnalysis`的[选择语言](https://userguide.mdanalysis.org/stable/selections.html):
```bash
mdkits density [FILENAME] --element="name H" --cell [FILENAME]
```
这样会输出一个文件名为`density_name_H.dat`的文件, 第一列为z轴坐标, 第二列为浓度分布, 单位为 mol/L. 如果想输出为单位为 $g/cm^3$ 的密度分布, 可以指定`--atomic_mass` 选项, 如:
```bash
mdkits density [FILENAME] --element="name H" --cell [FILENAME] --atomic_mass=1.00784
```
则输出单位为 $g/cm^3$ 的密度分布. 可以指定表面原子来将密度分布归一化到表面, 如:
```bash
mdkits density [FILENAME] --element="name O" --cell 10,10,10 --atomic_mass=18.01528 --surface="name Pt and name Ru"
```
这样会将密度分布归一化到表面, 同时以O原子的位置作为水分子的位置分析处理水分子的密度分布. 对于体系中存在 $OH^-$ 离子的体系可以使用`--update_water`的选项在每一帧更新水分子的位置, 不需要额外指定元素, 如:
```bash
mdkits density [FILENAME] --update_water --cell 10,10,10 --atomic_mass=18.01528 --surface="name Pt and name Ru"
```
输出的文件名为`density_water.dat`.

### 氢键

#### 单个水分子

#### 氢键分布

### 角度

#### 与表面法向量夹角分布

#### ion - O - ion 夹角分布

#### $\cos \phi \rho_{H_2 O}$ 分布

### RDF

### 位置归一化
`wrap`用于将轨迹文件中的原子位置进行归一化处理, 如将`[FILENAME]`中的原子位置归一化到晶胞中, 并输出为`wrapped.xyz`, 默认从`cp2k`的输出文件`input_inp`中读取`ABC`和`ALPHA_BETA_GAMMA`信息作为晶胞参数:
```bash
mdkits wrap [FILENAME] 
```
或指定`cp2k`的输入文件:
```bash
mdkits wrap [FILENAME] --cp2k_input_file setting.inp
```
或指定晶胞参数:
```bash
mdkits wrap [FILENAME] --cell 10,10,10
```
默认的`[FILENAME]`为`*-pos-1.xyz`

## DFT 性质分析脚本
### PDOS

### CUBE 文件
`cube`用于处理[`cube`格式](https://paulbourke.net/dataformats/cube/)的文件, 将其在z轴上进行平均:
```bash
mdkits cube [FILENAME]
```
分析好的数据会输出为`cube.out`, 可以同时计算一个区域内的平均值:
```bash
mdkits cube [FILENAME] -b 1 2
```
会将平均值打印在屏幕上, 同时记录在`cube.out`中的注释行.

## 其他
### 轨迹提取
`extract`用于提取轨迹文件中的特定的帧, 如从`frames.xyz`中提取第 1000 帧到第 2000 帧的轨迹文件, 并输出为`1000-2000.xyz`, `-r`选项的参数与`Python`的切片语法一致:
```bash
mdkits extract frames.xyz -r 1000:2000 -o 1000-2000.xyz
```
或从`cp2k`的默认输出的轨迹文件`*-pos-1.xyz`文件中提取最后一帧输出为`extracted.xyz`(`extract`的默认行为):
```bash
mdkits extract
```
或每50帧输出一个结构到`./coord`目录中, 同时调整输出格式为`cp2k`的`@INCLUDE coord.xyz`的形式:
```bash
mdkits extract -cr ::50
```

### 结构文件转换
`convert`用于将结构文件从一种格式转换为另一种格式, 如将`structure.xyz`转换为`out.cif`(默认文件名为`out`), 对于不储存周期性边界条件的文件, 可以使用`--cell`选项指定`PBC`:
```bash
mdkits convert -c structure.xyz --cell 10,10,10
```
将`structure.cif`转换为`POSCAR`:
```bash
mdkits convert -v structure.cif
```
将`structure.cif`转换为`structure_xyz.xyz`:
```bash
mdkits convert -c structure.cif -o structure_xyz
```

### 数据处理
`data`用于对数据进行处理如:
1. `--nor`: 对数据进行归一化处理
2. `--gaus`: 对数据进行高斯过滤
3. `--fold`: 堆数据进行折叠平均
4. `--err`: 计算数据的误差棒   
等

### 绘图工具
`plot`用于绘制数据图, `plot`需要读取`yaml`格式的配置文件进行绘图, `yaml`文件的形式如下:
```yaml
# plot mode 1
figure1:
  data:
    legend1: ./data1.dat
    legend2: ./data2.dat
  x:
    0: x-axis
  y:
    1: y-axis
  x_range: 
    - 5
    - 15

# plot mode 2
figure2:
  data:
    y-xais: ./data.dat
  x:
    0: x-axis
  y:
    1: legend1
    2: legend2
    3: legend3
    4: legend4
    5: legend5
  y_range:
    - 0.5
    - 6
  legend_fontsize: 12

# plot mode error
12_dp_e_error:
  data:
    legend: ./error.dat
  x:
    0: x-axis
  y:
    1: y-axis
  fold: dp
  legend_fontsize: 12
```
如上`plot`支持三种绘图模式, `mode 1`, `mode 2`和`mode error`. `mode 1`用于绘制多组数据文件的同一列数据对比, `mode 2`用于绘制同一数据文件的不同列数据对比, `mode error`用于绘制均方根误差图.

`plot`可以同时处理多个`yaml`文件, 每个`yaml`文件可以包含多个绘图配置, `mode 1`和`mode 2`的绘图配置可以自动识别, 但是`error`模式需要而外指定, 如:
```bash
mdkits plot *.yaml
```
和:
```bash
mdkits plot *.yaml --error
```