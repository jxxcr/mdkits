import numpy as np
import os

# 定义变量
# pdos-k*-21150.cube
k1 = "O"
k2 = "H"
k3 = "Pt"
k4 = "Ne"
k5 = "Li"
Fermi = -3.615120
bin_size = 0.1

def process_pdos_file(filename, columns, fermi):
    data = np.loadtxt(filename, skiprows=2)
    energies = data[:, 1] * 27.2114 - fermi
    dos = np.sum(data[:, columns], axis=1)
    return np.column_stack((energies, dos))

def bin_data(energies, dos, bin_size):
    min_e = np.floor(np.min(energies))
    max_e = np.ceil(np.max(energies))
    bins = np.arange(min_e, max_e + bin_size, bin_size)
    binned_dos = np.zeros_like(bins)
    
    for i, e in enumerate(energies):
        bin_idx = np.searchsorted(bins, e) - 1
        if 0 <= bin_idx < len(bins):
            binned_dos[bin_idx] += dos[i]
    
    return bins, binned_dos

def process(prefix):
    # 处理ALPHA/BETA文件
    pt_pdos = process_pdos_file(f"./pdos-k3-{prefix}.cube", [7,8,9,10,11], Fermi)
    li_pdos = process_pdos_file(f"./pdos-k5-{prefix}.cube", [3], Fermi)
    o_pdos = process_pdos_file(f"pdos-k1-{prefix}.cube", [3,4,5,6], Fermi)
    h_pdos = process_pdos_file(f"pdos-k2-{prefix}.cube", [3], Fermi)
    
    # 合并数据
    pt_energies = pt_pdos[:, 0]
    pt_dos = pt_pdos[:, 1] 
    li_energies = li_pdos[:, 0]
    li_dos = li_pdos[:, 1]
    h2o_energies = o_pdos[:, 0]
    h2o_dos = o_pdos[:, 1] + h_pdos[:, 1]
    
    # 分bin处理
    pt_bins, pt_binned = bin_data(pt_energies, pt_dos, bin_size)
    li_bins, li_binned = bin_data(li_energies, li_dos, bin_size)
    h2o_bins, h2o_binned = bin_data(h2o_energies, h2o_dos, bin_size)
    
    # 保存结果
    np.savetxt(f"Pt-{prefix}.MAV", np.column_stack((pt_bins, pt_binned)), fmt="%-15.6f%-15.6f")
    np.savetxt(f"Li-{prefix}.MAV", np.column_stack((li_bins, li_binned)), fmt="%-15.6f%-15.6f")
    np.savetxt(f"H2O-{prefix}.MAV", np.column_stack((h2o_bins, h2o_binned)), fmt="%-15.6f%-15.6f")

# 处理ALPHA和BETA数据
process("21150")

# 清理临时文件
for f in [f"{k}.pdos" for k in [k1, k2, k3, k4, k5]]:
    if os.path.exists(f):
        os.remove(f)


