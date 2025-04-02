# MD 轨迹分析脚本
mdtool 提供了多种工具
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
4. `err`: 计算数据的误差棒
等