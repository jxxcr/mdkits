# MD 轨迹分析脚本
`mdtool` 提供了多种工具, 安装脚本:
```bash
pip install mdtool --upgrade
```
### 密度分布

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
mdtool wrap [FILENAME] 
```
或指定`cp2k`的输入文件:
```bash
mdtool wrap [FILENAME] --cp2k_input_file setting.inp
```
或指定晶胞参数:
```bash
mdtool wrap [FILENAME] --cell 10,10,10
```
默认的`[FILENAME]`为`*-pos-1.xyz`

## DFT 性质分析脚本
### PDOS

### 静电势

### 电荷差分

## 其他
### 轨迹提取
`extract`用于提取轨迹文件中的特定的帧, 如从`frames.xyz`中提取第 1000 帧到第 2000 帧的轨迹文件, 并输出为`1000-2000.xyz`, `-r`选项的参数与`Python`的切片语法一致:
```bash
mdtool extract frames.xyz -r 1000:2000 -o 1000-2000.xyz
```
或从`cp2k`的默认输出的轨迹文件`*-pos-1.xyz`文件中提取最后一帧输出为`extracted.xyz`(`extract`的默认行为):
```bash
mdtool extract
```
或每50帧输出一个结构到`./coord`目录中, 同时调整输出格式为`cp2k`的`@INCLUDE coord.xyz`的形式:
```bash
mdtool extract -cr ::50
```

### 结构文件转换
`convert`用于将结构文件从一种格式转换为另一种格式, 如将`structure.xyz`转换为`out.cif`(默认文件名为`out`), 对于不储存周期性边界条件的文件, 可以使用`--cell`选项指定`PBC`:
```bash
mdtool convert -c structure.xyz --cell 10,10,10
```
将`structure.cif`转换为`POSCAR`:
```bash
mdtool convert -v structure.cif
```
将`structure.cif`转换为`structure_xyz.xyz`:
```bash
mdtool convert -c structure.cif -o structure_xyz
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
mdtool plot *.yaml
```
和:
```bash
mdtool plot *.yaml --error
```