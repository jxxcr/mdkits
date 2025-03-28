#!/usr/bin/env python3

# is to generate cp2k input file 
import argparse
import shutil
import os
from ase.io import read, write
from pymatgen.core.structure import Structure
from pymatgen.io.cp2k.inputs import (
	Cp2kInput, 
	Section, 
	Keyword, 
	Cell, 
	Coord, 
	Kind
)


def insert_section(strs, section_name, section):

	# to insert subsection to a high level section
	insert = Cp2kInput.from_str(strs)
	section.insert(insert.get_section(section_name))
	
	return section


def add_keyword(keyword, section):

	# to add keyword in a section
	section.add(Keyword.from_str(keyword))


def Global(
	run_type="ENEGRY", 
	project_name="cp2k", 
	print_level="MEDIUM", 
	walltime=107000
):

	# global section
	Global = Section("GLOBAL")
	
	add_keyword(f"RUN_TYPE {run_type}", Global)
	add_keyword(f"PROJECT_NAME {project_name}", Global)
	add_keyword(f"PRINT_LEVEL {print_level}", Global)
	add_keyword(f"WALLTIME {walltime}", Global)
	
	return Global


def motion(
	constraint_list=None,
	cell_opt=False,
	geo_opt=False
):

	# motion section
	motion = Section("MOTION")
	
	## constraint subsection
	if constraint_list != None:
	    strs = f"""
	    &CONSTRAINT
	      &FIXED_ATOMS
	        LIST {constraint_list}
	      &END FIXED_ATOMS
	    &END CONSTRAINT
	    """
	    insert_section(strs, "CONSTRAINT", motion)
	
	## cell_opt subsection
	if cell_opt:
	    strs = f"""
	    &CELL_OPT
	      OPTIMIZER BFGS
	      MAX_ITER 200
	    &END CELL_OPT
	    """
	    insert_section(strs, "CELL_OPT", motion)
	
	## geo_opt subsection
	if geo_opt:
	    strs = f"""
	    &GEO_OPT
	      TYPE MINIMIZATION
	      OPTIMIZER BFGS
	      MAX_ITER 500
	    &END GEO_OPT
	    """
	    insert_section(strs, "GEO_OPT", motion)
	
	return motion


