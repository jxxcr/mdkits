# mdkits
`mdkits` 提供了多种工具, 安装脚本:
```bash
pip install mdkits --upgrade
```
## 通用的选项参数类型
1. `CELL TYPE`: 指定晶胞参数, 如`10,10,10`, `10,10,10,90,90,90`等
2. `FRAME RANGE`: 指定帧范围, 如`1`, `1:10:2`等
3. `--group`和`--surface`: 按[选择语言](https://userguide.mdanalysis.org/stable/selections.html)选取分析对象
4. `--update_water`, `--distance` 和 `--angle`: 在分析轨迹的过程中开启动态更新水分子的功能
5. 在服务器中将其对应的`SSH config-file`中的`Host`指定为`ssh_name`环境变量就可以在脚本输出`path`的前面带上`ssh_name`, 方便后续的`scp`操作:
```bash
ssh_name:path/to/file
```

## 轨迹文件处理脚本
`md`为轨迹文件处理工具, 其中包含多个处理工具
### 密度分布
`density`用于分析体系中的某种元素沿z轴的密度分布, 如分析体系中的`O`元素沿z轴的密度分布:
```bash
mdkits md density [FILENAME] --group="name H" --cell [FILENAME]
```
这样会输出一个文件名为`density_name_H.dat`的文件, 第一列为z轴坐标, 第二列为浓度分布, 单位为 mol/L. 如果想输出为单位为 $g/cm^3$ 的密度分布, 可以指定`--atomic_mass` 选项, 如:
```bash
mdkits md density [FILENAME] --group="name H" --cell [FILENAME] --atomic_mass=1.00784
```
则输出单位为 $g/cm^3$ 的密度分布. 可以指定表面原子来将密度分布归一化到表面, 如:
```bash
mdkits md density [FILENAME] --group="name O" --cell 10,10,10 --atomic_mass=18.01528 --surface="name Pt and name Ru"
```
这样会将密度分布归一化到表面, 同时以O原子的位置作为水分子的位置分析处理水分子的密度分布. 对于体系中存在 $OH^-$ 离子的体系可以使用`--update_water`的选项在每一帧更新水分子的位置, 不需要额外指定元素, 如:
```bash
mdkits md density [FILENAME] --update_water --cell 10,10,10 --atomic_mass=18.01528 --surface="name Pt and name Ru"
```
输出的文件名为`density_water.dat`.

### 氢键
`hb`用于分析体系中的氢键, 如分析体系中的氢键在z轴上的分布:
```bash
mdkits md hb [FILENAME] --cell 10,10,40 --surface "prop z < 10" --update_water
```
或分析单个水分子的氢键:
```bash
mdkits md hb [FILENAME] --cell 10,10,40 --index 15
```

### 角度
`angel`用于分析水分子中的二分向量和OH向量与表面法向量的夹角的丰度分布, 如分析距离表面 5 Å 的水分子的角度丰度分布:
```bash
mdkits md angle [FILENAME] --cell 10,10,40 --surface "name Pt" --water_height 5
```

### 偶极分布
`diople`用于分析体系中的偶极($\cos \phi \rho_{H_2 O}$)分布, 如分析体系中的 $\cos \phi \rho_{H_2 O}$ 分布:
```bash
mdkits md diople [FILENAME] --cell 10,10,40 --surface "name Pt"
```

### 径向分布函数(RDF)
`rdf`用于分析两个`group`之间的径向分布函数, 如分析体系中的`O`元素与`H`元素之间的径向分布函数:
```bash
mdkits md rdf [FILENAME] --group "name O" "name H" --cell 10,10,40 --range 0.1 5
```

### 均方位移(MSD)
`msd`用于分析体系中某些原子的均方位移, 如分析体系中`Li`原子在z轴上的均方位移:
```bash
mdkits md msd [FILENAME] z "name Li"
```

### 监控
`monitor`用于监控体系中原子高度, 键长和键角的变化, 如监控`index`为0的原子的高度:
```bash
mdkits md monitor [FILENAME] --cell 10,10,40 --surface "name Pt" -i 0
```
会输出0距离表面的高度随每一帧的变化, 如监控0-1的键长:
```bash
mdkits md monitor [FILENAME] --cell 10,10,40 --surface "name Pt" -i 0 -i 1
```
会输出0和1距离表面的高度和0-1之间的键长随每一帧的变化, 如监控1-0-2的键角:
```bash
mdkits md monitor [FILENAME] --cell 10,10,40 --surface "name Pt" -i 1 -i 0 -i 2
```
会输出1, 0, 2距离表面的高度, 1-0和0-2的键长和1-0-2的键角随每一帧的变化, 注意位于角上的原子应该放在中间

### 位置归一化
`wrap`用于将轨迹文件中的原子位置进行归一化处理, 如将`[FILENAME]`中的原子位置归一化到晶胞中, 并输出为`wrapped.xyz`, 默认从`cp2k`的输出文件`input_inp`中读取`ABC`和`ALPHA_BETA_GAMMA`信息作为晶胞参数:
```bash
mdkits md wrap [FILENAME] 
```
或指定`cp2k`的输入文件:
```bash
mdkits md wrap [FILENAME] --cp2k_input_file setting.inp
```
或指定晶胞参数:
```bash
mdkits md wrap [FILENAME] --cell 10,10,10
```
默认的`[FILENAME]`为`*-pos-1.xyz`

### 振动态密度(VDOS)
`vac`用于分析轨迹的速度自相关函数, 同时计算速度自相关函数的傅里叶变换, 即振动动态密度(VDOS), 如分析体系中的VDOS:
```bash
mdkits md vac h2o-vel-1.xyz
```
默认的`[FILENAME]`为`*-vel-1.xyz`

## DFT 性质分析脚本
`dft`为DFT性质分析工具, 其中包含多个分析工具
### PDOS
`pdos`用于分析体系中的pdos, 分析[FILENAME]的d轨道的dos:
```bash
mdkits dft pdos [FILENAME] -t d
```

### CUBE 文件
`cube`用于处理[`cube`格式](https://paulbourke.net/dataformats/cube/)的文件, 将其在z轴上进行平均:
```bash
mdkits dft cube [FILENAME]
```
分析好的数据会输出为`cube.out`, 可以同时计算一个区域内的平均值:
```bash
mdkits dft cube [FILENAME] -b 1 2
```
会将平均值打印在屏幕上, 同时记录在`cube.out`中的注释行.

## 建模
`build`为建模的工具, 其中包含多个建模工具

### 构建体相模型
`bulk`用于构建体相模型, 如构建`Pt`的`fcc`体相模型:
```bash
mdkits build bulk Pt fcc
```
构建为常胞模型:
```bash
mdkits build bulk Pt fcc --cubic
```
构建一个`Caesium chloride`结构的模型:
```bash
mdkits build bulk CsCl cesiumchloride -a 4.123
```
构建一个`fluorite `结构的模型:
```bash
mdkits build bulk BaF2 fluorite -a 6.196
```

### 构建表面模型
`surface`用于构建常见的表面模型, 骑用法为:
```bash
mdkits build surface [ELEMENT] [SURFACE_TYPE] [SIZE]
```
如构建`Pt`的`fcc111`表面模型:
```bash
mdkits build surface Pt fcc111 2 2 3 --vacuum 15
```
构建石墨烯表面:
```bash
mdkits build surface C2 graphene 3 3 1 --vacuum 15
```

### 从现有结构中构建表面模型
`cut`用于从现有的结构中构建表面模型(模型必须为常胞模型), 如从`Pt_fcc.cif`中构建`fcc331`表面模型:
```bash
mdkits build cut Pt_fcc.cif --face 3 3 1 --size 3 3 5 --vacuum 15
```

### 在表面结构上添加吸附物
`adsorbate`用于在表面结构上添加吸附物, 如在`surface.cif`上添加`H`原子:
```bash
mdkits build adsorbate surface.cif H --select "index 0" --height 1    
```
或在`Pt_fcc111_335.cif`上添加覆盖度为5的`H`原子:
```bash
mdkits build adsorbate Pt_fcc111_335.cif H --select "prop z > 16" --height 2 --cover 5
```

### 构建溶液相模型
`solution`用于构建溶液相模型, 初次使用时应先安装`juliaup`:
```bash
mdkits build solution --install_julia
```
然后安装`Packmol`:
```bash
mdkits build solution --install_packmol
```
成功安装后就可以使用`solution`功能了, 如构建一个32个水分子的水盒子:
```bash
mdkits build solution --water_number 32 --cell 9.86,9.86,9.86
```
或构建一个含有离子的溶液:
```bash
mdkits build solution li.xyz k.xyz --water_number 64 --tolerance 2.5 -n 25 -n 45 --cell 15,15,15
```
其中`-n`的个数必须与指定的溶剂分子种类数量一致, 用于分别指定添加的溶剂的数量. 或者从`packmol`的输入文件中构建溶液相模型:
```bash
mdkits build solution input.pm input2.pm  --infile
```

### 构建界面模型
`interface`用于构建界面模型, 如构建一个没有真空的界面模型:
```bash
mdkits build interface --slab Pt_fcc100_555.cif --sol water_160.cif
```
或构建一个带有气相模型的界面:
```bash
mdkits build interface --slab Pt_fcc100_555.cif --sol water_160.cif --cap ne --vacuum 20
```

### 构建超胞模型
`supercell`用于构建超胞模型:
```bash
mdkits build supercell Li3PO4.cif 2 2 2
```

## 其他
### 轨迹提取
`extract`用于提取轨迹文件中的特定的帧, 如从`frames.xyz`中提取第 1000 帧到第 2000 帧的轨迹文件, 并输出为`1000-2000.xyz`, `-r`选项的参数与`Python`的切片语法一致:
```bash
mdkits extract frames.xyz -r 1000:2000 -o 1000-2000.xyz
```
或从`cp2k`的默认输出的轨迹文件`*-pos-1.xyz`文件中提取最后一帧输出为`frames_-1.xyz`(`extract`的默认行为):
```bash
mdkits extract
```
或每50帧输出一个结构到`./coord`目录中, 同时调整输出格式为`cp2k`的`@INCLUDE coord.xyz`的形式:
```bash
mdkits extract -cr ::50
```
提取部分元素的位置, 如提取`O`元素和`H`元素的位置:
```bash
mdkits extract --select "name O or name H"
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