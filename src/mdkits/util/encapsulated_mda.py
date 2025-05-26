import MDAnalysis
import numpy as np
from . import numpy_geo


def update_water(self, o_group, h_group, distance_judg=1.2, angle_judg:tuple[float, float]=(None, None), return_index=False):
    """
    input: o and h atom
    output: o and two h in this frame
    """
    oh_pair = MDAnalysis.lib.distances.capped_distance(o_group.positions, h_group.positions, min_cutoff=0, max_cutoff=distance_judg, box=self.u.dimensions, return_distances=False)

    oh_o = oh_pair[:, 0]
    unique_oh_o = np.unique(oh_o)

    group_oh_h = {}
    for oh_o_index in unique_oh_o:
        oh_h_index = oh_pair[oh_o == oh_o_index, 1]
        group_oh_h[oh_o_index] = oh_h_index

    oh1_list = []
    oh2_list = []
    o_list = []
    for oh_o_index in unique_oh_o:
        oh_h_index = group_oh_h[oh_o_index]
        if angle_judg is not None and len(oh_h_index) >= 2:
                for i in range(len(oh_h_index)):
                    for j in range(i + 1, len(oh_h_index)):
                            h1_index = oh_h_index[i]
                            h2_index = oh_h_index[j]

                            o_pos = o_group[oh_o_index].position
                            h1_pos = h_group[h1_index].position
                            h2_pos = h_group[h2_index].position

                            oh1_vec = h1_pos - o_pos
                            oh2_vec = h2_pos - o_pos

                            angle_deg = numpy_geo.vector_vector_angle(oh1_vec, oh2_vec)

                            if angle_judg[0] <= angle_deg <= angle_judg[1]:
                                o_list.append(oh_o_index)
                                oh1_list.append(h1_index)
                                oh2_list.append(h2_index)
        elif len(oh_h_index) == 2:
            o_list.append(oh_o_index)
            oh1_list.append(oh_h_index[0])
            oh2_list.append(oh_h_index[1])
    oh1_index = np.array(oh1_list)
    oh2_index = np.array(oh2_list)
    o_index = np.array(o_list)

    if return_index:
        return o_index, oh1_index, oh2_index
    else:
        if len(o_index) == 0:
            raise ValueError("No water found in this atom group")

        o = o_group[o_index]
        oh1 = h_group[oh1_index]
        oh2 = h_group[oh2_index]
        return o, oh1, oh2