def force_eval(
	structure,
	method="QUICKSTEP",
	data_path="/public/software/cp2k-2022.1-intel/cp2k-2022.1/data",
	charge=None,
	ot=False,
	hse=False
):

	# force_eval section
	force_eval = Section("FORCE_EVAL")
	add_keyword(f"METHOD {method}", force_eval)
	
	## dft subsection
	dft = Section("DFT")
	add_keyword(f"BASIS_SET_FILE_NAME {data_path}/BASIS_MOLOPT", dft)
	add_keyword(f"POTENTIAL_FILE_NAME {data_path}/GTH_POTENTIALS", dft)
	if isinstance(charge, int):
	    dft.add_keyword(f"CHARGE {charge}", dft)
	
	### mgrid subsubsection
	strs = """
	&MGRID
	  CUTOFF 400
	&END MGRID
	"""
	insert_section(strs, "MGRID", dft)
	
	### qs subsubsection
	strs = """
	&QS
	  EPS_DEFAULT 1.0E-13
	  EXTRAPOLATION ASPC
	  EXTRAPOLATION_ORDER 2
	&END QS
	"""
	insert_section(strs, "QS", dft)
	
	### scf subsubsection
	if ot:
	    strs = """
	    &SCF
	      SCF_GUESS RESTART
	      EPS_SCF 3.0E-6
	      MAX_SCF 50
	
	      &OUTER_SCF
	        EPS_SCF 3.0E-6
	        MAX_SCF 20
	      &END OUTER_SCF
	
	      &OT
	        MINIMIZER DIIS
	        PRECONDITIONER FULL_SINGLE_INVERSE
	      &END OT
	    &END SCF
	    """
	    insert_section(strs, dft)
	else:
	    strs = """
	    &SCF
	      SCF_GUESS RESTART
	      EPS_SCF 3.0E-7
	      MAX_SCF 500
	      ADDED_MOS 500
	      CHOLESKY INVERSE
	
	      &SMEAR ON
	        METHOD FERMI_DIRAC
	      &END SMEAR
	
	      &DIAGONALIZATION
	        ALGORITHM STANDARD
	      &END DIAGONALIZATION
	
	      &MIXING
	        METHOD BROYDEN_MIXING
	        ALPHA 0.15
	        BETA 1.0
	        NBROYDEN 16
	      &END MIXING
	
	      &PRINT
	
	        &RESTART
	          ADD_LAST NUMERIC
	          
	          &EACH
	            QS_SCF 50
	          &END EACH
	        &END RESTART
	      &END PRINT
	    &END SCF
	    """
	    insert_section(strs, "SCF", dft)
	
	### xc subsubsection
	if hse:
	    strs = f"""
	    &XC
	
	      &VDW_POTENTIAL
	        DISPERSION_FUNCTIONAL PAIR_POTENTIAL
	
	        &PAIR_POTENTIAL
	          TYPE DFTD3
	          PARAMETER_FILE_NAME {data_path}/dftd3.dat
	          REFERENCE_FUNCTIONAL PBE
	        &END PAIR_POTENTIAL
	      &END VDW_POTENTIAL
	
	      &XC_FUNCTIONAL
	
	        &XWPBE
	          SCALE_X -0.25
	          SCALE_X0 1.0
	          OMEGA 0.11
	        &END XWPBE
	
	        &PBE
	          SCALE_X 0.0
	          SCALE_C 1.0
	        &END PBE
	      &END XC_FUNCTIONAL
	
	      &HF
	        FRACTION 0.25
	
	        &INTERACTION_POTENTIAL
	          POTENTIAL_TYPE SHORTRANGE
	          OMEGA 0.11
	          T_C_G_DATA
	        &END INTERACTION_POTENTIAL
	
	        &SCREENING
	          EPS_SCHWARZ 1.0E-6
	          SCREEN_ON_INITIAL_P .FALSE.
	        &END SCREENING
	
	        &MEMORY
	          MAX_MEMORY 3000
	          EPS_STORAGE_SCALING 0.1
	        &END MEMORY
	
	        &PERIODIC
	          NUMPER_OF_SHELLS 0
	        &END PERIODIC
	      &END HF
	    &END XC
	    """
	    insert_section(strs, "XC", dft)
	else:
	    strs = f"""
	    &XC
	
	      &XC_FUNCTIONAL PBE
	      &END XC_FUNCTIONAL
	
	      &VDW_POTENTIAL
	        DISPERSION_FUNCTIONAL PAIR_POTENTIAL
	
	        &PAIR_POTENTIAL
	          TYPE DFTD3
	          PARAMETER_FILE_NAME {data_path}/dftd3.dat
	          REFERENCE_FUNCTIONAL PBE
	        &END PAIR_POTENTIAL
	      &END VDW_POTENTIAL
	    &END XC
	    """
	    insert_section(strs, "XC", dft)
	
	### print subsubsection
	strs = """
	&PRINT
	
	  &E_DENSITY_CUBE
	    ADD_LAST NUMERIC
	
	    &EACH
	      GEO_OPT 0
	    &END EACH
	  &END E_DENSITY_CUBE
	
	  &PDOS
	    COMPONENTS .TRUE.
	    NLUMO -1
	    ADD_LAST NUMERIC
	
	    &EACH
	      MD 50
	      GEO_OPT 0
	    &END EACH
	  &END PDOS
	
	  &MO_CUBES
	    NHOMO 5
	    NLUMO 5
	    WRITE_CUBE F
	    ADD_LAST NUMERIC
	    
	    &EACH
	      MD 50
	      GEO_OPT 0
	    &END EACH
	  &END MO_CUBES
	
	  &V_HARTREE_CUBE ON
	    STRIDE 8 8 1
	    APPEND T
	
	    &EACH
	      MD 50
	      GEO_OPT 0
	    &END EACH
	  &END V_HARTREE_CUBE
	&END PRINT
	"""
	insert_section(strs, "PRINT", dft)
	
	force_eval.insert(dft)
	
	## subsys subsection
	subsys = Section("SUBSYS")
	
	### cell subsubsection
	cell = Cell(structure.lattice)
	subsys.insert(cell)

	### coord subsubsection
	coord = Section("COORD")
	add_keyword("@INCLUDE ./coord.xyz", coord)
	subsys.insert(coord)
	
	### kind subsubsection
	for atom in structure.species:
	    kind = Kind(atom, basis_set=None, potential=None)
	    subsys.insert(kind)
	
	force_eval.insert(subsys)
	
	
	return force_eval


parser = argparse.ArgumentParser(description='generate cp2k input file')
parser.add_argument('input_file_name', type=str, help='input file name')
parser.add_argument('--cell', nargs="+", help='set cell, a list of lattice, [x, y, z] or [x, y, z, a, b, c]')
parser.add_argument('--bp', type=str, nargs="?", default=None, help='a file contains all basis_set and potential information')
## function args of golbal
parser.add_argument('--run_type', type=str, nargs="?", default="ENEGRY", help='specie run_type keyword of global')
parser.add_argument('--project_name', type=str, nargs="?", default="cp2k", help='specie project_name keyword of global')
parser.add_argument('--print_level', type=str, nargs="?", default="MEDIUM", help='specie print_level keyword of global')
parser.add_argument('--walltime', type=int, nargs="?", default=107000, help='specie walltime keyword of global')
## function args of motion
parser.add_argument('--constraint_list', type=str, nargs="?", default=None, help='specie constranit_list keyword of motion')
parser.add_argument('--cell_opt', type=bool, nargs="?", default=False, help='specie cell_opt section of motion')
parser.add_argument('--geo_opt', type=bool, nargs="?", default=False, help='specie geo_opt section of motion')
## function args of force_eval
parser.add_argument('--method', type=str, nargs="?", default="QUICKSTEP", help='specie methon keyword of force_eval')
parser.add_argument('--charge', type=int, nargs="?", default=None, help='specie charge keyword of force_eval')
parser.add_argument('--ot', type=bool, nargs="?", default=False, help='specie scf type is ot(else is smear) of force_eval')
parser.add_argument('--hse', type=bool, nargs="?", default=False, help='specie xc type is hse(else is pbe) of force_eval')
args = parser.parse_args()



if args.input_file_name[-3:] == "xyz":
	with open(args.input_file_name, 'r') as f:
		data = f.readline().strip()
		if not isinstance(int(data), int):
			atom_number = sum(1 for line in f if line.strip)
	
			add_line = f"{int(atom_number+1)}\n\n"
			with open(args.input_file_name, 'r') as g:
				gile = g.readlines()
				gile.insert(0, add_line)
			with open(args.input_file_name, 'w') as g:
				g.writelines(gile)

if args.bp == None:
	bp_dict = {
		'Pt': ['DZVP-MOLOPT-SR-GTH', 'GTH-PBE-q18'], 
		'O': ['DZVP-MOLOPT-SR-GTH', 'GTH-PBE-q6'], 
		'C': ['DZVP-MOLOPT-SR-GTH', 'GTH-PBE-q4'],
		'Cs': ['DZVP-MOLOPT-SR-GTH', 'GTH-PBE-q9'],
		'Li': ['DZVP-MOLOPT-SR-GTH', 'GTH-PBE-q3'],
		'Ne': ['DZVP-MOLOPT-SR-GTH', 'GTH-PBE-q8'], 
		'Ru': ['DZVP-MOLOPT-SR-GTH', 'GTH-PBE-q16'], 
		'Ag': ['DZVP-MOLOPT-SR-GTH', 'GTH-PBE-q11'], 
		'Ir': ['DZVP-MOLOPT-SR-GTH', 'GTH-PBE-q17'], 
		'C': ['DZVP-MOLOPT-SR-GTH', 'GTH-PBE-q4'], 
		'H': ['DZVP-MOLOPT-SR-GTH', 'GTH-PBE-q1'], 
		'F': ['DZVP-MOLOPT-SR-GTH', 'GTH-PBE-q7'], 
		'Na': ['DZVP-MOLOPT-SR-GTH', 'GTH-PBE-q9'], 
		'K': ['DZVP-MOLOPT-SR-GTH', 'GTH-PBE-q9'], 
		'Cl': ['DZVP-MOLOPT-SR-GTH', 'GTH-PBE-q7']
	}
else:
	bp_dict = {}
	with open(args.bp, 'r') as f:
		for line in f:
			key, value1, value2 = line.strip().split()
			bp_dict[key] = [value1, value2]


if args.input_file_name[-3:] == "cif":
	atoms = read(args.input_file_name)
	atoms.write("POSCAR")
	structure = Structure.from_file("POSCAR")
	os.remove("POSCAR")

elif args.input_file_name[-3:] == "xyz":
	atoms = read(args.input_file_name, format="xyz")
	atoms.set_cell(args.cell)
	atoms.write("POSCAR", format="vasp")
	structure = Structure.from_file("POSCAR")
	os.remove("POSCAR")

Global = Global(
	run_type=args.run_type,
	project_name=args.project_name,
	print_level=args.print_level,
	walltime=args.walltime
)
motion = motion(
	constraint_list=args.constraint_list,
	cell_opt=args.cell_opt,
	geo_opt=args.geo_opt
)
force_eval = force_eval(
	structure,
	method=args.method,
	charge=args.charge,
	ot=args.ot,
	hse=args.hse
)

used_bp_dict = {}
for atom in structure.species:
	if str(atom) in bp_dict:
		used_bp_dict[str(atom)] = bp_dict[str(atom)]

for key, value in used_bp_dict.items():
	print(key, value)
	add_keyword(f"BASIS_SET {value[0]}", force_eval.by_path(f"SUBSYS/{key}"))
	add_keyword(f"POTENTIAL {value[1]}", force_eval.by_path(f"SUBSYS/{key}"))

if args.input_file_name[-3:] == "cif":
	atoms = read(args.input_file_name)
	atoms.write("temp.xyz")
	with open("temp.xyz", 'r') as f:
		coord = ''
		for i, line in enumerate(f):
			if i < 2:
				continue
			coord += f"  {' '.join(line.split()[0:4])}\n"
	
	with open("coord.xyz", 'w') as f:
		f.write(coord)
	os.remove("temp.xyz")

elif args.input_file_name[-3:] == "xyz":
	with open(args.input_file_name, 'r') as f:
		coord = ''
		for i, line in enumerate(f):
			if i < 2:
				continue
			coord += f"  {' '.join(line.split()[0:4])}\n"
	
	with open("coord.xyz", 'w') as f:
		f.write(coord)
		

inp = Cp2kInput.from_str(
	Global.get_str()+
	motion.get_str()+
	force_eval.get_str()
)
inp.write_file("input.inp")


# copy sub script
sub_script_path = "/public/home/jxxcr/script/sub_cp2k"
shutil.copy2(sub_script_path, ".")
